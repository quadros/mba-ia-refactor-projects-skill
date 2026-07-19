# Audit Report — task-manager-api

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask 3.0.0 (+ Flask-SQLAlchemy)
Files:   15 analyzed | ~1158 lines of code

Summary
CRITICAL: 2 | HIGH: 2 | MEDIUM: 3 | LOW: 3

Findings

[CRITICAL] Hashing de senha com MD5
File: models/user.py:27-32 (set_password, check_password)
Description: A senha é transformada com hashlib.md5(pwd.encode()).hexdigest(), sem salt, e comparada por igualdade de string.
Impact: MD5 é criptograficamente quebrado e extremamente rápido de atacar por força bruta/rainbow table — qualquer vazamento do banco compromete as senhas de todos os usuários rapidamente, mesmo dentro de um projeto que já tem a camada de Model corretamente posicionada.
Recommendation: Substituir por werkzeug.security.generate_password_hash/check_password_hash. Ver Playbook #7 (Hashing Seguro de Senha).

[CRITICAL] Autenticação falsa (token forjável)
File: routes/user_routes.py:185-211 (login)
Description: O endpoint de login retorna 'token': 'fake-jwt-token-' + str(user.id) — uma string previsível, sem assinatura, expiração ou verificação criptográfica.
Impact: Qualquer cliente pode forjar acesso como qualquer usuário apenas conhecendo (ou adivinhando sequencialmente) seu id, sem nunca ter fornecido a senha correta em requisições subsequentes.
Recommendation: Gerar um JWT real assinado com a SECRET_KEY da aplicação, com expiração. Ver Playbook #10 (Substituir Autenticação Falsa por JWT Real).

[HIGH] Lógica de negócio duplicada fora do Model
File: routes/task_routes.py:30-39 (get_tasks), 71-80 (get_task); routes/user_routes.py:171-180 (get_user_tasks)
Description: O cálculo de "task atrasada" já existe corretamente encapsulado em Task.is_overdue() (models/task.py:50-60), mas é reimplementado inline, com o mesmo if/else aninhado, em pelo menos 3 lugares diferentes nas rotas.
Impact: A camada de rota faz trabalho de Model; qualquer mudança na regra de "atraso" (ex.: considerar fuso horário) precisa ser lembrada e replicada em 4 lugares (o Model + 3 rotas) em vez de um só.
Recommendation: Rotas devem chamar task.is_overdue() em vez de reimplementar a lógica. Ver Playbook #8 (Eliminar Duplicação Reaproveitando o Model).

[HIGH] Serialização duplicada em vez de reuso do Model
File: routes/task_routes.py:17-28 (get_tasks); routes/user_routes.py:162-169 (get_user_tasks)
Description: As rotas reconstroem manualmente, campo a campo, o mesmo dicionário que Task.to_dict() (models/task.py:23-36) já produz.
Impact: Duplicação que só existe porque a camada de rota não reutiliza a camada de Model — qualquer novo campo em Task precisa ser adicionado em múltiplos lugares.
Recommendation: Chamar task.to_dict() e complementar apenas com os campos derivados (overdue, user_name). Ver Playbook #8.

[MEDIUM] Queries N+1 em relatórios
File: routes/report_routes.py:53-68 (summary_report, laço user_stats)
Description: Para calcular produtividade por usuário, o código itera sobre todos os usuários e, para cada um, dispara uma nova query Task.query.filter_by(user_id=u.id) em memória, em vez de uma agregação SQL (GROUP BY).
Impact: O número de queries cresce linearmente com o número de usuários; em relatórios de summary_report e user_report, a mesma lógica de contagem por status é refeita em Python em vez de no banco.
Recommendation: Substituir por func.count/GROUP BY via SQLAlchemy. Ver Playbook #6 (Eliminar Queries N+1).

[MEDIUM] Segredos hardcoded
File: app.py:13 (SECRET_KEY); services/notification_service.py:9-10 (email_user, email_password do Gmail em texto puro)
Description: A chave de sessão Flask e as credenciais SMTP de um Gmail de produção estão fixas como literais no código-fonte, mesmo em um projeto com alguma organização de camadas.
Impact: Qualquer pessoa com acesso ao repositório tem acesso à conta de e-mail de produção usada para notificações e pode forjar sessões assinadas pela SECRET_KEY.
Recommendation: Mover para variáveis de ambiente. Ver Playbook #1 (Extrair Configuração).

[MEDIUM] except genérico engolindo erros
File: routes/task_routes.py:62 (except: no get_tasks); routes/user_routes.py:130-132 (except: no update_user)
Description: Cláusulas except: sem tipo capturam qualquer exceção e retornam sempre a mesma mensagem genérica ("Erro interno"/"Erro ao atualizar"), sem logar a causa raiz.
Impact: Bugs de programação reais (ex.: erro de tipo, atributo inexistente) ficam indistinguíveis de erros de negócio esperados, dificultando debug em produção.
Recommendation: Capturar exceções específicas e logar a causa antes de responder; usar um error handler centralizado para o caso genérico. Ver Playbook #5 (Error Handling Centralizado).

[LOW] Constantes definidas mas ignoradas pelo resto do código
File: utils/helpers.py:110-116 (VALID_STATUSES, VALID_ROLES, MIN_PASSWORD_LENGTH etc.) vs. listas literais repetidas em models/task.py:39, routes/task_routes.py:110, routes/user_routes.py:71
Description: O projeto já criou um módulo de constantes central em utils/helpers.py, mas models e routes ignoram-no e repetem as mesmas listas de valores válidos literalmente em vários pontos.
Impact: Duas fontes de verdade para o mesmo conjunto de valores válidos — pior do que não ter a constante, porque cria a falsa impressão de que há um único lugar para alterar essas regras.
Recommendation: Importar e usar as constantes já existentes em vez de duplicá-las. Ver Playbook #12 (Centralizar Constantes e Validação).

[LOW] Imports não utilizados
File: routes/task_routes.py:7 (json, os, sys, time); routes/report_routes.py:8 (json)
Description: Módulos são importados mas nunca referenciados no corpo dos arquivos.
Impact: Ruído que dificulta entender as dependências reais de cada módulo e pode mascarar imports realmente necessários perdidos no meio de imports mortos.
Recommendation: Remover imports não utilizados.

[LOW] Uso de datetime.utcnow() (API deprecated)
File: models/task.py (linhas 15-16, 52), models/user.py:14, routes/task_routes.py (múltiplas ocorrências), routes/report_routes.py (múltiplas ocorrências), seed.py
Description: datetime.datetime.utcnow() é deprecated desde Python 3.12 em favor de datetime.now(datetime.UTC); o projeto usa esse padrão extensivamente como default de coluna e em comparações de data.
Impact: Em versões futuras do Python, o uso continuado gera warnings e, eventualmente, pode ser removido; o valor retornado também é "naive" (sem timezone), propenso a bugs de comparação com datas timezone-aware.
Recommendation: Substituir por datetime.now(UTC) em runtimes Python 3.12+. Ver Playbook #13 (Substituir API Deprecated).

================================
Total: 10 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```
