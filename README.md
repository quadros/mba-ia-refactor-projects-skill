# Desafio: Skill de Auditoria e Refatoração Arquitetural

Este repositório contém a resolução do desafio `refactor-arch`: uma Skill de Claude Code capaz de analisar, auditar e refatorar para o padrão MVC qualquer codebase, independente de linguagem ou framework. A skill foi construída e validada em três projetos legados fornecidos como boilerplate: `code-smells-project` (Python/Flask), `ecommerce-api-legacy` (Node.js/Express) e `task-manager-api` (Python/Flask parcialmente organizado).

> Ver `SPEC_1.md` para o enunciado original do desafio.

## Sumário

- [A) Análise Manual](#a-análise-manual)
- [B) Construção da Skill](#b-construção-da-skill)
- [C) Resultados](#c-resultados)
- [D) Como Executar](#d-como-executar)

---

## A) Análise Manual

Antes de construir a skill, os três projetos foram lidos manualmente, arquivo por arquivo, para entender os problemas reais que a skill precisaria detectar. Os achados abaixo (mínimo 5 por projeto, com pelo menos 1 CRITICAL/HIGH, 2 MEDIUM e 2 LOW) foram a base do catálogo de anti-patterns da skill.

### Projeto 1 — `code-smells-project` (Python/Flask, API de E-commerce)

| # | Severidade | Problema | Local | Justificativa |
|---|---|---|---|---|
| 1 | **CRITICAL** | SQL Injection generalizado | `models.py` (praticamente todas as funções, ex.: linhas 28, 48-50, 92, 109-111, 127-129, 140, 149-151, 155-166, 174, 188, 192, 220, 224, 279-280, 291-297) | Toda query é montada por concatenação de string com dados vindos direto da requisição (`"SELECT * FROM produtos WHERE id = " + str(id)`, login por `email`/`senha` concatenados). Um único payload malicioso compromete leitura, escrita e autenticação do banco inteiro. |
| 2 | **CRITICAL** | Endpoint que executa SQL arbitrário sem autenticação | `app.py:59-78` (`/admin/query`) | Recebe uma string `sql` do corpo da requisição e executa diretamente com `cursor.execute(query)`, sem autenticação, sem allowlist, sem sandboxing. É equivalente a um shell SQL exposto publicamente — pode dropar tabelas, exfiltrar dados ou ler o schema inteiro. |
| 3 | **CRITICAL** | Credenciais e segredos hardcoded + expostos | `app.py:7-8` (`SECRET_KEY`), `controllers.py:289` (`health_check` retorna `secret_key` e `debug` no JSON) | A chave de sessão Flask está fixa no código-fonte e, pior, é devolvida em texto puro pelo endpoint público `/health`. Qualquer cliente pode ler a `SECRET_KEY` da aplicação. |
| 4 | **CRITICAL** | God File / God Module | `models.py` (315 linhas) e `controllers.py` (293 linhas) | Um único arquivo `models.py` concentra acesso a dados, regra de negócio e SQL cru para 4 domínios diferentes (produtos, usuários, pedidos, itens de pedido); `controllers.py` mistura parsing de request, validação, orquestração e logging para todos os domínios. Não há nenhuma separação de responsabilidades — mudar uma entidade arrisca quebrar as outras três. |
| 5 | **HIGH** | Senhas armazenadas em texto puro | `models.py:105-131` (`login_usuario`, `criar_usuario`) | Não há hashing de senha em nenhum momento — a senha é gravada e comparada como string simples (`senha = '" + senha + "'"`). Qualquer vazamento do banco expõe as senhas de todos os usuários diretamente. |
| 6 | **HIGH** | `debug=True` habilitado | `app.py:8`, `app.py:88` | O modo debug do Flask/Werkzeug fica ativo, o que expõe um console interativo de Python acessível via navegador em caso de erro não tratado — permite execução remota de código. |
| 7 | **MEDIUM** | Queries N+1 | `models.py:171-233` (`get_pedidos_usuario`, `get_todos_pedidos`) | Para cada pedido é aberto um novo cursor para buscar seus itens, e para cada item um outro cursor para buscar o nome do produto — 3 níveis de query aninhada em vez de um `JOIN`. Com poucos pedidos já gera dezenas de round-trips ao banco. |
| 8 | **MEDIUM** | Duplicação de código (DRY) | `models.py` — o dicionário de mapeamento de `produto` é reconstruído de forma idêntica em `get_todos_produtos`, `get_produto_por_id` e `buscar_produtos`; a validação de produto é duplicada quase integralmente entre `criar_produto` e `atualizar_produto` em `controllers.py` | Qualquer mudança de schema (novo campo, renomear coluna) precisa ser replicada manualmente em múltiplos lugares, com alto risco de inconsistência. |
| 9 | **LOW** | Logging via `print()` | `controllers.py` (linhas 8, 11, 57, 61, 106, 161, 179, 182, 208-210, 219, 248, 250) | Não há módulo de logging estruturado — mensagens de erro e auditoria (inclusive "envio" de e-mail/SMS/push simulado) vão para stdout sem nível, timestamp ou destino configurável. |
| 10 | **LOW** | Magic strings/listas soltas no código | `controllers.py:52` (`categorias_validas`), `controllers.py:242` (lista de status de pedido) | Listas de valores válidos (categorias, status) são recriadas inline dentro das funções de controller em vez de viverem em um único módulo de constantes, tornando fácil ficarem dessincronizadas entre criar/atualizar. |

### Projeto 2 — `ecommerce-api-legacy` (Node.js/Express, LMS com checkout)

| # | Severidade | Problema | Local | Justificativa |
|---|---|---|---|---|
| 1 | **CRITICAL** | God Class `AppManager` | `src/AppManager.js` (arquivo inteiro, 142 linhas) | Uma única classe é responsável por conexão com banco, criação de schema, seed de dados, definição de todas as rotas HTTP e toda a lógica de negócio de checkout/pagamento — o equivalente Node do "God Class" descrito no enunciado do desafio. |
| 2 | **CRITICAL** | Segredos e credenciais hardcoded | `src/utils.js:1-7` (`dbPass`, `paymentGatewayKey`, `smtpUser`) | Chave de gateway de pagamento (`pk_live_...`), senha de banco e usuário SMTP de produção estão fixos no código-fonte versionado — qualquer pessoa com acesso ao repositório tem acesso às credenciais de produção. |
| 3 | **CRITICAL** | "Criptografia" de senha inventada e reversível | `src/utils.js:17-23` (`badCrypto`) | Em vez de um hash criptográfico (bcrypt/argon2/scrypt), a função apenas repete um `base64` truncado 10.000 vezes e corta os 10 primeiros caracteres — não é um hash de via única, é trivialmente reversível/colidível, e ainda loga a senha em claro no console antes de "criptografar" (`console.log` na linha 45 do checkout). |
| 4 | **HIGH** | Callback hell sem tratamento de erro consistente | `src/AppManager.js:80-129` (`/api/admin/financial-report`) | Cadeia de callbacks aninhados (`db.all` → `forEach` → `db.all` → `forEach` → `db.get` → `db.get`) sem `try/catch`, sem `Promise`/`async-await`, com contadores manuais (`coursesPending`, `enrPending`) para saber quando a resposta terminou — extremamente frágil e difícil de testar. |
| 5 | **HIGH** | Estado global mutável | `src/utils.js:9-10` (`globalCache`, `totalRevenue`) | Um objeto de cache e um contador de receita vivem como variáveis de módulo mutáveis, compartilhadas entre todas as requisições concorrentes — sem isolamento, corrida de dados garantida sob carga. |
| 6 | **MEDIUM** | Queries N+1 em cascata | `src/AppManager.js:80-129` | Para cada curso busca as matrículas, para cada matrícula busca o usuário e o pagamento — O(cursos × matrículas) round-trips ao banco em vez de um `JOIN` único. |
| 7 | **MEDIUM** | Validação de pagamento inexistente | `src/AppManager.js:29-48` | O número do cartão só é "validado" verificando se começa com `"4"` (`cc.startsWith("4")`); não há validação de formato, Luhn check, nem de nenhum outro campo (e-mail, senha) além de truthy check. |
| 8 | **LOW** | Corrupção de dados sabida e ignorada | `src/AppManager.js:131-137` (`DELETE /api/users/:id`) | O próprio código reconhece, no texto de resposta, que apaga o usuário mas deixa matrículas e pagamentos "sujos" no banco (`"...ficaram sujos no banco"`) — ausência de cascade/soft-delete tratada como aceitável. |
| 9 | **LOW** | Nomenclatura de variáveis ilegível | `src/AppManager.js:29-33` (`u`, `e`, `p`, `cid`, `cc`) | Nomes de uma letra para usuário, e-mail, senha, id do curso e cartão de crédito dificultam a leitura e aumentam a chance de troca acidental de parâmetros. |

### Projeto 3 — `task-manager-api` (Python/Flask, parcialmente organizado)

| # | Severidade | Problema | Local | Justificativa |
|---|---|---|---|---|
| 1 | **CRITICAL** | Hashing de senha com MD5 | `models/user.py:27-32` (`set_password`, `check_password`) | MD5 é criptograficamente quebrado e extremamente rápido de forçar por brute-force/rainbow table, sem salt. Apesar do projeto já ter uma pasta `models/`, a implementação de segurança dentro dela é insegura. |
| 2 | **CRITICAL** | Autenticação falsa (token forjável) | `routes/user_routes.py:207-211` (`login`) | O "token" retornado é literalmente a string `'fake-jwt-token-' + str(user.id)` — não há assinatura, expiração ou verificação real. Qualquer cliente pode forjar acesso como qualquer usuário apenas conhecendo seu `id`. |
| 3 | **HIGH** | Lógica de negócio duplicada fora do Model | `routes/task_routes.py:30-39`, `routes/user_routes.py:171-180` | O cálculo de "task atrasada" (`overdue`) já existe corretamente encapsulado em `Task.is_overdue()` (`models/task.py:50-60`), mas é reimplementado inline, com o mesmo if/else aninhado, em pelo menos 3 lugares diferentes nas rotas — a camada de rota está fazendo trabalho de Model. |
| 4 | **MEDIUM** | Queries N+1 em relatórios | `routes/report_routes.py:53-68` (`summary_report`) | Para calcular produtividade por usuário, itera sobre todos os usuários e, para cada um, dispara uma nova query `Task.query.filter_by(user_id=u.id)` em vez de uma agregação SQL (`GROUP BY`) — desempenho degrada linearmente com a base de usuários. |
| 5 | **MEDIUM** | Segredos hardcoded | `app.py:13` (`SECRET_KEY`), `services/notification_service.py:9-10` (usuário/senha SMTP do Gmail em texto puro) | Mesmo em um projeto com alguma organização de camadas, credenciais de e-mail de produção e a chave de sessão Flask continuam fixas no código-fonte. |
| 6 | **MEDIUM** | `except` genérico engolindo erros | `routes/task_routes.py:62` (`except:`), `routes/user_routes.py:130-132` (`except:`) | Cláusulas `except:` sem tipo capturam qualquer exceção (incluindo `KeyboardInterrupt`/bugs de programação) e retornam sempre a mesma mensagem genérica, escondendo a causa raiz e dificultando debug em produção. |
| 7 | **LOW** | Serialização duplicada em vez de reuso do Model | `routes/task_routes.py:17-28` | A rota reconstrói manualmente, campo a campo, o mesmo dicionário que `Task.to_dict()` (`models/task.py:23-36`) já produz, em vez de chamar o método existente — duplicação que só existe porque a camada de rota não confia na camada de Model. |
| 8 | **LOW** | Constantes definidas mas não usadas | `utils/helpers.py:110-116` (`VALID_STATUSES`, `VALID_ROLES`, `MIN_PASSWORD_LENGTH`, etc.) vs. listas literais repetidas em `models/task.py:39`, `routes/task_routes.py:110`, `routes/user_routes.py:71` | O projeto já criou um módulo de constantes central, mas as rotas e models ignoram-no e repetem as mesmas listas/valores literalmente — a abstração existe mas não é adotada, o que é pior do que não existir (duas fontes de verdade). |

---

## B) Construção da Skill

A skill vive em `code-smells-project/.claude/skills/refactor-arch/` e foi copiada, sem alterações, para os outros dois projetos — essa cópia literal (nenhum path ou nome hardcoded do projeto 1 dentro dos arquivos da skill) foi o critério prático usado para validar o requisito "agnóstica de tecnologia".

### Estrutura

```
refactor-arch/
├── SKILL.md                              # o "prompt" — orquestra as 3 fases, referencia os arquivos abaixo
└── reference/
    ├── project-analysis.md               # heurísticas de detecção (linguagem, framework, DB, domínio, arquitetura)
    ├── anti-patterns-catalog.md          # 16 anti-patterns, severidade CRITICAL→LOW, inclui detecção de API deprecated
    ├── report-template.md                 # formato obrigatório do relatório da Fase 2
    ├── architecture-guidelines.md        # regras do MVC alvo (Models/Views-Routes/Controllers/Config/Middlewares)
    └── refactoring-playbook.md           # 14 padrões de transformação com código antes/depois
```

### Decisões de design

- **`SKILL.md` como orquestrador, não como enciclopédia**: ele contém apenas o fluxo das 3 fases e as regras não-negociáveis (pausa obrigatória na Fase 2, validação obrigatória na Fase 3). Todo o conhecimento de domínio (o que é um anti-pattern, como classificar severidade, como transformar código) fica nos arquivos de `reference/`, carregados no início da execução — separação que espelha o próprio princípio MVC que a skill aplica ao código-alvo.
- **Sinais de detecção acionáveis, não adjetivos**: seguindo a dica do enunciado, cada entrada do catálogo tem uma seção "Sinais de detecção" com padrões textuais/estruturais concretos (ex.: `"SELECT ... " + variavel`, `except:` sem tipo, callback aninhado 3+ níveis) em vez de descrições vagas como "código ruim".
- **Regra de decisão explícita para a Fase 3**: `architecture-guidelines.md` termina com uma regra de decisão de uma frase ("essa linha decide sobre HTTP, sobre negócio, ou sobre persistência?") para que a skill saiba mover código para a camada certa mesmo em casos não cobertos literalmente pelos exemplos.
- **Adaptação a projetos parcialmente organizados é uma regra explícita, não uma exceção improvisada**: `architecture-guidelines.md` instrui a não recriar estrutura já correta — isso foi decisivo no projeto 3, onde a skill preservou `models/`/`routes/`/`services/`/`utils/` existentes e só adicionou `config/`, `controllers/` e `middlewares/` (as camadas que realmente faltavam para eliminar findings).

### Anti-patterns incluídos e por quê

O catálogo tem 16 entradas (mínimo exigido: 8) distribuídas em 5 CRITICAL, 4 HIGH, 4 MEDIUM, 3 LOW — o conjunto foi montado diretamente a partir da análise manual dos 3 projetos (seção A), garantindo que cada anti-pattern tivesse pelo menos uma ocorrência real observada, não uma entrada teórica. A entrada #13 (**APIs Depreciadas**) documenta uma tabela de sinais por linguagem/framework (`datetime.utcnow()`, `new Buffer()`, `Model.query.get()` legado do SQLAlchemy 2.0, etc.) e foi validada na prática no projeto 3, que de fato usava `datetime.utcnow()` extensivamente.

### Como a skill garante agnosticismo de tecnologia

1. As heurísticas de `project-analysis.md` são baseadas em artefatos universais de qualquer projeto de backend (manifesto de dependências, imports do entry point, padrões de schema SQL no código) — nunca em um caminho de arquivo específico.
2. Todo anti-pattern do catálogo é descrito por um **padrão estrutural** (concatenação de string formando SQL, callback aninhado, literal de segredo) que existe em qualquer linguagem imperativa, com exemplos ilustrados tanto em Python quanto em JavaScript no playbook.
3. Teste real nos 3 projetos: a mesma cópia da skill (zero edição) processou Python/Flask monolítico (projeto 1), Node.js/Express com callbacks (projeto 2) e Python/Flask parcialmente organizado (projeto 3) — três combinações de linguagem × nível de organização.

### Desafios encontrados

- **Achar o nível certo de prescrição no playbook**: exemplos genéricos demais não seriam acionáveis; exemplos copiados literalmente do projeto 1 tornariam a skill acoplada a ele. A solução foi mostrar o *princípio* de cada transformação com um exemplo mínimo e reutilizável (ex.: "extrair segredo para env var" com um settings.py genérico) em vez de mostrar a solução final completa de um projeto específico.
- **Projeto 3 exigiu uma decisão de escopo diferente dos outros dois**: como ele já tinha camadas, aplicar cegamente "criar estrutura MVC do zero" teria sido destrutivo e desnecessário. Resolvido adicionando a regra de decisão explícita em `architecture-guidelines.md` (ver acima) em vez de tratar isso como um caso especial hardcoded na Fase 3 do `SKILL.md`.
- **Autenticação falsa (`fake-jwt-token`) e "criptografia" caseira (`badCrypto`)**: substituí-las por soluções reais (JWT assinado, `werkzeug.security`/`scrypt`) sem adicionar dependências pesadas — no Node.js optei pelo módulo nativo `crypto` (scrypt) em vez de instalar `bcrypt` (que exige compilação nativa), evitando fragilidade de build sem abrir mão de segurança real.
- **Preservar contrato de API enquanto remove vulnerabilidade**: `/admin/query` e `/admin/reset-db` no projeto 1 eram, eles mesmos, a vulnerabilidade CRITICAL — mantê-los "funcionando" não fazia sentido. O `SKILL.md` documenta essa exceção explicitamente (remover/proteger endpoints que são a própria vulnerabilidade) para a Fase 3 não ficar paralisada tentando preservar comportamento inseguro.

## C) Resultados

### Resumo dos relatórios de auditoria (Fase 2)

| Projeto | Stack | CRITICAL | HIGH | MEDIUM | LOW | Total |
|---|---|---|---|---|---|---|
| 1 — code-smells-project | Python/Flask | 6 | 3 | 3 | 3 | **15** |
| 2 — ecommerce-api-legacy | Node.js/Express | 3 | 2 | 2 | 3 | **10** |
| 3 — task-manager-api | Python/Flask (parcial) | 2 | 2 | 3 | 3 | **10** |

Relatórios completos: [`reports/audit-project-1.md`](reports/audit-project-1.md), [`reports/audit-project-2.md`](reports/audit-project-2.md), [`reports/audit-project-3.md`](reports/audit-project-3.md).

### Comparação antes/depois

**Projeto 1** — de 4 arquivos monolíticos (`app.py`, `controllers.py`, `models.py`, `database.py`, todos na raiz) para `src/{config,models,controllers,views,services,middlewares}/`, um arquivo por domínio. `/admin/query` e `/admin/reset-db` (SQL Injection/execução arbitrária sem auth) foram removidos; todas as queries parametrizadas; senha com hash.

**Projeto 2** — de uma única `AppManager.js` (God Class com DB + rotas + regra de negócio + callback hell) para `src/{config,db,models,controllers,routes,services,middlewares}/`. `badCrypto` substituído por `scrypt`; callbacks aninhados substituídos por `async/await`; `DELETE /api/users/:id` agora limpa matrículas/pagamentos relacionados em vez de deixá-los órfãos.

**Projeto 3** — estrutura pré-existente (`models/`, `routes/`, `services/`, `utils/`) preservada; adicionados apenas `config/`, `controllers/` e `middlewares/`. MD5 substituído por hash seguro; token falso substituído por JWT real; lógica de "atrasado"/serialização duplicada em 3+ rotas consolidada em `Task.to_dict()`/`is_overdue()`; N+1 do relatório de produtividade substituído por uma query agregada.

### Checklist de validação (preenchido para os 3 projetos)

| Item | Projeto 1 | Projeto 2 | Projeto 3 |
|---|---|---|---|
| **Fase 1** — Linguagem detectada corretamente | ✅ Python | ✅ JavaScript (Node.js) | ✅ Python |
| Framework detectado corretamente | ✅ Flask 3.1.1 | ✅ Express ^4.18.2 | ✅ Flask 3.0.0 |
| Domínio descrito corretamente | ✅ E-commerce (produtos/pedidos/usuários) | ✅ LMS com checkout (cursos/matrículas/pagamentos) | ✅ Task Manager (tasks/usuários/categorias) |
| Nº de arquivos condiz com a realidade | ✅ 4 arquivos, ~780 linhas | ✅ 3 arquivos, ~180 linhas | ✅ 15 arquivos, ~1158 linhas |
| **Fase 2** — Segue o template definido | ✅ | ✅ | ✅ |
| Cada finding tem arquivo e linhas exatos | ✅ | ✅ | ✅ |
| Findings ordenados CRITICAL → LOW | ✅ | ✅ | ✅ |
| Mínimo de 5 findings | ✅ 15 | ✅ 10 | ✅ 10 |
| Detecção de API deprecated incluída | ➖ (nenhuma API deprecated real encontrada no runtime usado) | ➖ (nenhuma API deprecated real encontrada) | ✅ `datetime.utcnow()` |
| Pausa e pede confirmação antes da Fase 3 | ✅ | ✅ | ✅ |
| **Fase 3** — Estrutura segue MVC | ✅ | ✅ | ✅ |
| Config extraída (sem hardcoded) | ✅ | ✅ | ✅ |
| Models abstraem dados | ✅ | ✅ | ✅ |
| Views/Routes separadas | ✅ | ✅ | ✅ |
| Controllers concentram o fluxo | ✅ | ✅ | ✅ |
| Error handling centralizado | ✅ | ✅ | ✅ |
| Entry point claro | ✅ `src/app.py` | ✅ `src/app.js` | ✅ `app.py` |
| Aplicação inicia sem erros | ✅ | ✅ | ✅ |
| Endpoints originais respondem corretamente | ✅ | ✅ | ✅ |

> Nota sobre "detecção de API deprecated": o catálogo cobre essa categoria (`anti-patterns-catalog.md #13`) e ela foi testada com sucesso no projeto 3. Nos projetos 1 e 2, as versões de runtime/dependências usadas não continham nenhuma API já deprecated — reportar uma como tal ali teria sido um falso positivo, o que o `SKILL.md` instrui explicitamente a evitar.

### Logs de validação (Fase 3, todos os projetos)

Cada projeto foi validado subindo a aplicação real (`python src/app.py` / `node src/app.js` / `python app.py`) em um ambiente limpo e testando os endpoints originais via `curl`. Trechos representativos:

```
# Projeto 1
$ python src/app.py
==================================================
SERVIDOR INICIADO
Rodando em http://localhost:5000
==================================================
$ curl -s http://localhost:5000/produtos/busca?q=Mouse
{"dados":[{...,"nome":"Mouse Wireless","preco":89.9,...}],"sucesso":true,"total":1}
$ curl -s -X POST http://localhost:5000/admin/query   # endpoint removido
-> 404

# Projeto 2
$ node src/app.js
LMS API rodando na porta 3000...
$ curl -s -X POST http://localhost:3000/api/checkout -d '{"usr":"Guilherme",...,"card":"4111222233334444"}'
{"msg":"Sucesso","enrollment_id":2}
$ curl -s http://localhost:3000/api/admin/financial-report
[{"course":"Clean Architecture","revenue":997,"students":[{"student":"Leonan","paid":997}]}, ...]

# Projeto 3
$ python seed.py && python app.py
Seed concluído com sucesso!  3 usuários / 4 categorias / 10 tasks
$ curl -s -X POST http://localhost:5000/login -d '{"email":"joao@email.com","password":"1234"}'
{"message":"Login realizado com sucesso","token":"eyJhbGciOiJIUzI1NiIs...", ...}
$ curl -s http://localhost:5000/reports/summary | head -c 200
{"generated_at":"...","overdue":{"count":2,...},"overview":{"total_categories":4,"total_tasks":10,"total_users":3},...}
```

### Observações sobre o comportamento da skill em stacks diferentes

- O mesmo catálogo e o mesmo playbook (com exemplos em Python **e** JavaScript) foram suficientes para os 3 projetos sem nenhuma edição da skill entre execuções — apenas cópia da pasta `refactor-arch/`.
- A quantidade de findings caiu de 15 (projeto 1, monolito sem nenhuma camada) para 10 e 10 (projetos 2 e 3), o que é esperado: quanto mais desorganizado o ponto de partida, mais violações de MVC/SOLID concentradas em poucos arquivos.
- O projeto 3 foi o único caso onde a Fase 3 precisou **conservar** estrutura em vez de criá-la — validou que a regra de decisão de `architecture-guidelines.md` funciona na prática, não só na teoria.
- O projeto 2 foi o único caso de callback-based I/O assíncrono; o playbook de "promisificar" (item #11) só existe por causa desse projeto e não teria sido descoberto testando apenas os dois projetos Python.

## D) Como Executar

### Pré-requisitos

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) instalado e autenticado (`claude --version`).
- Python 3.11+ e `pip` (projetos 1 e 3).
- Node.js 18+ e `npm` (projeto 2).

### Rodar a skill em cada projeto

```bash
# Projeto 1 — Python/Flask (E-commerce)
cd code-smells-project
claude "/refactor-arch"

# Projeto 2 — Node.js/Express (LMS com checkout)
cd ../ecommerce-api-legacy
claude "/refactor-arch"

# Projeto 3 — Python/Flask (Task Manager, parcialmente organizado)
cd ../task-manager-api
claude "/refactor-arch"
```

Em cada projeto, a skill imprime o resumo da Fase 1, o relatório da Fase 2 e **pausa pedindo confirmação** (`[y/n]`) antes de tocar em qualquer arquivo — responda `y` para prosseguir com a Fase 3.

### Como validar que a refatoração funcionou

```bash
# Projeto 1
cd code-smells-project
pip install -r requirements.txt
python src/app.py        # sobe em http://localhost:5000
curl http://localhost:5000/produtos

# Projeto 2
cd ecommerce-api-legacy
npm install
npm start                 # sobe em http://localhost:3000
curl http://localhost:3000/api/admin/financial-report

# Projeto 3
cd task-manager-api
pip install -r requirements.txt
python seed.py
python app.py              # sobe em http://localhost:5000
curl http://localhost:5000/tasks
```

Se a aplicação subir sem exceções e os endpoints acima responderem com JSON válido, a refatoração está validada — foi exatamente esse o procedimento usado para preencher o checklist da seção C.
