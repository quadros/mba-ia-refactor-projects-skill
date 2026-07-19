# Audit Report — code-smells-project

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask 3.1.1
Files:   4 analyzed | ~780 lines of code

Summary
CRITICAL: 6 | HIGH: 3 | MEDIUM: 3 | LOW: 3

Findings

[CRITICAL] SQL Injection generalizado
File: models.py:28, 48-50, 58, 60, 68, 92, 109-111, 122-129, 140, 149-151, 155-166, 174, 188, 192, 220, 224, 279-280, 291-297
Description: Praticamente todas as queries do arquivo são montadas por concatenação de string com dados de entrada não sanitizados (ex.: "SELECT * FROM produtos WHERE id = " + str(id), inserts de produto/usuário concatenando nome/email/senha diretamente).
Impact: Qualquer parâmetro de rota, body ou querystring pode injetar SQL arbitrário — leitura, alteração ou destruição de todo o banco (produtos, usuários, pedidos), incluindo bypass de login.
Recommendation: Reescrever todas as queries com placeholders parametrizados (?) e parâmetros separados. Ver Playbook #3 (Parametrizar Queries).

[CRITICAL] Endpoint que executa SQL arbitrário sem autenticação
File: app.py:59-78
Description: A rota POST /admin/query lê uma string "sql" do corpo da requisição e a executa diretamente via cursor.execute(query), sem autenticação, allowlist ou sandboxing.
Impact: Equivale a um console SQL público — permite DROP TABLE, exfiltração completa de dados ou leitura do schema por qualquer cliente não autenticado.
Recommendation: Remover o endpoint ou protegê-lo atrás de autenticação/role de admin real e uma allowlist estrita de operações; nunca expor execução de SQL livre. Ver Playbook #1 (config/segurança) e guidelines de Controllers.

[CRITICAL] Endpoint de reset de banco sem autenticação
File: app.py:47-57
Description: POST /admin/reset-db apaga todas as linhas de itens_pedido, pedidos, produtos e usuarios sem qualquer verificação de identidade ou permissão.
Impact: Qualquer requisição não autenticada destrói todos os dados de produção da aplicação.
Recommendation: Proteger com autenticação/autorização de administrador ou remover do código de produção. Ver Playbook #1.

[CRITICAL] Credenciais hardcoded e expostas em endpoint público
File: app.py:7-8; controllers.py:288-289 (health_check)
Description: SECRET_KEY está fixa no código-fonte ("minha-chave-super-secreta-123") e é devolvida em texto puro, junto com o flag debug, na resposta JSON do endpoint público /health.
Impact: A chave de sessão Flask fica publicamente acessível a qualquer cliente, permitindo forjar cookies de sessão assinados pela aplicação.
Recommendation: Mover para variável de ambiente e nunca incluir segredos no corpo de resposta de nenhum endpoint. Ver Playbook #1 (Extrair Configuração).

[CRITICAL] Modo debug habilitado
File: app.py:8, 88
Description: app.config["DEBUG"] = True e app.run(..., debug=True) ficam ativos com a aplicação escutando em host="0.0.0.0".
Impact: Em caso de exceção não tratada, o debugger interativo do Werkzeug fica acessível via navegador, permitindo execução remota de código arbitrário.
Recommendation: Controlar debug por variável de ambiente, desabilitado por padrão. Ver Playbook #1.

[CRITICAL] God Module (models.py e controllers.py)
File: models.py:1-315; controllers.py:1-293
Description: Um único arquivo models.py concentra acesso a dados e SQL cru para 4 domínios (produtos, usuários, pedidos, itens de pedido); controllers.py mistura parsing de request, validação e orquestração para os mesmos 4 domínios em um único arquivo.
Impact: Qualquer mudança em uma entidade exige tocar um arquivo gigante compartilhado por todas as outras, tornando testes isolados e manutenção segura impraticáveis.
Recommendation: Separar em um model e um controller por domínio. Ver Playbook #2 (Split God Class por Domínio).

[HIGH] Senhas armazenadas e comparadas em texto puro
File: models.py:105-131 (login_usuario, criar_usuario)
Description: Não há hashing em nenhum momento — a senha é gravada como string literal e comparada diretamente na cláusula WHERE do SQL de login.
Impact: Qualquer vazamento do banco expõe as senhas de todos os usuários em texto legível; login também é vulnerável ao SQL Injection já reportado.
Recommendation: Aplicar hashing seguro na gravação e comparação. Ver Playbook #7 (Hashing Seguro de Senha).

[HIGH] Lógica de negócio e efeitos colaterais dentro do Controller
File: controllers.py:188-220 (criar_pedido)
Description: O handler HTTP de criação de pedido chama o model, mas também decide e executa (via print) o "envio" de e-mail, SMS e push, e imprime mensagens de log de negócio diretamente no controller.
Impact: A camada HTTP fica acoplada a regras/efeitos de domínio que deveriam estar em um serviço de notificação isolado e testável.
Recommendation: Extrair para um controller/service de pedidos que orquestra e delega notificações a um serviço dedicado. Ver Playbook #4 (Extrair Lógica de Negócio do Controller).

[HIGH] Validação duplicada entre criar_produto e atualizar_produto
File: controllers.py:24-62 (criar_produto), 64-96 (atualizar_produto)
Description: O mesmo bloco de validação de nome/preço/estoque/categoria é reescrito quase identicamente nas duas funções, incluindo a lista de categorias válidas hardcoded em cada uma.
Impact: Qualquer nova regra de validação precisa ser lembrada e replicada manualmente nos dois lugares, com alto risco de divergência futura.
Recommendation: Centralizar validação em uma função/schema único reutilizado por criação e atualização. Ver Playbook #12 (Centralizar Constantes e Validação).

[MEDIUM] Queries N+1 na listagem de pedidos
File: models.py:171-201 (get_pedidos_usuario), 203-233 (get_todos_pedidos)
Description: Para cada pedido é aberto um cursor para buscar seus itens, e para cada item outro cursor para buscar o nome do produto — 3 níveis de query aninhada.
Impact: O número de queries cresce linearmente com pedidos × itens, degradando performance rapidamente à medida que o volume de dados cresce.
Recommendation: Substituir por uma única query com JOIN entre pedidos, itens_pedido e produtos. Ver Playbook #6 (Eliminar Queries N+1).

[MEDIUM] Duplicação de mapeamento de linha para dicionário
File: models.py:9-22 (get_todos_produtos), 30-41 (get_produto_por_id), 301-314 (buscar_produtos)
Description: O mesmo dicionário de 8 campos de produto é reconstruído manualmente, campo a campo, em três funções diferentes.
Impact: Qualquer mudança de schema (novo campo, rename) precisa ser replicada em 3 lugares, com risco de inconsistência entre eles.
Recommendation: Extrair uma função única de serialização de linha e reutilizá-la nas três funções. Ver Playbook #8 (Eliminar Duplicação Reaproveitando o Model).

[MEDIUM] Listas de validação hardcoded fora de um módulo de constantes
File: controllers.py:52 (categorias_validas), controllers.py:242 (lista de status de pedido)
Description: Valores válidos de categoria e de status de pedido são listas literais recriadas inline nas funções de controller, sem um módulo central de constantes.
Impact: Divergência silenciosa entre pontos diferentes do código que deveriam usar exatamente o mesmo conjunto de valores válidos.
Recommendation: Mover para config/constants.py e importar em todos os pontos de uso. Ver Playbook #12.

[LOW] Logging via print() em vez de módulo de logging
File: controllers.py:8, 11, 57, 61, 106, 161, 179, 182, 208-210, 219, 248, 250
Description: Toda mensagem de diagnóstico, auditoria e erro é escrita com print() para stdout, sem nível, timestamp ou destino configurável.
Impact: Impossível filtrar por severidade ou redirecionar logs em produção; mistura saída de negócio com saída de erro.
Recommendation: Substituir por módulo logging configurado centralmente. Ver Playbook #5 (Error Handling e Logging Centralizados).

[LOW] Magic numbers/strings soltos no código
File: controllers.py:47-50 (limites de tamanho de nome hardcoded), models.py:256-262 (faixas de desconto hardcoded: 10000, 0.1, 5000, 0.05, 1000, 0.02)
Description: Limiares de negócio (tamanho mínimo/máximo de nome, faixas de faturamento para desconto) aparecem como literais soltos sem nome, sem explicação do porquê desses valores.
Impact: Dificulta entender e alterar regras de negócio com segurança — não fica claro se 10000/0.1 são regra de negócio estável ou valor de teste esquecido.
Recommendation: Extrair para constantes nomeadas em config/constants.py. Ver Playbook #12.

[LOW] Parâmetro nomeado id faz shadow do builtin do Python
File: controllers.py:14, 64, 98 (buscar_produto, atualizar_produto, deletar_produto); models.py:24, 54, 65 (funções equivalentes)
Description: O parâmetro id é usado repetidamente como nome de variável, sombreando a função builtin id() do Python dentro do escopo dessas funções.
Impact: Reduz legibilidade e pode causar bugs sutis caso o builtin id() precise ser usado dentro dessas mesmas funções no futuro.
Recommendation: Renomear para produto_id/usuario_id. Ver Playbook #14 (Renomear para Nomes de Domínio).

================================
Total: 15 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```
