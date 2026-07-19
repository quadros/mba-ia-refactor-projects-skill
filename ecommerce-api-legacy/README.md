# ecommerce-api-legacy

LMS API (com fluxo de checkout) em Node.js/Express, refatorada para o padrão **MVC** pela skill `refactor-arch` (ver `.claude/skills/refactor-arch/`, copiada de `code-smells-project/`). O relatório de auditoria que motivou esta refatoração está em `../reports/audit-project-2.md`.

## Estrutura

```
src/
├── app.js                   # composition root
├── config/settings.js       # variáveis de ambiente (nenhum segredo hardcoded)
├── db/database.js           # conexão SQLite promisificada, schema, seed
├── models/                  # um arquivo por domínio, queries parametrizadas
│   ├── userModel.js
│   ├── courseModel.js
│   ├── enrollmentModel.js
│   ├── paymentModel.js
│   └── auditModel.js
├── controllers/             # orquestram o caso de uso (checkout, relatório, exclusão de usuário)
│   ├── checkoutController.js
│   ├── reportController.js
│   └── userController.js
├── routes/                  # rotas Express finas
│   ├── checkoutRoutes.js
│   ├── reportRoutes.js
│   └── userRoutes.js
├── services/
│   ├── authService.js       # hashing de senha (scrypt)
│   ├── paymentService.js    # gateway de pagamento simulado
│   └── cacheService.js      # substitui o cache global mutável
└── middlewares/
    ├── errorHandler.js      # tratamento de erro centralizado
    └── httpError.js
```

## Como rodar

```bash
npm install
npm start
```

A aplicação sobe em `http://localhost:3000`. O banco SQLite é em memória e já carrega seeds automaticamente no boot.

Exemplos de requisições estão em `api.http`.

## O que mudou em relação à versão original

- `AppManager.js` (God Class que misturava conexão de banco, rotas e regra de negócio) foi eliminada — dividida em models, controllers, routes e services.
- Segredos (`dbPass`, `paymentGatewayKey`, `smtpUser`) deixaram de ser hardcoded, agora vêm de variáveis de ambiente.
- `badCrypto` (base64 repetido, reversível) substituído por hashing com `scrypt`.
- Callback hell do relatório financeiro substituído por `async/await` + uma única query com `JOIN` (elimina N+1).
- Estado global mutável (`globalCache`) encapsulado em `cacheService`.
- `DELETE /api/users/:id` agora remove matrículas e pagamentos relacionados em vez de deixá-los órfãos no banco.
- Detalhes completos no relatório de auditoria: `../reports/audit-project-2.md`.
