# Audit Report — ecommerce-api-legacy

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   Node.js + Express ^4.18.2

Files:   3 analyzed | ~180 lines of code

Summary
CRITICAL: 3 | HIGH: 2 | MEDIUM: 2 | LOW: 3

Findings

[CRITICAL] God Class "AppManager"
File: src/AppManager.js:1-141
Description: Uma única classe concentra abertura de conexão com banco, criação de todo o schema, seed de dados, definição de todas as rotas HTTP (setupRoutes) e toda a lógica de negócio de checkout/pagamento/relatório financeiro.
Impact: Impossível testar checkout isoladamente sem subir Express + SQLite reais; qualquer mudança em uma rota arrisca quebrar as outras, e não há nenhuma fronteira entre HTTP, regra de negócio e persistência.
Recommendation: Separar em models por entidade (User, Course, Enrollment, Payment), um service de checkout e rotas finas em Express Router. Ver Playbook #2 (Split God Class por Domínio).

[CRITICAL] Segredos e credenciais hardcoded
File: src/utils.js:1-7
Description: dbPass, paymentGatewayKey ("pk_live_...", indicando ambiente de produção) e smtpUser estão fixos como literais no código-fonte versionado.
Impact: Qualquer pessoa com acesso ao repositório (incluindo histórico git) tem acesso à chave real do gateway de pagamento e às credenciais de banco/e-mail de produção.
Recommendation: Mover para variáveis de ambiente. Ver Playbook #1 (Extrair Configuração).

[CRITICAL] "Criptografia" de senha inventada e reversível
File: src/utils.js:17-23 (badCrypto); src/AppManager.js:45,68 (uso e log em claro)
Description: Em vez de um hash criptográfico, badCrypto repete um base64 truncado 10.000 vezes — não tem propriedade de via única e é previsível/colidível; além disso, a senha em claro e a chave do gateway de pagamento são impressas no console (linha 45) antes do "hash".
Impact: Senhas de usuário armazenadas de forma efetivamente reversível; segredo de pagamento e senha de usuário vazam em qualquer coletor de logs.
Recommendation: Substituir por bcrypt/argon2 e remover o log de dados sensíveis. Ver Playbook #7 (Hashing Seguro de Senha).

[HIGH] Callback hell sem tratamento de erro consistente
File: src/AppManager.js:80-129 (GET /api/admin/financial-report)
Description: Cadeia de callbacks aninhados (db.all → forEach → db.all → forEach → db.get → db.get) com contadores manuais (coursesPending, enrPending) para saber quando a resposta terminou, em vez de Promise.all/async-await; nem todo callback trata err.
Impact: Código frágil e difícil de testar; condição de corrida potencial se qualquer callback disparar fora da ordem esperada; erros de banco em callbacks internos são silenciosamente ignorados (parâmetro err não verificado em vários pontos).
Recommendation: Promisificar o driver sqlite3 e reescrever com async/await. Ver Playbook #11 (Promisificar / Eliminar Callback Hell).

[HIGH] Estado global mutável
File: src/utils.js:9-10 (globalCache, totalRevenue)
Description: Um objeto de cache e um contador de receita vivem como variáveis de módulo mutáveis, lidas e escritas por handlers de requisições concorrentes, sem nenhum isolamento por requisição.
Impact: Sob carga concorrente, requisições diferentes podem ler/escrever o mesmo estado de forma não determinística — bug de corrida garantido e impossível de testar de forma isolada.
Recommendation: Encapsular em um serviço com interface explícita (cacheService), instanciado e injetado, não uma variável solta de módulo. Ver Playbook #9 (Encapsular Estado Global Mutável).

[MEDIUM] Queries N+1 em cascata no relatório financeiro
File: src/AppManager.js:80-129
Description: Para cada curso é buscado o array de matrículas; para cada matrícula, uma query de usuário e uma de pagamento — O(cursos × matrículas) round-trips ao banco em vez de um JOIN único.
Impact: Tempo de resposta do relatório degrada linearmente (e depois quadraticamente, com aninhamento) conforme a base de cursos/matrículas cresce.
Recommendation: Uma única query com JOIN entre courses, enrollments, users e payments. Ver Playbook #6 (Eliminar Queries N+1).

[MEDIUM] Validação de pagamento inexistente
File: src/AppManager.js:29-48 (POST /api/checkout)
Description: O número do cartão só é "validado" checando se começa com o dígito "4" (cc.startsWith("4")); e-mail e senha só passam por checagem de truthy, sem formato/força.
Impact: Qualquer string começando com "4" é aceita como cartão válido; não há verificação real de formato de pagamento nem de e-mail, abrindo espaço para dados inconsistentes e abuso do fluxo de checkout.
Recommendation: Validação de entrada explícita na fronteira do controller antes de chamar o serviço de pagamento. Ver Playbook #12 (Centralizar Validação).

[LOW] Corrupção de dados sabida e ignorada
File: src/AppManager.js:131-137 (DELETE /api/users/:id)
Description: O próprio texto de resposta reconhece que o usuário é apagado mas matrículas e pagamentos relacionados "ficaram sujos no banco" — não há cascade nem soft delete.
Impact: Registros órfãos se acumulam no banco a cada exclusão de usuário, corrompendo integridade referencial silenciosamente e retornando uma mensagem de "sucesso" para uma operação que deixa o sistema em estado inconsistente.
Recommendation: Model de usuário deve remover/tratar registros dependentes explicitamente (cascade delete ou soft delete), nunca reportar sucesso para um estado inconsistente. Ver Playbook #2 e #4.

[LOW] Nomenclatura de variáveis ilegível
File: src/AppManager.js:29-33 (u, e, p, cid, cc)
Description: Parâmetros que representam nome de usuário, e-mail, senha, id do curso e número de cartão usam nomes de 1-2 letras.
Impact: Reduz legibilidade e aumenta o risco de trocar acidentalmente a ordem/uso de parâmetros sensíveis (ex.: confundir senha com cartão).
Recommendation: Renomear para nomes de domínio (userName, email, password, courseId, cardNumber). Ver Playbook #14 (Renomear para Nomes de Domínio).

[LOW] Logging de dados sensíveis no console
File: src/AppManager.js:45
Description: console.log imprime o número do cartão de crédito e a chave do gateway de pagamento em texto puro a cada checkout.
Impact: Dados sensíveis (PCI) acabam em qualquer coletor de log do processo, violando práticas básicas de proteção de dados de pagamento.
Recommendation: Remover o log ou mascarar os dados sensíveis antes de logar; centralizar logging estruturado. Ver Playbook #5 (Error Handling e Logging Centralizados).

================================
Total: 10 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```
