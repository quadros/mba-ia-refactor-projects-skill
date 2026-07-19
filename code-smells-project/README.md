# code-smells-project

API de E-commerce em Python/Flask, refatorada para o padrão **MVC** pela skill `refactor-arch` (ver `.claude/skills/refactor-arch/`). O relatório de auditoria que motivou esta refatoração está em `../reports/audit-project-1.md`.

## Estrutura

```
src/
├── app.py                  # composition root
├── config/
│   ├── settings.py         # variáveis de ambiente (nenhum segredo hardcoded)
│   ├── constants.py        # categorias/status válidos, faixas de desconto
│   └── database.py         # conexão SQLite, schema, seed
├── models/                 # um arquivo por domínio, queries parametrizadas
│   ├── produto_model.py
│   ├── usuario_model.py
│   └── pedido_model.py
├── controllers/            # orquestram o caso de uso, sem SQL/HTTP direto
│   ├── produto_controller.py
│   ├── usuario_controller.py
│   └── pedido_controller.py
├── views/                  # rotas HTTP finas (Flask Blueprints)
│   ├── produto_routes.py
│   ├── usuario_routes.py
│   ├── pedido_routes.py
│   └── misc_routes.py      # index, health
├── services/
│   └── notification_service.py
└── middlewares/
    └── error_handler.py    # tratamento de erro + logging centralizados
```

## Como rodar

```bash
pip install -r requirements.txt
python src/app.py
```

A aplicação sobe em `http://localhost:5000`. O banco SQLite (`loja.db`) é criado automaticamente no primeiro boot, já com produtos e usuários de exemplo (senhas agora armazenadas com hash).

Configuração via variáveis de ambiente (ver `.env.example`): `SECRET_KEY`, `FLASK_DEBUG`, `DATABASE_PATH`, `HOST`, `PORT`.

## O que mudou em relação à versão original

- Removida a SQL Injection generalizada — todas as queries agora são parametrizadas.
- Removidos os endpoints `/admin/query` (executava SQL arbitrário do body) e `/admin/reset-db` (apagava o banco), ambos sem autenticação — eram a própria vulnerabilidade CRITICAL, não uma feature legítima.
- `SECRET_KEY` e `DEBUG` deixaram de ser hardcoded e de vazar na resposta do `/health`.
- Senhas passam a ser armazenadas com hash (`werkzeug.security`) em vez de texto puro.
- Lógica de negócio, SQL e roteamento — antes concentrados em `models.py`/`controllers.py` — foram separados em Models, Controllers e Views por domínio.
- Queries N+1 na listagem de pedidos substituídas por `JOIN`.
- Detalhes completos no relatório de auditoria: `../reports/audit-project-1.md`.
