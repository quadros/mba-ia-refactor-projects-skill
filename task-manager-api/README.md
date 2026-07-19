# task-manager-api

API de Task Manager em Python/Flask. Já tinha alguma separação de camadas (`models/`, `routes/`, `services/`, `utils/`) antes da refatoração; a skill `refactor-arch` (ver `.claude/skills/refactor-arch/`, copiada de `code-smells-project/`) **preservou essa estrutura** e corrigiu pontualmente os problemas encontrados, em vez de recriar tudo do zero — acrescentando apenas `config/`, `controllers/` e `middlewares/`, que não existiam e eram necessários para eliminar findings da auditoria. O relatório está em `../reports/audit-project-3.md`.

## Estrutura

```
app.py                       # composition root
database.py                  # instância SQLAlchemy
config/settings.py           # variáveis de ambiente (nenhum segredo hardcoded) — NOVO
controllers/                 # orquestram o caso de uso — NOVO
├── task_controller.py
├── user_controller.py
├── report_controller.py
└── category_controller.py
models/                      # já existia — corrigido (hash de senha, datetime)
├── task.py
├── user.py
└── category.py
routes/                      # já existia — agora rotas finas, chamando controllers
├── task_routes.py
├── user_routes.py
└── report_routes.py
services/
└── notification_service.py  # já existia — credenciais movidas para config
middlewares/
└── error_handler.py         # tratamento de erro centralizado — NOVO
utils/
├── helpers.py                # já existia — constantes agora realmente usadas
└── auth.py                   # geração/verificação de JWT real — NOVO
```

## Como rodar

```bash
pip install -r requirements.txt
python seed.py
python app.py
```

A aplicação sobe em `http://localhost:5000`. Rode `seed.py` antes do primeiro boot para popular usuários, categorias e tasks de exemplo.

Configuração via variáveis de ambiente (ver `.env.example`): `SECRET_KEY`, `DATABASE_URI`, `SMTP_*`, `JWT_EXPIRATION_HOURS`.

## O que mudou em relação à versão original

- Hash de senha migrado de MD5 (quebrado) para `werkzeug.security`.
- Login passa a emitir um JWT real assinado (`utils/auth.py`), em vez de `'fake-jwt-token-' + id`.
- Lógica de "task atrasada" e serialização, antes duplicadas em 3+ rotas, agora só existem em `Task.to_dict()`/`Task.is_overdue()` — rotas e controllers reaproveitam.
- Produtividade por usuário em `/reports/summary`, antes uma query por usuário em loop (N+1), agora uma única query agregada com `GROUP BY`.
- `SECRET_KEY` e credenciais SMTP deixaram de ser hardcoded.
- `except:` genéricos substituídos por tratamento de erro centralizado (`middlewares/error_handler.py`).
- `datetime.utcnow()` (deprecated) substituído por `utils.helpers.utcnow()`.
- Constantes já existentes em `utils/helpers.py` (status/roles válidos) agora são de fato importadas e usadas, em vez de duplicadas como listas literais.
- Detalhes completos no relatório de auditoria: `../reports/audit-project-3.md`.
