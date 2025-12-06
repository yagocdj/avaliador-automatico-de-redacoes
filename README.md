# 🎓 Banca Examinadora Digital - Avaliação Automatizada de Redações ENEM

Sistema multi-agente baseado em IA para avaliação automatizada de redações do ENEM utilizando Google Gemini e RAG (Retrieval-Augmented Generation).

## 📋 Sobre o Projeto

Este sistema avalia redações do ENEM nas **5 competências** usando:
- **6 agentes especializados** (1 para cada competência + 1 consolidador)
- **Google Gemini 3** como LLM
- **RAG** com manuais oficiais do ENEM (contexto injection)
- **Experimento comparativo**: RAG vs Baseline

### Dados do Experimento

**40 redações reais** divididas em 2 temas:
- **Prompt 3**: "Ciência, tecnologia e superação dos limites humanos" (20 redações)
- **Prompt 6**: "Preservação da Amazônia: Desafio brasileiro ou internacional?" (20 redações)

**2 modos de avaliação**:
- **RAG**: Com manuais oficiais do ENEM (contexto completo)
- **Baseline**: Sem manuais (conhecimento prévio do LLM)

**Total**: 80 avaliações (40 redações × 2 modos)

---

## 🚀 Início Rápido (3 passos)

### 1️⃣ Instalar Dependências

```bash
pip install -r requirements.txt
```

### 2️⃣ Configurar API Key do Google Gemini

**Obtenha sua chave em**: https://makersuite.google.com/app/apikey

**Configure a variável de ambiente:**

```powershell
# Windows PowerShell
$env:GEMINI_API_KEY="sua-chave-aqui"
```

```bash
# Linux/Mac
export GEMINI_API_KEY="sua-chave-aqui"
```

**Ou crie um arquivo `.env` na raiz:**
```
GEMINI_API_KEY=sua-chave-aqui
```

### 3️⃣ Executar

**Verificar configuração (recomendado):**
```bash
python verificar_configuracao.py
```

**Testar com 1 redação (~2 minutos):**
```bash
python processar_experimento.py --teste
```

**Executar experimento completo (~30-60 minutos):**
```bash
python processar_experimento.py
```

---

## 📂 Estrutura do Projeto

```
├── avaliacao_automatica/       # Core do sistema
│   ├── config/
│   │   ├── agents.yaml         # Definição dos 6 agentes
│   │   └── tasks.yaml          # Tarefas de avaliação (5 competências)
│   ├── crew.py                 # Orquestração (Gemini configurado aqui)
│   ├── main.py                 # Script principal
│   └── manual_loader.py        # Carregador de manuais (RAG)
│
├── rag_context/                # Manuais do ENEM (PDFs)
│   ├── Competencia_1.pdf       # Gramática
│   ├── Competencia_2.pdf       # Tema e Estrutura
│   ├── Competencia_3.pdf       # Argumentação
│   ├── Competencia_4.pdf       # Coesão
│   └── Competencia_5.pdf       # Proposta de Intervenção
│
├── exemplo_uso.py              # Exemplo simples
├── exemplo_output.json         # Exemplo de resultado
├── requirements.txt            # Dependências
├── textos_apoio.py             # Temas e textos de apoio (estilo ENEM)
├── processar_experimento.py   # Script principal do experimento
├── verificar_configuracao.py  # Verifica se está tudo OK
│
├── redacoes_prompt_3.csv       # 20 redações do tema 3
├── redacoes_prompt_6.csv       # 20 redações do tema 6
│
└── analise_redacoes.ipynb      # Notebook de análise dos dados
```

---

## 🎯 Como Funciona

### Arquitetura Multi-Agente

```
┌─────────────────────────────────────────────────────────┐
│                   BANCA EXAMINADORA                     │
└─────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┴──────────────────┐
        │                                      │
┌───────▼────────┐                   ┌────────▼───────┐
│  MODO RAG      │                   │  MODO BASELINE │
│  (com manuais) │                   │  (sem manuais) │
└───────┬────────┘                   └────────┬───────┘
        │                                      │
        └──────────────────┬──────────────────┘
                           │
        ┌──────────────────┴──────────────────┐
        │         PROCESSO SEQUENCIAL          │
        │                                      │
        │  1. Agente Gramática (Comp. I)      │
        │  2. Agente Estrutura (Comp. II)     │
        │  3. Agente Argumentação (Comp. III) │
        │  4. Agente Coesão (Comp. IV)        │
        │  5. Agente Proposta (Comp. V)       │
        │  6. Presidente (Consolidador)       │
        │                                      │
        └──────────────────┬──────────────────┘
                           │
                   ┌───────▼────────┐
                   │  Resultado JSON │
                   └────────────────┘
```

### Inputs de Cada Avaliação

Cada agente recebe:
1. **Redação**: Texto completo do estudante
2. **Tema**: Ex: "Ciência, tecnologia e superação dos limites humanos"
3. **Textos de apoio**: Contexto fornecido (estilo ENEM)
4. **Manual** (apenas modo RAG): Critérios oficiais da competência

### Outputs

**Por competência** (JSON):
```json
{
  "competencia": 1,
  "nota": 160,
  "justificativa": "O texto demonstra bom domínio...",
  "desvios_encontrados": ["lista de desvios"]
}
```

**Notas possíveis**: 0, 40, 80, 120, 160, 200  
**Nota final**: 0 a 1000 (soma das 5 competências)

---

## 📊 Resultados Gerados

Após executar `processar_experimento.py`, serão criados 4 arquivos JSON:

```
resultados_experimento/
├── resultados_prompt3_rag.json       # 20 avaliações COM manuais
├── resultados_prompt3_baseline.json  # 20 avaliações SEM manuais
├── resultados_prompt6_rag.json       # 20 avaliações COM manuais
└── resultados_prompt6_baseline.json  # 20 avaliações SEM manuais
```

### Estrutura de Cada Resultado

```json
[
  {
    "prompt_id": 3,
    "tema": "Ciência, tecnologia e superação dos limites humanos",
    "modo_avaliacao": "com_rag",
    "timestamp": "2025-12-05T...",
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
    "status": "sucesso"
  }
]
```

---

## 🔧 Configuração Avançada

### Alterar Modelo do Gemini

Edite `avaliacao_automatica/crew.py` (linha ~32):

```python
llm = LLM(
    model="gemini/gemini-3",  # Modelo atual
    temperature=0.1
)
```

**Modelos disponíveis:**
- `gemini/gemini-3` - Atual
- `gemini/gemini-1.5-flash` - Rápido e eficiente
- `gemini/gemini-1.5-pro` - Mais poderoso

### Alterar Temperature

```python
temperature=0.1  # Mais consistente (recomendado para avaliação)
temperature=0.7  # Mais criativo
```

---

## 🧪 Script de Verificação

O script `verificar_configuracao.py` verifica:

✅ **Arquivos necessários** (CSVs, scripts, configs)  
✅ **Estrutura dos CSVs** (colunas corretas, dados válidos)  
✅ **tasks.yaml** (configuração correta)  
✅ **Textos de apoio** (temas corretos dos prompts 3 e 6)  
✅ **Dependências Python** (crewai, pandas, etc.)  
✅ **API Key do Gemini** (configurada corretamente)

**Executar:**
```bash
python verificar_configuracao.py
```

**Saída esperada:**
```
✅ Arquivos
✅ Estrutura CSVs
✅ tasks.yaml
✅ Textos de Apoio
✅ Dependências
✅ Gemini API Key

🎉 TUDO PRONTO! Você pode executar o experimento.
```

---

## 📖 Exemplo de Uso Simples

```python
from avaliacao_automatica.crew import BancaExaminadora
from textos_apoio import obter_textos_apoio

# Obter tema e textos de apoio
tema, textos_apoio = obter_textos_apoio(3)  # Prompt 3

# Criar banca
banca = BancaExaminadora()

# Avaliar redação
resultado = banca.avaliar_redacao(
    redacao="Texto da redação aqui...",
    tema=tema,
    textos_apoio=textos_apoio,
    modo_rag=True  # True = com manuais, False = baseline
)

print(resultado)
```

Veja mais em: `exemplo_uso.py`

---

## 🔍 Troubleshooting

### ❌ "API Key não encontrada"

**Problema:** Variável de ambiente não configurada

**Solução:**
```bash
# Verificar se está configurada:
echo $env:GEMINI_API_KEY  # Windows PowerShell
echo $GEMINI_API_KEY      # Linux/Mac

# Se não aparecer nada:
$env:GEMINI_API_KEY="sua-chave-aqui"  # Windows
export GEMINI_API_KEY="sua-chave-aqui"  # Linux/Mac
```

### ❌ "Module 'crewai' not found"

**Problema:** Dependências não instaladas

**Solução:**
```bash
pip install -r requirements.txt
```

### ❌ "Rate Limit Exceeded"

**Problema:** Muitas requisições simultâneas

**Solução:**
- Gemini gratuito: 15 requisições/minuto
- O script já respeita limites automaticamente
- Aguarde alguns segundos entre tentativas

### ❌ "Invalid API Key"

**Problema:** Chave incorreta ou expirada

**Solução:**
1. Verifique se copiou a chave corretamente (sem espaços)
2. Gere uma nova em: https://makersuite.google.com/app/apikey

### ❌ Arquivo CSV não encontrado

**Problema:** Executando do diretório errado

**Solução:**
```bash
# Certifique-se de estar na raiz do projeto:
cd C:\Users\SamuelDeMoraisLima\Documents\Mestrado\avaliacao-automatizada-de-redacoes

# Verificar arquivos:
dir  # Windows
ls   # Linux/Mac
```

---

## 💰 Custos

### Google Gemini (Tier Gratuito)

- **Limite gratuito**: 15 requisições/minuto
- **Total de requisições**: ~240 (40 redações × 6 agentes)
- **Tempo estimado**: 30-60 minutos (respeitando rate limit)
- **Custo**: **GRATUITO** dentro do tier

**Veja preços atualizados**: https://ai.google.dev/pricing

---

## 📝 Dados dos Prompts

### Prompt 3: Ciência, tecnologia e superação dos limites humanos
- **Redações**: 20
- **Textos de apoio**: 3 textos (Revolução tecnológica, IA/biotech, ética)
- **Arquivo**: `redacoes_prompt_3.csv`

### Prompt 6: Preservação da Amazônia: Desafio brasileiro ou internacional?
- **Redações**: 20
- **Textos de apoio**: 4 textos (Biodiversidade, INPE, soberania, sustentabilidade)
- **Arquivo**: `redacoes_prompt_6.csv`

---

## 🎓 Competências Avaliadas

| Competência | Descrição | Agente |
|-------------|-----------|--------|
| **I** | Domínio da norma culta da língua portuguesa | Agente Gramática |
| **II** | Compreensão do tema e estrutura dissertativa | Agente Estrutura |
| **III** | Seleção e organização de argumentos | Agente Argumentação |
| **IV** | Mecanismos linguísticos (coesão) | Agente Coesão |
| **V** | Proposta de intervenção | Agente Proposta |

**Consolidação**: Presidente da Banca (agrega tudo)

---

## 📚 Tecnologias

- **Python** 3.8+
- **CrewAI** - Framework multi-agente
- **Google Gemini 3** - LLM
- **Pandas** - Manipulação de dados
- **PyPDF** - Leitura dos manuais

---

## 🤝 Contribuindo

Para modificar ou estender o projeto:

1. **Adicionar novos agentes**: Edite `avaliacao_automatica/config/agents.yaml`
2. **Modificar critérios**: Edite `avaliacao_automatica/config/tasks.yaml`
3. **Trocar LLM**: Edite `avaliacao_automatica/crew.py`
4. **Adicionar prompts**: Edite `textos_apoio.py` e adicione CSVs

---

## 📄 Licença

Este é um projeto acadêmico para fins de pesquisa em avaliação automatizada de redações.

---

## 🚀 Comandos Rápidos

```bash
# 1. Verificar tudo
python verificar_configuracao.py

# 2. Testar (1 redação)
python processar_experimento.py --teste

# 3. Experimento completo (40 redações)
python processar_experimento.py

# 4. Analisar resultados
jupyter notebook analise_redacoes.ipynb
```

---

**Desenvolvido para o Mestrado em Avaliação Automatizada de Redações**  
**Última atualização**: Dezembro 2025  
**Versão**: 3.0
