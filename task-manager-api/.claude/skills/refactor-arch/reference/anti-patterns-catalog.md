# Catálogo de Anti-patterns

Usado na **Fase 2 (Auditoria)**. Para cada anti-pattern: o que é, **sinais de detecção concretos** (o que grepar/observar — não "código ruim", mas o padrão textual/estrutural exato), a severidade e o campo `Recommendation` que deve apontar para o playbook (`refactoring-playbook.md`).

Regra de ouro: **todo finding precisa citar arquivo e linha(s) reais**. Se você não consegue apontar a linha exata, não é um finding, é uma suspeita — investigue mais antes de reportar.

---

## CRITICAL

### 1. Hardcoded Credentials / Secrets

**O que é**: chaves, senhas, tokens ou segredos de API escritos diretamente no código-fonte.

**Sinais de detecção**:
- Atribuições literais a variáveis com nomes como `SECRET_KEY`, `PASSWORD`, `API_KEY`, `TOKEN`, `db_pass`, `paymentGatewayKey` seguidas de uma string literal (não uma leitura de `os.environ`/`process.env`).
- `grep -riE "(secret|password|api[_-]?key|token|pass)\s*[:=]\s*['\"]"` sobre o código-fonte (excluindo testes/exemplos).
- O segredo sendo devolvido em uma resposta HTTP (agrava para "exposição ativa", não só "hardcoded").

**Playbook**: → `playbook-1-extract-config.md` (ver `refactoring-playbook.md #1`).

---

### 2. SQL Injection

**O que é**: construção de queries SQL por concatenação/interpolação de strings com dados de entrada do usuário, em vez de queries parametrizadas.

**Sinais de detecção**:
- `"SELECT ... " + variavel`, `f"...{variavel}..."` ou template strings (`` `...${var}...` ``) formando um comando SQL.
- Ausência de `?`/`%s`/placeholders nomeados junto de uma tupla/lista de parâmetros separada no `execute()`.
- Endpoint que aceita e executa SQL arbitrário vindo do corpo da requisição (forma extrema: "SQL Injection por design").

**Playbook**: → `refactoring-playbook.md #3` (Parametrização de Queries).

---

### 3. God Class / God Module (violação total de separação de responsabilidades)

**O que é**: um único arquivo/classe concentra acesso a dados (SQL), regra de negócio para múltiplos domínios e, às vezes, roteamento — o oposto do MVC.

**Sinais de detecção**:
- Um arquivo com >150-200 linhas que mistura: `execute()`/query direta **e** validação de regra de negócio **e** formatação de resposta HTTP, para **mais de um domínio/entidade** (ex.: produtos + usuários + pedidos no mesmo arquivo).
- Uma classe cujo construtor abre conexão de banco **e** cujos métodos definem rotas (`app.post(...)` dentro de um método de classe) **e** implementam regra de negócio de pagamento/checkout.
- Teste mental: "para testar só a regra X, preciso subir servidor HTTP e banco real?" — se sim, é God Class.

**Playbook**: → `refactoring-playbook.md #2` (Split God Class por domínio).

---

### 4. Endpoint Administrativo / Debug Sem Proteção

**O que é**: rotas que expõem controle total do sistema (executar SQL arbitrário, resetar banco, ligar modo debug) sem autenticação/autorização.

**Sinais de detecção**:
- Rota que recebe uma string e a executa diretamente contra o banco/SO (`cursor.execute(body.sql)`, `eval(...)`, `exec(...)`, `child_process.exec(req.body...)`).
- Rota de reset/delete em massa (`DELETE FROM ...` sem `WHERE`) acessível sem checagem de autenticação/role.
- `debug=True` / `app.config["DEBUG"] = True` em uma aplicação que sobe com `host="0.0.0.0"`.

**Playbook**: → `refactoring-playbook.md #1` e `#4` (config por ambiente + middleware de autenticação/erro).

---

### 5. Armazenamento Inseguro de Senha

**O que é**: senha gravada em texto puro, ou "hash" com algoritmo criptograficamente quebrado/inadequado (MD5, SHA1 sem salt) ou inventado (ex.: encode Base64 repetido).

**Sinais de detecção**:
- Comparação direta de senha em SQL (`WHERE senha = '<valor>'`) ou em Python/JS (`if user.password == pwd`) sem nenhuma função de hash entre a gravação e a leitura.
- Uso de `hashlib.md5`/`hashlib.sha1` para senha.
- Função de "criptografia" caseira (loop manual, `base64` repetido, XOR simples) no lugar de uma lib de hashing de senha (bcrypt/argon2/scrypt/`werkzeug.security`).

**Playbook**: → `refactoring-playbook.md #7` (Hashing seguro de senha).

---

## HIGH

### 6. Lógica de Negócio no Controller/Rota (Fat Controller)

**O que é**: a camada HTTP (controller/rota) contém regras de negócio, cálculos, orquestração de múltiplos passos ou efeitos colaterais (envio de notificação, cálculo de desconto) em vez de delegar a uma camada de serviço/model.

**Sinais de detecção**:
- Função handler de rota com >30-40 linhas contendo `if`/cálculo de negócio (descontos, totais, elegibilidade) em vez de só: parsear entrada → chamar controller/service → formatar saída.
- `print`/`console.log` de "envio de e-mail/SMS/notificação" dentro do handler HTTP, simulando um efeito colateral de domínio.
- Mesma regra de negócio (ex.: cálculo de "atrasado") reimplementada de forma idêntica em 2+ rotas em vez de chamar um único método do Model.

**Playbook**: → `refactoring-playbook.md #4` (Extrair Controller/Service) e `#8` (Eliminar duplicação reaproveitando o Model).

---

### 7. Estado Global Mutável

**O que é**: variáveis de módulo/globais mutáveis compartilhadas entre requisições concorrentes, usadas como cache, contador ou store de sessão.

**Sinais de detecção**:
- Declaração de objeto/dict/contador no escopo de módulo (fora de qualquer função/classe) que é lido e escrito por múltiplos handlers (`let globalCache = {}`, `db_connection = None` com `global` reatribuído em função).
- Nenhum mecanismo de isolamento por requisição (sem request-scoped context, sem injeção).

**Playbook**: → `refactoring-playbook.md #9` (Encapsular estado em módulo/classe com escopo controlado, ex.: connection pool ou singleton explícito de config).

---

### 8. Autenticação Falsa / Token Não Criptográfico

**O que é**: um mecanismo que parece autenticação (retorna algo chamado "token") mas não tem nenhuma propriedade criptográfica — é forjável.

**Sinais de detecção**:
- Token construído por concatenação de string previsível (`'fake-jwt-token-' + user.id`, `'token_' + email`).
- Ausência de biblioteca de JWT/assinatura (`pyjwt`, `jsonwebtoken`) apesar do nome "jwt" aparecer no código.
- Nenhuma verificação de expiração/assinatura em rotas subsequentes que deveriam exigir autenticação.

**Playbook**: → `refactoring-playbook.md #10` (JWT real assinado).

---

### 9. Callback Hell / Nesting Profundo Sem Tratamento de Erro

**O que é**: cadeias de callbacks aninhados (3+ níveis) coordenando controle de fluxo assíncrono manualmente, geralmente sem tratamento de erro consistente em cada nível.

**Sinais de detecção**:
- 3 ou mais callbacks aninhados no mesmo bloco de código (`db.get(..., (err, x) => { db.get(..., (err, y) => { db.run(..., (err) => {...}) }) })`).
- Contadores manuais (`pending--`, `if (pending === 0)`) para saber quando operações assíncronas paralelas terminaram, em vez de `Promise.all`/`async-await`.
- Nem todo callback trata `err` (alguns ignoram o primeiro parâmetro).

**Playbook**: → `refactoring-playbook.md #11` (Promisificar / async-await).

---

## MEDIUM

### 10. Queries N+1

**O que é**: uma query para buscar uma lista, seguida de uma query adicional por item da lista (ou por item relacionado), em vez de um `JOIN`/eager load.

**Sinais de detecção**:
- `for` sobre o resultado de uma query, executando uma nova query dentro do laço (`for row in rows: cursor.execute(...)`).
- Callback `.forEach()` sobre resultado de `db.all()` que dispara outro `db.get()`/`db.all()` por iteração.
- Loop em Python sobre `Model.query.all()` chamando `Model.query.filter_by()` outra vez por item, quando uma agregação (`GROUP BY`/`func.count`) resolveria em uma query.

**Playbook**: → `refactoring-playbook.md #6` (Eliminar N+1 com JOIN/eager loading/agregação).

---

### 11. Validação Duplicada / Ausente na Fronteira

**O que é**: cada rota reimplementa manualmente a mesma validação de campo (tipo, obrigatoriedade, range) em vez de usar uma função/schema compartilhado — ou não valida em algumas rotas onde valida em outras.

**Sinais de detecção**:
- O mesmo bloco de `if campo not in dados: return erro` repetido quase identicamente em duas ou mais funções (create/update do mesmo recurso).
- Um módulo de constantes/validação existe no projeto (`utils/helpers.py` com `VALID_STATUSES` etc.) mas as rotas usam listas literais próprias em vez de importá-lo.

**Playbook**: → `refactoring-playbook.md #12` (Centralizar validação).

---

### 12. Exceção Genérica Engolindo Erros

**O que é**: blocos `try/except`/`catch` que capturam qualquer erro e retornam sempre a mesma mensagem genérica, sem logar a causa raiz nem diferenciar tipos de falha.

**Sinais de detecção**:
- `except:` sem tipo (Python) ou `catch (e) {}` vazio/genérico (JS) sem `console.error`/`logging.exception`.
- Mensagem de erro sempre idêntica ("Erro interno") independente da exceção real, dificultando debug em produção.

**Playbook**: → `refactoring-playbook.md #5` (Error handling centralizado).

---

### 13. APIs Depreciadas / Obsoletas

**O que é**: uso de funções, métodos ou padrões marcados como deprecated pela própria linguagem/framework/runtime, com substituto moderno disponível.

**Sinais de detecção — verifique a versão real do runtime/framework antes de reportar (a depreciação depende da versão):**

| Linguagem/Framework | API deprecated | Substituto |
|---|---|---|
| Python 3.12+ | `datetime.datetime.utcnow()` / `utcfromtimestamp()` | `datetime.datetime.now(datetime.UTC)` |
| Python | `imp` module | `importlib` |
| Flask | rodar com `app.run(debug=True)` como servidor de produção | servidor WSGI (gunicorn/uwsgi) + `FLASK_DEBUG` controlado por env |
| Node.js | `new Buffer(...)` | `Buffer.from(...)` / `Buffer.alloc(...)` |
| Node.js `sqlite3` (callback API) | callbacks aninhados manuais para controle de fluxo | `util.promisify` ou driver com Promises nativas (`sqlite`, `better-sqlite3`) |
| Express 4 body parsing | middleware `body-parser` externo | `express.json()`/`express.urlencoded()` nativos (já builtin desde Express 4.16) |
| SQLAlchemy 1.x style | `Model.query.get(id)` (legacy query API, deprecated desde SQLAlchemy 2.0) | `db.session.get(Model, id)` |

**Como aplicar**: grepe o código por essas assinaturas e confira a versão do runtime/framework no manifest de dependências antes de marcar como finding — reportar uma API como deprecated numa versão onde ela não é seria um falso positivo.

**Playbook**: → `refactoring-playbook.md #13` (Substituir API deprecated).

---

## LOW

### 14. Magic Numbers / Magic Strings

**O que é**: valores literais (números ou strings) com significado de negócio espalhados pelo código, sem nome, em vez de constantes nomeadas.

**Sinais de detecção**: listas de valores válidos (status, categorias, roles) ou limiares numéricos (`if faturamento > 10000`) escritos inline e repetidos em mais de um lugar.

**Playbook**: → `refactoring-playbook.md #12` (mesmo padrão de centralização de constantes).

---

### 15. Nomenclatura Pobre

**O que é**: identificadores de uma letra ou não descritivos para variáveis que representam conceitos de negócio (`u`, `e`, `p`, `cc`, `cid`).

**Sinais de detecção**: parâmetros de função de 1-2 caracteres representando entidades de domínio (usuário, email, senha, cartão) em vez de HTTP genérico (`i` em loop simples é aceitável, `u` para "usuário" não é).

**Playbook**: → `refactoring-playbook.md #14` (Renomear para nomes de domínio).

---

### 16. Logging via `print`/`console.log`

**O que é**: uso de saída padrão para logging de aplicação em vez de um módulo de logging configurável (níveis, formato, destino).

**Sinais de detecção**: `print(...)`/`console.log(...)` usados para mensagens de erro, auditoria ou diagnóstico (não para output esperado de CLI).

**Playbook**: → `refactoring-playbook.md #5` (parte do error handling centralizado, que inclui logging estruturado).

---

## Resumo de severidades (mínimo 8 exigido pelo desafio — catálogo tem 16)

| Severidade | Quantidade no catálogo |
|---|---|
| CRITICAL | 5 |
| HIGH | 4 |
| MEDIUM | 4 |
| LOW | 3 |

Ao auditar um projeto, **nem todo anti-pattern do catálogo vai aparecer** — reporte apenas os que têm evidência real no código, sempre com arquivo:linha.
