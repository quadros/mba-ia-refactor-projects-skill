# Guidelines de Arquitetura — Padrão MVC Alvo

Define a estrutura de destino da **Fase 3**, agnóstica de linguagem. Os nomes de diretório abaixo são a convenção padrão desta skill; adapte a capitalização/idioma aos arquivos já existentes no projeto (ex.: se o projeto já usa `models/`/`routes/` em inglês, mantenha; não force renomear o que já está correto).

```
src/  (ou raiz do projeto, se não houver src/)
├── config/
│   └── settings.(py|js)      # toda config e segredos, lidos de variáveis de ambiente
├── models/
│   └── <entidade>_model.(py|js)   # um arquivo por domínio/entidade
├── views/ ou routes/
│   └── <entidade>_routes.(py|js)  # definição de endpoints, sem lógica de negócio
├── controllers/
│   └── <entidade>_controller.(py|js)  # orquestra o caso de uso, chama models
├── middlewares/  (ou similar)
│   └── error_handler.(py|js) # tratamento de erro e logging centralizados
└── app.(py|js)                # composition root — monta tudo, não contém regra de negócio
```

## Responsabilidade de cada camada

### Models
- **Fazem**: acesso a dados (queries parametrizadas), validação de invariantes da entidade (ex.: `is_overdue()`, `validate_priority()`), serialização (`to_dict()`).
- **Não fazem**: nada de HTTP (não conhecem `request`/`response`), não formatam mensagens de erro HTTP, não decidem status code.
- Um model por entidade/domínio (`produto_model`, `usuario_model`, `pedido_model` — nunca um `models.py` único para tudo).
- Toda query usa parâmetros (`?`/`%s`/placeholder nomeado), nunca concatenação de string.

### Views / Routes
- **Fazem**: mapeiam método HTTP + path → função de controller; extraem parâmetros da requisição (path, query, body) e repassam; retornam a resposta HTTP com o status code apropriado.
- **Não fazem**: cálculo de negócio, acesso direto a banco, validação de regra de domínio (validação de **formato de entrada HTTP**, tipo "campo obrigatório presente no JSON", pode ficar aqui ou ser delegada ao controller — mas nunca regra de negócio como "estoque suficiente").
- Devem ser "finas": uma rota idealmente tem 3-6 linhas (parse → chama controller → responde).

### Controllers
- **Fazem**: orquestram o caso de uso — chamam um ou mais models/services, aplicam a sequência de passos da regra de negócio, decidem sucesso/erro de domínio.
- **Não fazem**: SQL cru, não conhecem detalhes de framework HTTP além de receber dados já parseados e devolver um resultado estruturado (dict/objeto) — quem traduz isso para HTTP é a View/Route.
- Efeitos colaterais de domínio (enviar e-mail, notificar) são delegados a um `service`, não implementados inline com `print`/`console.log`.

### Config
- Um único módulo lê todas as variáveis de ambiente (`os.environ`/`process.env`) e expõe um objeto/dict de configuração tipado.
- Nenhum segredo, chave ou senha aparece como literal fora deste módulo (e mesmo aqui, o valor vem de env var, com um default seguro só para desenvolvimento local, nunca um segredo real).

### Middlewares / Error Handling
- Um ponto único captura exceções não tratadas e as transforma em resposta HTTP padronizada (`{"erro": mensagem}`, status code apropriado) — substitui os `try/except`/`try/catch` repetidos em cada handler.
- Logging estruturado (nível, timestamp) acontece aqui e em qualquer módulo de serviço, nunca via `print`/`console.log` solto.

### Entry point / Composition Root
- `app.py`/`app.js` apenas: cria a instância do framework, registra config, registra middlewares, registra rotas/blueprints, inicia o servidor.
- Não contém handlers de rota inline com lógica, não define schema de banco, não faz seed de dados (isso vai para um script/módulo separado, como este projeto já faz corretamente com `seed.py` no projeto 3).

## Regra de decisão para Fase 3

Antes de mover código, pergunte para cada trecho: **"essa linha decide algo sobre HTTP, sobre a entidade de negócio, ou sobre como os dados são persistidos?"**
- HTTP → View/Route
- Negócio/orquestração → Controller
- Persistência/invariante da entidade → Model

Se o projeto **já tiver alguma separação** (caso do projeto 3, `task-manager-api`), a Fase 3 não recria a estrutura do zero — ela corrige as violações pontuais (lógica de negócio duplicada nas rotas, segredo hardcoded, hash fraco) mantendo os diretórios existentes, e só introduz `controllers/`/`config/`/`middlewares/` se eles realmente não existirem e forem necessários para eliminar um finding da auditoria.
