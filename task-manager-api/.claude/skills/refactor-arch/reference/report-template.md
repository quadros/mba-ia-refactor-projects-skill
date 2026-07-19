# Template de Relatório de Auditoria (Fase 2)

Este é o formato **obrigatório** de saída da Fase 2. Preencha exatamente esta estrutura — não resuma, não pule seções.

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <nome do diretório do projeto>
Stack:   <linguagem> + <framework>
Files:   <N> analyzed | ~<M> lines of code

Summary
CRITICAL: <n> | HIGH: <n> | MEDIUM: <n> | LOW: <n>

Findings

[CRITICAL] <Nome do anti-pattern>
File: <arquivo>:<linha ou intervalo de linhas>
Description: <o que foi encontrado, em 1-3 frases, citando o trecho relevante>
Impact: <consequência concreta — o que quebra, que risco existe, por que importa>
Recommendation: <ação de refatoração recomendada, referenciando o padrão do playbook>

[CRITICAL] <próximo finding CRITICAL>
...

[HIGH] <próximo finding>
...

[MEDIUM] <próximo finding>
...

[LOW] <próximo finding>
...

================================
Total: <N> findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

## Regras de preenchimento

1. **Ordenação obrigatória**: CRITICAL primeiro, depois HIGH, depois MEDIUM, depois LOW. Dentro da mesma severidade, ordem de descoberta é aceitável.
2. **Arquivo e linha exatos**: `File:` deve apontar para a linha real onde o problema começa (e o intervalo, se for um bloco/God Class). Nunca escreva "em vários lugares" sem listar pelo menos os principais arquivos:linhas.
3. **Summary deve bater com a contagem real** de findings listados abaixo — some antes de escrever o total.
4. **Recommendation** deve ser acionável e, sempre que possível, citar o padrão de transformação equivalente em `refactoring-playbook.md` (ex.: "Extrair para módulo de config — ver Playbook #1").
5. **Mínimo de findings**: o relatório deve ter pelo menos 5 findings, com pelo menos 1 CRITICAL ou HIGH. Se o projeto for pequeno e não atingir isso organicamente, revise o código com mais cuidado antes de concluir a auditoria — não infle findings artificiais nem invente severidade maior do que a real.
6. **Pausa obrigatória**: depois de imprimir o relatório completo, **pare e pergunte ao usuário** se deseja prosseguir para a Fase 3 (`[y/n]`). Nunca inicie modificação de arquivos antes dessa confirmação explícita.
7. Ao final da fase 2 fora do terminal interativo (ex.: quando o relatório precisa ser salvo em arquivo), salve exatamente este texto — sem reformulação — em `reports/audit-project-N.md`, com um cabeçalho `# Audit Report — <nome do projeto>` acima do bloco.
