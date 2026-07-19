# Playbook de Refatoração — Padrões de Transformação

Usado na **Fase 3**. Cada padrão resolve um ou mais itens do `anti-patterns-catalog.md`. Os exemplos ilustram a transformação em Python e/ou JavaScript — aplique o princípio equivalente na linguagem real do projeto.

---

## 1. Extrair Configuração / Eliminar Segredo Hardcoded

Resolve: *Hardcoded Credentials*, *Endpoint Admin/Debug Sem Proteção* (parte do `debug=True`).

**Antes** (`app.py`):
```python
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
app.config["DEBUG"] = True
```

**Depois** (`config/settings.py`):
```python
import os

class Settings:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
    DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    DATABASE_PATH = os.environ.get("DATABASE_PATH", "loja.db")

settings = Settings()
```
`app.py`:
```python
from config.settings import settings
app.config["SECRET_KEY"] = settings.SECRET_KEY
app.config["DEBUG"] = settings.DEBUG
```
Crie também um `.env.example` documentando as variáveis esperadas (sem valores reais).

---

## 2. Split God Class por Domínio

Resolve: *God Class / God Module*.

**Antes** (`models.py` — um arquivo, 4 domínios):
```python
def get_todos_produtos(): ...
def criar_usuario(nome, email, senha): ...
def criar_pedido(usuario_id, itens): ...
```

**Depois** (um módulo por entidade):
```
models/
├── produto_model.py   # get_todos, get_por_id, criar, atualizar, deletar, buscar
├── usuario_model.py    # get_todos, get_por_id, criar, autenticar
└── pedido_model.py      # criar, get_por_usuario, get_todos, atualizar_status
```
```python
# models/produto_model.py
from database import get_db

def get_todos():
    db = get_db()
    rows = db.execute("SELECT * FROM produtos").fetchall()
    return [dict(row) for row in rows]
```
Cada arquivo só conhece sua própria tabela. Nenhum import cruzado de regra de negócio entre models (se `pedido_model` precisa de dado de produto, ele importa `produto_model`, não reimplementa a query).

---

## 3. Parametrizar Queries (eliminar SQL Injection)

Resolve: *SQL Injection*.

**Antes**:
```python
cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))
cursor.execute(
    "INSERT INTO usuarios (nome, email, senha) VALUES ('" + nome + "', '" + email + "', '" + senha + "')"
)
```

**Depois**:
```python
cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))
cursor.execute(
    "INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)",
    (nome, email, senha_hash)
)
```
Em Node.js/`sqlite3`:
```js
// Antes
db.run(`INSERT INTO users (email) VALUES ('${email}')`);
// Depois
db.run("INSERT INTO users (email) VALUES (?)", [email]);
```
Regra: **nenhum valor vindo de `request`/`req.body`/`req.params` pode tocar a string SQL diretamente** — sempre via placeholder + parâmetro.

---

## 4. Extrair Lógica de Negócio do Controller/Rota

Resolve: *Fat Controller / Lógica de Negócio na Rota*.

**Antes** (rota faz tudo, `AppManager.js`):
```js
app.post('/api/checkout', (req, res) => {
    // parse + valida cartão + processa pagamento + grava matrícula + grava pagamento + audit log, tudo inline
});
```

**Depois**:
```js
// controllers/checkoutController.js
async function checkout({ userName, email, password, courseId, card }) {
    const course = await courseModel.findActiveById(courseId);
    if (!course) throw new NotFoundError('Curso não encontrado');

    const user = await userModel.findOrCreateByEmail({ userName, email, password });
    const paymentResult = await paymentService.charge(card, course.price);
    if (!paymentResult.approved) throw new PaymentDeniedError();

    const enrollment = await enrollmentModel.create(user.id, course.id);
    await paymentModel.create(enrollment.id, course.price, paymentResult.status);
    await auditService.log(`Checkout curso ${course.id} por ${user.id}`);
    return { enrollmentId: enrollment.id };
}

// routes/checkoutRoutes.js
router.post('/api/checkout', async (req, res, next) => {
    try {
        const result = await checkoutController.checkout(mapBody(req.body));
        res.status(200).json({ msg: 'Sucesso', ...result });
    } catch (err) { next(err); }
});
```
A rota fica fina; o controller orquestra; models/services fazem persistência/pagamento.

---

## 5. Centralizar Tratamento de Erros e Logging

Resolve: *Exceção Genérica Engolindo Erros*, *Logging via print/console.log*.

**Antes** (repetido em toda função):
```python
try:
    ...
except Exception as e:
    print("ERRO: " + str(e))
    return jsonify({"erro": str(e)}), 500
```

**Depois**:
```python
# middlewares/error_handler.py
import logging
logger = logging.getLogger(__name__)

def register_error_handlers(app):
    @app.errorhandler(Exception)
    def handle_unexpected(e):
        logger.exception("Erro não tratado")
        return jsonify({"erro": "Erro interno"}), 500

    @app.errorhandler(ValidationError)
    def handle_validation(e):
        return jsonify({"erro": str(e)}), 400
```
Handlers de rota deixam de ter `try/except` genérico; erros esperados usam exceções de domínio (`ValidationError`, `NotFoundError`) capturadas centralizadamente.

Em Express, o equivalente é um middleware de 4 argumentos registrado por último: `app.use((err, req, res, next) => { logger.error(err); res.status(err.status || 500).json({ erro: err.message }); })`.

---

## 6. Eliminar Queries N+1

Resolve: *Queries N+1*.

**Antes**:
```python
for row in pedidos:
    cursor2.execute("SELECT * FROM itens_pedido WHERE pedido_id = " + str(row["id"]))
    for item in cursor2.fetchall():
        cursor3.execute("SELECT nome FROM produtos WHERE id = " + str(item["produto_id"]))
```

**Depois** (um único JOIN):
```python
cursor.execute("""
    SELECT p.id, p.status, p.total, ip.produto_id, ip.quantidade, ip.preco_unitario, pr.nome AS produto_nome
    FROM pedidos p
    JOIN itens_pedido ip ON ip.pedido_id = p.id
    JOIN produtos pr ON pr.id = ip.produto_id
    WHERE p.usuario_id = ?
""", (usuario_id,))
```
Com ORM (SQLAlchemy):
```python
# Antes: Task.query.filter_by(user_id=u.id) dentro de um for sobre users
# Depois: agregação única
from sqlalchemy import func
stats = db.session.query(Task.user_id, func.count(Task.id)).group_by(Task.user_id).all()
```

---

## 7. Hashing Seguro de Senha

Resolve: *Armazenamento Inseguro de Senha*.

**Antes**:
```python
self.password = hashlib.md5(pwd.encode()).hexdigest()
```
```js
function badCrypto(pwd) { /* base64 repetido 10000x */ }
```

**Depois**:
```python
from werkzeug.security import generate_password_hash, check_password_hash

def set_password(self, pwd):
    self.password = generate_password_hash(pwd)

def check_password(self, pwd):
    return check_password_hash(self.password, pwd)
```
Em Node.js: `bcrypt.hash(pwd, 10)` / `bcrypt.compare(pwd, hash)`.

---

## 8. Eliminar Duplicação Reaproveitando o Model

Resolve: *Fat Controller (duplicação)*, *Serialização duplicada*.

**Antes** (rota reimplementa `to_dict`):
```python
task_data = {}
task_data['id'] = t.id
task_data['title'] = t.title
# ...8 linhas repetidas em 3 rotas diferentes
```

**Depois**:
```python
task_data = t.to_dict()
task_data['overdue'] = t.is_overdue()
```
Regra geral: se uma lógica (serialização, cálculo de status) já existe como método do Model, a rota **chama** o método — nunca copia o corpo dele.

---

## 9. Encapsular Estado Global Mutável

Resolve: *Estado Global Mutável*.

**Antes**:
```js
let globalCache = {};
function logAndCache(key, data) { globalCache[key] = data; }
```

**Depois**:
```js
// services/cacheService.js
class CacheService {
    constructor() { this._store = new Map(); }
    set(key, value) { this._store.set(key, value); }
    get(key) { return this._store.get(key); }
}
module.exports = new CacheService(); // singleton explícito, injetado onde necessário
```
O ponto-chave não é "ter uma instância única" (isso pode ser aceitável para cache), mas **tornar o acesso explícito e testável** — o serviço pode ser substituído/mockado em teste, uma variável de módulo solta não pode.

---

## 10. Substituir Autenticação Falsa por JWT Real

Resolve: *Autenticação Falsa / Token Não Criptográfico*.

**Antes**:
```python
return jsonify({"token": "fake-jwt-token-" + str(user.id)})
```

**Depois**:
```python
import jwt, datetime
from config.settings import settings

def gerar_token(user):
    payload = {
        "sub": user.id,
        "role": user.role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=8)
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
```
Rotas protegidas passam a validar o token (`jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])`) em um middleware/decorator de autenticação, em vez de confiar cegamente em um id.

> Nota de escopo: implementar o *middleware de verificação* completo em todas as rotas pode estar fora do escopo de uma refatoração puramente estrutural — quando assim for, a Fase 3 aplica a geração de token real e documenta no relatório que a validação de token nas rotas protegidas é uma recomendação de follow-up de segurança.

---

## 11. Promisificar / Eliminar Callback Hell

Resolve: *Callback Hell*.

**Antes**:
```js
db.get(sql1, [id], (err, a) => {
    db.get(sql2, [a.id], (err, b) => {
        db.run(sql3, [b.id], (err) => { res.json(ok); });
    });
});
```

**Depois**:
```js
const { promisify } = require('util');
const dbGet = promisify(db.get.bind(db));
const dbRun = promisify(db.run.bind(db));

async function processar(id) {
    const a = await dbGet(sql1, [id]);
    const b = await dbGet(sql2, [a.id]);
    await dbRun(sql3, [b.id]);
}
```
Operações paralelas usam `Promise.all([...])` em vez de contadores manuais de "pending".

---

## 12. Centralizar Constantes e Validação

Resolve: *Magic Numbers/Strings*, *Validação Duplicada*.

**Antes**: listas `["pendente", "aprovado", ...]` repetidas em 3 arquivos.

**Depois**:
```python
# config/constants.py
VALID_ORDER_STATUSES = ["pendente", "aprovado", "enviado", "entregue", "cancelado"]
VALID_CATEGORIES = ["informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"]
```
```python
from config.constants import VALID_ORDER_STATUSES

def validar_status(status):
    return status in VALID_ORDER_STATUSES
```
Toda rota/model que precisa validar esse valor importa a mesma constante — uma única fonte de verdade.

---

## 13. Substituir API Deprecated

Resolve: *APIs Depreciadas/Obsoletas*.

**Antes**:
```python
criado_em = datetime.datetime.utcnow()
```

**Depois** (Python 3.12+):
```python
from datetime import datetime, UTC
criado_em = datetime.now(UTC)
```
Node.js:
```js
// Antes
const buf = new Buffer(data);
// Depois
const buf = Buffer.from(data);
```
Sempre confirme a versão do runtime/framework (`requirements.txt`/`package.json`) antes de aplicar — a troca só é necessária/segura na versão onde a API antiga é de fato deprecated.

---

## 14. Renomear para Nomes de Domínio

Resolve: *Nomenclatura Pobre*.

**Antes**:
```js
app.post('/api/checkout', (req, res) => {
    let u = req.body.usr, e = req.body.eml, p = req.body.pwd, cid = req.body.c_id, cc = req.body.card;
});
```

**Depois**:
```js
app.post('/api/checkout', (req, res) => {
    const { usr: userName, eml: email, pwd: password, c_id: courseId, card: cardNumber } = req.body;
});
```
Nomes devem comunicar o conceito de negócio, não abreviar por economia de digitação.

---

## Cobertura mínima (14 padrões, exigido ≥8)

Todos os 16 anti-patterns do catálogo têm um padrão de transformação correspondente acima (alguns padrões resolvem mais de um anti-pattern, como o #5 e o #12).
