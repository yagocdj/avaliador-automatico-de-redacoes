"""
SCRIPT DE PROCESSAMENTO DO EXPERIMENTO
Processa as redações dos prompts 3 e 6 nos modos RAG e Baseline
Configurado para usar Google Gemini
"""

import pandas as pd
import json
import ast
import os
from pathlib import Path
from avaliacao_automatica.crew import BancaExaminadora
from textos_apoio import obter_textos_apoio


def carregar_csv(caminho_csv: str) -> pd.DataFrame:
    """Carrega o CSV de redações"""
    print(f"📂 Carregando {caminho_csv}...")
    df = pd.read_csv(caminho_csv)
    print(f"   ✓ {len(df)} redações carregadas")
    return df


def processar_essay(essay_str: str) -> str:
    """
    Converte o campo 'essay' de string para texto limpo
    O campo vem como: "['parágrafo 1', 'parágrafo 2', ...]"
    """
    try:
        # Converte a string para lista Python
        paragrafos = ast.literal_eval(essay_str)
        # Junta os parágrafos com quebra de linha dupla
        return "\n\n".join(paragrafos)
    except Exception:
        return essay_str


def avaliar_redacao_completa(
    banca: BancaExaminadora,
    redacao: str,
    tema: str,
    textos_apoio: str,
    prompt_id: int,
    modo_rag: bool,
    nota_real: int,
    competencias_reais: list
) -> dict:
    """
    Avalia uma redação e retorna o resultado estruturado
    """
    modo_nome = "RAG" if modo_rag else "BASELINE"
    print(f"\n{'='*80}")
    print(f"🎓 Avaliando - Prompt {prompt_id} - Modo: {modo_nome}")
    print(f"   Tema: {tema}")
    print(f"   Nota Real: {nota_real}")
    print(f"{'='*80}")
    
    try:
        resultado = banca.avaliar_redacao( # type: ignore
            redacao=redacao,
            tema=tema,
            textos_apoio=textos_apoio,
            modo_rag=modo_rag
        )
        
        # Estruturar resultado
        resultado_estruturado = {
            "prompt_id": prompt_id,
            "tema": tema,
            "modo_avaliacao": "com_rag" if modo_rag else "baseline",
            "nota_real": nota_real,
            "competencias_reais": competencias_reais,
            "avaliacao_sistema": resultado,
            "status": "sucesso"
        }
        
        print("✅ Avaliação concluída!")
        return resultado_estruturado
        
    except Exception as e:
        print(f"❌ Erro na avaliação: {e}")
        return {
            "prompt_id": prompt_id,
            "tema": tema,
            "modo_avaliacao": "com_rag" if modo_rag else "baseline",
            "nota_real": nota_real,
            "erro": str(e),
            "status": "erro"
        }


def processar_prompt(
    csv_path: str,
    prompt_id: int,
    modo_rag: bool,
    output_dir: Path
):
    """
    Processa todas as redações de um prompt em um modo específico
    """
    modo_nome = "rag" if modo_rag else "baseline"
    print(f"\n{'#'*80}")
    print(f"# PROCESSANDO PROMPT {prompt_id} - MODO: {modo_nome.upper()}")
    print(f"{'#'*80}")
    
    # Carregar CSV
    df = carregar_csv(csv_path)
    
    # Obter tema e textos de apoio
    tema, textos_apoio = obter_textos_apoio(prompt_id)
    print(f"\n📝 Tema: {tema}")
    print(f"📋 Textos de apoio carregados: {len(textos_apoio)} caracteres")
    
    # Criar banca
    banca = BancaExaminadora()
    
    # Resultados
    resultados = []
    
    # Processar cada redação
    for idx, row in df.iterrows():
        print(f"\n--- Redação {idx + 1}/{len(df)} ---")
        
        # Extrair dados
        redacao_texto = processar_essay(row['essay'])
        nota_real = row['score']
        
        # Converter competencias de string para lista
        try:
            competencias_reais = ast.literal_eval(row['competence'])
        except Exception:
            competencias_reais = []
        
        # Avaliar
        resultado = avaliar_redacao_completa(
            banca=banca,
            redacao=redacao_texto,
            tema=tema,
            textos_apoio=textos_apoio,
            prompt_id=prompt_id,
            modo_rag=modo_rag,
            nota_real=nota_real,
            competencias_reais=competencias_reais
        )
        
        resultados.append(resultado)
    
    # Salvar resultados
    output_file = output_dir / f"resultados_prompt{prompt_id}_{modo_nome}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*80}")
    print(f"✅ Prompt {prompt_id} ({modo_nome.upper()}) processado!")
    print(f"   Resultados salvos em: {output_file}")
    print(f"{'='*80}")
    
    return resultados


def verificar_api_key_gemini():
    """Verifica se a API Key do Gemini está configurada"""
    if "GEMINI_API_KEY" not in os.environ and "GOOGLE_API_KEY" not in os.environ:
        print("\n" + "="*80)
        print("⚠️  ATENÇÃO: API Key do Google Gemini não encontrada!")
        print("="*80)
        print("\nConfigure uma das seguintes variáveis de ambiente:")
        print("  - GEMINI_API_KEY")
        print("  - GOOGLE_API_KEY")
        print("\nExemplo (Windows PowerShell):")
        print('  $env:GEMINI_API_KEY="sua-chave-aqui"')
        print("\nExemplo (Linux/Mac):")
        print('  export GEMINI_API_KEY="sua-chave-aqui"')
        print("\nOu crie um arquivo .env com:")
        print('  GEMINI_API_KEY=sua-chave-aqui')
        print("="*80)
        raise EnvironmentError("API Key do Gemini não configurada")
    
    print("✅ API Key do Gemini encontrada")


def processar_experimento_completo():
    """
    Processa o experimento completo:
    - Prompt 3: RAG e Baseline
    - Prompt 6: RAG e Baseline
    """
    print("\n" + "="*80)
    print("🚀 INICIANDO EXPERIMENTO COMPLETO")
    print("="*80)
    
    # Verificar API Key
    verificar_api_key_gemini()
    
    # Criar diretório de resultados
    output_dir = Path("resultados_experimento")
    output_dir.mkdir(exist_ok=True)
    
    # Caminhos dos CSVs
    csv_prompt3 = "redacoes_prompt_3.csv"
    csv_prompt6 = "redacoes_prompt_6.csv"
    
    # Verificar se os arquivos existem
    if not Path(csv_prompt3).exists():
        print(f"❌ Arquivo não encontrado: {csv_prompt3}")
        return
    
    if not Path(csv_prompt6).exists():
        print(f"❌ Arquivo não encontrado: {csv_prompt6}")
        return
    
    # Processar Prompt 3
    print("\n" + "#"*80)
    print("# FASE 1: PROMPT 3")
    print("#"*80)
    
    # Prompt 3 - RAG
    processar_prompt(csv_prompt3, 3, modo_rag=True, output_dir=output_dir)
    
    # Prompt 3 - Baseline
    processar_prompt(csv_prompt3, 3, modo_rag=False, output_dir=output_dir)
    
    # Processar Prompt 6
    print("\n" + "#"*80)
    print("# FASE 2: PROMPT 6")
    print("#"*80)
    
    # Prompt 6 - RAG
    processar_prompt(csv_prompt6, 6, modo_rag=True, output_dir=output_dir)
    
    # Prompt 6 - Baseline
    processar_prompt(csv_prompt6, 6, modo_rag=False, output_dir=output_dir)
    
    print("\n" + "="*80)
    print("🎉 EXPERIMENTO COMPLETO FINALIZADO!")
    print("="*80)
    print(f"Resultados salvos em: {output_dir.absolute()}")


def processar_teste_individual():
    """
    Processa apenas UMA redação de teste COM RAG (para debug)
    """
    print("\n🧪 MODO TESTE COM RAG - Uma redação do Prompt 3")
    
    # Verificar API Key do Gemini
    verificar_api_key_gemini()
    
    # Carregar apenas a primeira redação do prompt 3
    df = pd.read_csv("redacoes_prompt_3.csv")
    row = df.iloc[0]
    
    redacao_texto = processar_essay(row['essay'])
    
    # Obter tema e textos de apoio do prompt 3
    tema, textos_apoio = obter_textos_apoio(3)
    
    print(f"\nTema: {tema}")
    print(f"Tamanho da redação: {len(redacao_texto)} caracteres")
    print(f"Tamanho textos de apoio: {len(textos_apoio)} caracteres")
    print(f"Primeiros 200 caracteres da redação:\n{redacao_texto[:200]}...")
    
    # Avaliar COM RAG
    banca = BancaExaminadora()
    resultado = banca.avaliar_redacao( # type: ignore
        redacao=redacao_texto,
        tema=tema,
        textos_apoio=textos_apoio,
        modo_rag=True
    )
    
    print("\n✅ Teste COM RAG concluído!")
    print(f"Resultado:\n{resultado}")


def processar_teste_individual_baseline():
    """
    Processa apenas UMA redação de teste SEM RAG - Baseline (para debug)
    """
    print("\n🧪 MODO TESTE SEM RAG (BASELINE) - Uma redação do Prompt 3")
    
    # Verificar API Key do Gemini
    verificar_api_key_gemini()
    
    # Carregar apenas a primeira redação do prompt 3
    df = pd.read_csv("redacoes_prompt_3.csv")
    row = df.iloc[0]
    
    redacao_texto = processar_essay(row['essay'])
    
    # Obter tema e textos de apoio do prompt 3
    tema, textos_apoio = obter_textos_apoio(3)
    
    print(f"\nTema: {tema}")
    print(f"Tamanho da redação: {len(redacao_texto)} caracteres")
    print(f"Tamanho textos de apoio: {len(textos_apoio)} caracteres")
    print(f"Primeiros 200 caracteres da redação:\n{redacao_texto[:200]}...")
    
    # Avaliar SEM RAG (Baseline)
    banca = BancaExaminadora()
    resultado = banca.avaliar_redacao( # type: ignore
        redacao=redacao_texto,
        tema=tema,
        textos_apoio=textos_apoio,
        modo_rag=False  # SEM os manuais (baseline)
    )
    
    print("\n✅ Teste SEM RAG (Baseline) concluído!")
    print(f"Resultado:\n{resultado}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Modo teste COM RAG: processa apenas uma redação
        processar_teste_individual()
    elif len(sys.argv) > 1 and sys.argv[1] == "--test-no-rag":
        # Modo teste SEM RAG (Baseline): processa apenas uma redação
        processar_teste_individual_baseline()
    else:
        # Modo completo: processa todas as redações
        processar_experimento_completo()

