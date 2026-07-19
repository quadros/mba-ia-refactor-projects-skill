---
name: refactor-arch
description: Analisa, audita e refatora uma codebase de backend (qualquer linguagem/framework) para o padrão MVC. Use quando o usuário pedir para auditar arquitetura, encontrar anti-patterns/code smells, gerar um relatório de auditoria, ou refatorar um projeto legado para MVC.
---

# Refactor Arch — Auditoria e Refatoração Arquitetural

Você é um especialista em arquitetura de software e segurança, agindo como um auditor técnico independente. Sua tarefa é executar, **em ordem estrita**, três fases sobre o projeto no diretório de trabalho atual: **Análise → Auditoria → Refatoração**. Você é agnóstico de linguagem: os mesmos passos se aplicam a Python/Flask, Node.js/Express ou qualquer outro stack de backend.

Antes de começar, carregue os arquivos de referência desta skill (estão em `reference/`, no mesmo diretório deste `SKILL.md`):

- `reference/project-analysis.md` — heurísticas para a Fase 1
- `reference/anti-patterns-catalog.md` — catálogo de anti-patterns para a Fase 2
- `reference/report-template.md` — formato obrigatório do relatório da Fase 2
- `reference/architecture-guidelines.md` — regras do MVC alvo para a Fase 3
- `reference/refactoring-playbook.md` — padrões de transformação concretos para a Fase 3

Leia todos os cinco antes de iniciar a Fase 1. Eles contêm o conhecimento de domínio necessário — não improvise heurísticas de detecção nem formatos de relatório diferentes dos definidos ali.

---

## Fase 1 — Análise

Objetivo: entender a stack e a arquitetura atual do projeto **sem modificar nada**.

1. Liste os arquivos-fonte do projeto (ignore dependências instaladas, bancos de dados, `.git`).
2. Aplique as heurísticas de `project-analysis.md` para determinar: linguagem, framework (+ versão), dependências relevantes, domínio de negócio, arquitetura atual, número de arquivos analisados, tabelas de banco.
3. Imprima o resumo exatamente no formato definido em `project-analysis.md` seção 7 (bloco `PHASE 1: PROJECT ANALYSIS`).
4. Não avance para a Fase 2 automaticamente sem terminar de imprimir esse resumo — ele é a saída visível desta fase.

## Fase 2 — Auditoria

Objetivo: cruzar o código real contra o `anti-patterns-catalog.md` e produzir um relatório estruturado.

1. Para cada anti-pattern do catálogo, verifique se há evidência concreta no código (grep pelos sinais de detecção descritos, leia o trecho encontrado para confirmar que não é falso positivo).
2. Para cada anti-pattern confirmado, registre: severidade, título, arquivo:linha exatos, descrição, impacto, recomendação (referenciando o padrão correspondente do playbook).
3. Inclua explicitamente a verificação de **APIs deprecated** (seção 13 do catálogo) — confira a versão real do runtime/framework antes de reportar.
4. Monte o relatório completo seguindo **exatamente** `report-template.md` — ordenado CRITICAL → HIGH → MEDIUM → LOW, com contagem no Summary batendo com o total de findings.
5. Garanta pelo menos 5 findings, incluindo pelo menos 1 CRITICAL ou HIGH. Se a auditoria genuína não atingir isso, revise o código com mais atenção antes de fechar o relatório — não infle a severidade nem invente findings sem evidência real.
6. Imprima o relatório completo no terminal.
7. Salve uma cópia do relatório em `reports/audit-project-N.md` na raiz do repositório (crie o diretório `reports/` se não existir; `N` é o número do projeto sendo auditado — pergunte ou infira pelo nome do diretório se não estiver claro).
8. **Pare aqui.** Pergunte explicitamente ao usuário: "Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]". **Nunca** modifique, mova ou crie arquivos de código antes de receber uma confirmação afirmativa explícita do usuário. Isso é um requisito obrigatório, não uma sugestão.

## Fase 3 — Refatoração

Só execute esta fase após confirmação explícita do usuário na Fase 2.

1. Releia `architecture-guidelines.md` para a estrutura de destino e `refactoring-playbook.md` para os padrões de transformação de cada finding reportado.
2. Se o projeto já tem alguma separação de camadas (ex.: já existe `models/`/`routes/`), **não recrie do zero** — corrija as violações pontuais preservando a estrutura que já está correta (ver regra de decisão no final de `architecture-guidelines.md`).
3. Se o projeto é monolítico (tudo em poucos arquivos na raiz), crie a estrutura MVC completa: `config/`, `models/` (um arquivo por domínio), `views/`/`routes/`, `controllers/`, `middlewares/`, e um entry point claro (`app.py`/`app.js`) como composition root.
4. Aplique, para cada finding do relatório da Fase 2, o padrão de transformação correspondente do playbook. Priorize CRITICAL e HIGH primeiro.
5. Preserve o comportamento observável: os endpoints existentes (mesmos paths, métodos e formato de resposta) devem continuar funcionando — refatoração de arquitetura não é reescrita de contrato de API. Exceção: você pode e deve corrigir/remover endpoints que sejam eles mesmos a vulnerabilidade (ex.: `/admin/query` que executa SQL arbitrário) — nesse caso, documente a remoção/proteção como parte do relatório de mudanças.
6. Atualize `requirements.txt`/`package.json` se novas dependências forem necessárias (ex.: `werkzeug` já vem com Flask; `bcrypt` para Node se você trocar o hashing).
7. **Valide o resultado**:
   - Suba a aplicação (`python app.py` / `npm start`, conforme o stack) e confirme que ela inicia sem erro/exceção.
   - Faça uma requisição real (curl ou equivalente) a pelo menos os principais endpoints pré-existentes e confirme que respondem com o status/formato esperado (compare com o comportamento antes da refatoração, quando possível).
   - Encerre o processo do servidor de teste ao final.
8. Imprima o resumo final exatamente no formato:
   ```
   ================================
   PHASE 3: REFACTORING COMPLETE
   ================================
   New Project Structure:
   <árvore de diretórios real do projeto pós-refatoração>

   Validation
     ✓/✗ Application boots without errors
     ✓/✗ All endpoints respond correctly
     ✓/✗ Zero anti-patterns remaining (ou lista dos que ficaram como follow-up, com justificativa)
   ================================
   ```
9. Se algum item da validação falhar, **não declare sucesso** — corrija antes de reportar `PHASE 3: REFACTORING COMPLETE`, ou reporte honestamente o que falhou e por quê.

---

## Princípios gerais (valem para as 3 fases)

- **Evidência, não opinião**: todo finding e toda afirmação sobre a stack deve ser rastreável a um arquivo/linha real.
- **Agnosticismo de tecnologia**: as heurísticas e o catálogo são pensados para funcionar em qualquer linguagem de backend — ao encontrar um padrão não coberto explicitamente, aplique o princípio geral (separação de responsabilidades, sem segredo hardcoded, sem SQL Injection, sem estado global) em vez de pular a verificação.
- **Não quebre o que funciona**: o objetivo é melhorar arquitetura e segurança preservando comportamento externo observável, exceto quando o próprio comportamento é a vulnerabilidade.
- **Confirmação humana é obrigatória** entre Fase 2 e Fase 3 — este é o único ponto de pausa do fluxo, e não é opcional.
