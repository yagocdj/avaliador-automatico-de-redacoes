# 📘 Guia de Processamento dos Experimentos

## 🎯 Objetivo

Este guia explica como processar os experimentos de avaliação automatizada de redações com salvamento incremental e recuperação automática.

## 🚀 Como Usar

### Sintaxe Básica

```bash
python processar_experimento.py --prompt <arquivo.csv> --rag
python processar_experimento.py --prompt <arquivo.csv> --no-rag
```

### Exemplos Práticos

#### 1. Processar Prompt 3 COM RAG
```bash
python processar_experimento.py --prompt redacoes_prompt_3.csv --rag
```

#### 2. Processar Prompt 3 SEM RAG (Baseline)
```bash
python processar_experimento.py --prompt redacoes_prompt_3.csv --no-rag
```

#### 3. Processar Prompt 6 COM RAG
```bash
python processar_experimento.py --prompt redacoes_prompt_6.csv --rag
```

#### 4. Processar Prompt 6 SEM RAG (Baseline)
```bash
python processar_experimento.py --prompt redacoes_prompt_6.csv --no-rag
```

## ✨ Funcionalidades

### 1. 💾 Salvamento Incremental

Cada redação é salva **imediatamente após ser processada**. Isso significa:

- ✅ Se processar 13 redações e o programa falhar, as 13 ficam salvas
- ✅ Não perde progresso em caso de erro
- ✅ Pode parar e retomar a qualquer momento

**Exemplo de saída:**
```
📄 Processando Redação 1/20
✅ Avaliação concluída!
💾 Progresso salvo: 1 redações em resultados_prompt3_rag.json
📊 Progresso: 1/20 redações processadas

📄 Processando Redação 2/20
✅ Avaliação concluída!
💾 Progresso salvo: 2 redações em resultados_prompt3_rag.json
📊 Progresso: 2/20 redações processadas
...
```

### 2. 🔄 Recuperação Automática

Se o processamento for interrompido, o script **continua de onde parou**:

**Primeira execução:**
```bash
python processar_experimento.py --prompt redacoes_prompt_3.csv --rag
# Processou 13 redações... depois quebrou
```

**Segunda execução (retoma automaticamente):**
```bash
python processar_experimento.py --prompt redacoes_prompt_3.csv --rag
📥 13 resultados anteriores carregados
🔄 RECUPERAÇÃO DETECTADA: 13/20 redações já processadas
   Continuando de onde parou...
⏭️  Redação 1/20 - JÁ PROCESSADA (pulando)
⏭️  Redação 2/20 - JÁ PROCESSADA (pulando)
...
⏭️  Redação 13/20 - JÁ PROCESSADA (pulando)
📄 Processando Redação 14/20  # Começa daqui!
```

### 3. 🛡️ Tratamento de Erros

O script trata alucinações do LLM e outros erros:

- ✅ Remove prefixos como `'''json` ou ` ```json` do JSON
- ✅ Registra erros detalhadamente no resultado
- ✅ Continua processando as próximas redações
- ✅ Marca redações com erro como `"status": "erro"`

**Exemplo de erro registrado:**
```json
{
  "redacao_index": 12,
  "prompt_id": 3,
  "modo_avaliacao": "com_rag",
  "nota_real": 720,
  "erro": "Falha ao parsear JSON: Expecting value: line 1 column 1 (char 0)",
  "erro_tipo": "ValueError",
  "timestamp": "2025-12-08T15:30:45.123456",
  "status": "erro"
}
```

## 📂 Estrutura de Saída

Os resultados são salvos em `resultados_experimento/`:

```
resultados_experimento/
├── resultados_prompt3_rag.json       # Prompt 3 COM RAG
├── resultados_prompt3_baseline.json  # Prompt 3 SEM RAG
├── resultados_prompt6_rag.json       # Prompt 6 COM RAG
└── resultados_prompt6_baseline.json  # Prompt 6 SEM RAG
```

### Estrutura de Cada Resultado

```json
[
  {
    "redacao_index": 0,
    "prompt_id": 3,
    "tema": "Ciência, tecnologia e superação dos limites humanos",
    "modo_avaliacao": "com_rag",
    "nota_real": 720,
    "competencias_reais": [120, 160, 160, 160, 120],
    "avaliacao_sistema": {
      "competencias": {
        "competencia_1": { "nota": 120, "justificativa": "..." },
        "competencia_2": { "nota": 160, "justificativa": "..." },
        "competencia_3": { "nota": 160, "justificativa": "..." },
        "competencia_4": { "nota": 160, "justificativa": "..." },
        "competencia_5": { "nota": 120, "justificativa": "..." }
      },
      "nota_final": 720,
      "resumo_executivo": "..."
    },
    "timestamp": "2025-12-08T15:30:45.123456",
    "status": "sucesso"
  },
  {
    "redacao_index": 1,
    "prompt_id": 3,
    "tema": "Ciência, tecnologia e superação dos limites humanos",
    "modo_avaliacao": "com_rag",
    "nota_real": 560,
    "competencias_reais": [120, 80, 120, 120, 120],
    "avaliacao_sistema": { ... },
    "timestamp": "2025-12-08T15:35:12.789012",
    "status": "sucesso"
  }
]
```

## 🎓 Processar os 4 Experimentos

Execute os 4 comandos em sequência:

```bash
# Experimento 1: Prompt 3 com RAG
python processar_experimento.py --prompt redacoes_prompt_3.csv --rag

# Experimento 2: Prompt 3 sem RAG
python processar_experimento.py --prompt redacoes_prompt_3.csv --no-rag

# Experimento 3: Prompt 6 com RAG
python processar_experimento.py --prompt redacoes_prompt_6.csv --rag

# Experimento 4: Prompt 6 sem RAG
python processar_experimento.py --prompt redacoes_prompt_6.csv --no-rag
```

## ⚠️ Casos de Uso Importantes

### Caso 1: Interrupção Manual (Ctrl+C)

```bash
python processar_experimento.py --prompt redacoes_prompt_3.csv --rag
# Pressiona Ctrl+C depois de 10 redações

⚠️  INTERROMPIDO PELO USUÁRIO
💾 Resultados parciais foram salvos e podem ser retomados
```

**Solução:** Execute o mesmo comando novamente para continuar.

### Caso 2: Erro do LLM (JSON mal formatado)

```bash
📄 Processando Redação 13/20
❌ Erro na avaliação: Falha ao parsear JSON: ...
💾 Progresso salvo: 13 redações em resultados_prompt3_rag.json
📊 Progresso: 13/20 redações processadas

# Continua processando a próxima (14/20)
```

**Solução:** O script continua automaticamente. Redação com erro fica marcada no JSON.

### Caso 3: Quero Reprocessar Tudo

Se quiser começar do zero, **delete o arquivo de saída**:

```bash
rm resultados_experimento/resultados_prompt3_rag.json
python processar_experimento.py --prompt redacoes_prompt_3.csv --rag
```

## 📊 Relatório Final

Ao final, você verá um relatório completo:

```
================================================================================
✅ PROCESSAMENTO CONCLUÍDO!
================================================================================
📁 Arquivo: redacoes_prompt_3.csv
🎯 Prompt: 3
⚙️  Modo: RAG
📊 Total: 20/20 redações
✅ Sucessos: 19
❌ Erros: 1
💾 Resultados salvos em: resultados_experimento/resultados_prompt3_rag.json
================================================================================
```

## 🧪 Modo Teste (Debug)

Para testar com apenas 1 redação:

```bash
# Testar redação índice 0 COM RAG
python processar_experimento.py --test 0

# Testar redação índice 5 SEM RAG
python processar_experimento.py --test-no-rag 5
```

## 🔍 Verificar Resultados

Para ver quantas redações foram processadas:

```bash
# Linux/Mac
jq 'length' resultados_experimento/resultados_prompt3_rag.json

# Python
python -c "import json; print(len(json.load(open('resultados_experimento/resultados_prompt3_rag.json'))))"
```

Para ver apenas sucessos:

```bash
# Python
python -c "import json; r=json.load(open('resultados_experimento/resultados_prompt3_rag.json')); print(sum(1 for x in r if x['status']=='sucesso'))"
```

## ❓ FAQ

### P: O que acontece se eu executar o mesmo comando duas vezes?

**R:** Na segunda vez, ele detecta que já processou e pula todas as redações já feitas. É seguro executar múltiplas vezes.

### P: Perdi o arquivo de resultados, posso recuperar?

**R:** Não. Os resultados só existem no arquivo JSON. Se deletar, precisa reprocessar.

### P: Posso processar dois experimentos ao mesmo tempo?

**R:** Sim, desde que sejam arquivos diferentes ou modos diferentes (ex: prompt3 RAG e prompt6 baseline).

### P: Como ver o progresso em tempo real?

**R:** O script mostra no terminal:
```
📊 Progresso: 13/20 redações processadas
```

### P: Quanto tempo demora?

**R:** ~2-3 minutos por redação. Para 20 redações: ~40-60 minutos.

## 🆘 Problemas Comuns

### Erro: "Arquivo não encontrado"

```bash
❌ Erro: Arquivo não encontrado: redacoes_prompt_3.csv
```

**Solução:** Certifique-se de estar no diretório correto:
```bash
cd /caminho/para/avaliador-automatico-de-redacoes
ls redacoes_prompt_*.csv
```

### Erro: "API Key não configurada"

```bash
⚠️  ATENÇÃO: API Key do Google Gemini não encontrada!
```

**Solução:**
```bash
# Linux/Mac
export GEMINI_API_KEY="sua-chave-aqui"

# Windows PowerShell
$env:GEMINI_API_KEY="sua-chave-aqui"
```

## 📚 Referências

- **Script principal:** `processar_experimento.py`
- **Configuração da banca:** `avaliacao_automatica/crew.py`
- **README geral:** `README.md`

