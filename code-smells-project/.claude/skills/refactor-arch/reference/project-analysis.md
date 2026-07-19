# Análise de Projeto — Heurísticas de Detecção

Este documento orienta a **Fase 1 (Análise)**. O objetivo é produzir um resumo factual e verificável da stack e da arquitetura atual — nunca adivinhar. Toda afirmação deve vir de uma evidência concreta (um arquivo, uma linha, uma dependência).

## 1. Detecção de linguagem

Liste os arquivos-fonte do projeto (ignore `node_modules/`, `venv/`, `.venv/`, `__pycache__/`, `.git/`, arquivos de banco `*.db`, `*.sqlite`) e conte por extensão.

| Sinal | Linguagem |
|---|---|
| `requirements.txt`, `pyproject.toml`, `Pipfile`, maioria de arquivos `*.py` | Python |
| `package.json`, maioria de arquivos `*.js`/`*.ts` | Node.js / JavaScript / TypeScript |
| `pom.xml`, `build.gradle`, `*.java` | Java |
| `go.mod`, `*.go` | Go |
| `Gemfile`, `*.rb` | Ruby |
| `composer.json`, `*.php` | PHP |

Se houver mistura, a linguagem "principal" é a do runtime da aplicação (ex.: scripts `.sh` de deploy não contam).

## 2. Detecção de framework

Nunca assuma a versão — leia o manifest de dependências.

- **Python**: abra `requirements.txt` / `pyproject.toml`.
  - `flask` → Flask (a versão vem do pin, ex. `flask==3.1.1`)
  - `django` → Django
  - `fastapi` → FastAPI
  - Confirme com o import real no entry point (`from flask import Flask`, `app = Flask(__name__)`).
- **Node.js**: abra `package.json` → bloco `dependencies`.
  - `express` → Express (versão do `package.json`, ex. `^4.18.2`)
  - `fastify`, `koa`, `@nestjs/core` → respectivamente
  - Confirme com `require('express')` / `import express from 'express'` no entry point.

Reporte também dependências auxiliares relevantes para a arquitetura (ex.: `flask-cors`, `flask-sqlalchemy`, `sqlite3`, `body-parser`) — elas indicam camadas existentes (CORS, ORM, parsing).

## 3. Detecção de banco de dados

Procure por:

- Import/require de driver: `sqlite3`, `psycopg2`, `pymysql`, `mongoose`, `sqlite3` (node), `mysql2`, `pg`.
- ORMs: `flask_sqlalchemy`/`SQLAlchemy`, `sequelize`, `prisma`, `typeorm`, `mongoose`.
- Strings de conexão / `DATABASE_URL` / arquivos `*.db`.
- `CREATE TABLE` no código (schema definido em runtime, típico de projetos sem migrations) — extraia os nomes de tabela literalmente do SQL encontrado.

Liste as tabelas/coleções encontradas nominalmente (ex.: `produtos, usuarios, pedidos, itens_pedido`), não apenas "SQLite".

## 4. Detecção de domínio de negócio

O domínio não é adivinhado — é inferido de:

- Nomes de rotas/endpoints (`/produtos`, `/pedidos`, `/checkout`, `/tasks`, `/users`).
- Nomes de tabelas/models.
- Texto do `README.md` do projeto, se existir.
- Mensagens/strings literais no código (ex.: `"Bem-vindo à API da Loja"`).

Descreva o domínio em uma linha objetiva, citando as entidades principais entre parênteses (ex.: `E-commerce API (produtos, pedidos, usuários)`, `LMS API com fluxo de checkout (cursos, matrículas, pagamentos)`, `Task Manager API (tasks, usuários, categorias)`).

## 5. Mapeamento de arquitetura atual

Classifique em uma das categorias:

- **Monolítica sem camadas**: toda a lógica (rotas + regra de negócio + acesso a dados) está em poucos arquivos na raiz, sem diretórios `models/`, `controllers/`, `routes/`. Sinal: 3-5 arquivos concentram >80% do código.
- **Parcialmente organizada**: já existem diretórios como `models/`, `routes/`, `services/`, `utils/`, mas a separação é inconsistente — lógica de negócio ainda vaza para rotas, ou models fazem mais que dados. Sinal: existe estrutura de pastas, mas o código dentro delas viola as responsabilidades esperadas (ver `architecture-guidelines.md`).
- **MVC bem aplicado**: models sem HTTP, controllers sem SQL cru, rotas finas. (Raro nos projetos-alvo deste desafio — é o estado final que a Fase 3 produz.)

Ao classificar "parcialmente organizada", **não pare na existência das pastas** — abra os arquivos e verifique se a separação é real (ver seção "God Class disfarçado" no catálogo de anti-patterns).

## 6. Contagem de arquivos e linhas

Use `find`/`wc` para números exatos, nunca estimativas de cabeça:

```bash
find . -name '*.py' -not -path '*/venv/*' -not -path '*/__pycache__/*' | xargs wc -l
find . -name '*.js' -not -path '*/node_modules/*' | xargs wc -l
```

Reporte "Source files: N files analyzed" com o N real da contagem, e a soma aproximada de linhas.

## 7. Formato de saída da Fase 1

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <linguagem>
Framework:     <framework> <versão>
Dependencies:  <libs relevantes separadas por vírgula>
Domain:        <domínio inferido (entidades principais)>
Architecture:  <classificação> — <justificativa curta em uma linha>
Source files:  <N> files analyzed
DB tables:     <lista de tabelas/coleções, se aplicável>
================================
```

Esse resumo deve ser suficiente para alguém que nunca viu o projeto entender, em 7 linhas, o que ele é e como está organizado — sem abrir um único arquivo.
