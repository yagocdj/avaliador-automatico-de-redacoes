"""
SCRIPT DE PROCESSAMENTO DO EXPERIMENTO
Processa as redações dos prompts 3 e 6 nos modos RAG e Baseline
Configurado para usar Google Gemini

MODO DE USO:
    python processar_experimento.py --prompt redacoes_prompt_3.csv --rag
    python processar_experimento.py --prompt redacoes_prompt_3.csv --no-rag
    python processar_experimento.py --prompt redacoes_prompt_6.csv --rag
    python processar_experimento.py --prompt redacoes_prompt_6.csv --no-rag
    
FEATURES:
    - Salvamento incremental: cada redação processada é salva imediatamente
    - Recuperação automática: continua de onde parou em caso de interrupção
    - Tratamento de erros: alucinações do LLM são tratadas e registradas
"""

import pandas as pd
import json
import ast
import os
import re
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from avaliacao_automatica.crew import BancaExaminadora
from textos_apoio import obter_textos_apoio


def extrair_prompt_id_do_arquivo(nome_arquivo: str) -> int:
    """
    Extrai o ID do prompt do nome do arquivo
    Ex: 'redacoes_prompt_3.csv' -> 3
    """
    match = re.search(r'prompt[_\s]*(\d+)', nome_arquivo, re.IGNORECASE)
    if match:
        return int(match.group(1))
    raise ValueError(f"Não foi possível extrair o prompt_id do arquivo: {nome_arquivo}")


def carregar_csv(caminho_csv: str) -> pd.DataFrame:
    """Carrega o CSV de redações"""
    print(f"📂 Carregando {caminho_csv}...")
    df = pd.read_csv(caminho_csv)
    print(f"   ✓ {len(df)} redações carregadas")
    return df


def gerar_nome_arquivo_resultado(csv_path: str, modo_rag: bool) -> str:
    """
    Gera o nome do arquivo de resultado baseado no CSV e modo
    Ex: redacoes_prompt_3.csv + RAG -> resultados_prompt3_rag.json
    """
    prompt_id = extrair_prompt_id_do_arquivo(csv_path)
    modo_nome = "rag" if modo_rag else "baseline"
    return f"resultados_prompt{prompt_id}_{modo_nome}.json"


def carregar_resultados_existentes(output_path: Path) -> List[Dict[str, Any]]:
    """
    Carrega resultados já processados se existirem
    """
    if output_path.exists():
        try:
            with open(output_path, 'r', encoding='utf-8') as f:
                resultados = json.load(f)
            print(f"📥 {len(resultados)} resultados anteriores carregados de {output_path.name}")
            return resultados
        except Exception as e:
            print(f"⚠️  Erro ao carregar resultados anteriores: {e}")
            return []
    return []


def salvar_resultados_incrementais(resultados: List[Dict[str, Any]], output_path: Path):
    """
    Salva os resultados incrementalmente (após cada redação processada)
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(resultados, f, ensure_ascii=False, indent=2)
        print(f"💾 Progresso salvo: {len(resultados)} redações em {output_path.name}")
    except Exception as e:
        print(f"❌ Erro ao salvar resultados: {e}")


def limpar_json_alucinado(texto: str) -> str:
    """
    Limpa possíveis alucinações do LLM no JSON
    Remove prefixos como ```json, ```JSON, etc.
    """
    # Remove blocos de código markdown
    texto = re.sub(r'^```[a-zA-Z]*\s*', '', texto.strip())
    texto = re.sub(r'```\s*$', '', texto.strip())
    # Remove aspas triplas no início/fim
    texto = re.sub(r'^[\'\"]{3}', '', texto.strip())
    texto = re.sub(r'[\'\"]{3}$', '', texto.strip())
    return texto.strip()


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
    competencias_reais: list,
    idx_redacao: int
) -> dict:
    """
    Avalia uma redação e retorna o resultado estruturado
    Inclui tratamento de erros e parsing de JSON
    """
    modo_nome = "RAG" if modo_rag else "BASELINE"
    print(f"\n{'='*80}")
    print(f"🎓 Redação {idx_redacao} - Prompt {prompt_id} - Modo: {modo_nome}")
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
        
        # VERIFICAR SE RESULTADO É NULL/NONE
        if resultado is None:
            print(f"⚠️  AVISO: Resultado da avaliação veio NULL/None!")
            raise ValueError("Resultado da avaliação é None - possível erro no CrewAI")
        
        # Tentar processar o resultado se vier como string
        if isinstance(resultado, str):
            resultado_limpo = limpar_json_alucinado(resultado)
            try:
                resultado = json.loads(resultado_limpo)
            except json.JSONDecodeError as e:
                print(f"⚠️  JSON mal formatado detectado. Tentando corrigir...")
                print(f"   Primeiros 200 caracteres: {resultado[:200]}")
                # Salvar o erro para debug
                erro_info = {
                    "erro_tipo": "json_decode",
                    "mensagem": str(e),
                    "resultado_bruto": resultado[:500]  # Primeiros 500 chars
                }
                raise ValueError(f"Falha ao parsear JSON: {e}") from e
        
        # VERIFICAR SE RESULTADO TEM AS CHAVES ESPERADAS
        if not isinstance(resultado, dict):
            print(f"⚠️  AVISO: Resultado não é um dicionário! Tipo: {type(resultado)}")
            print(f"   Conteúdo: {str(resultado)[:300]}")
            raise ValueError(f"Resultado não é um dict válido. Tipo: {type(resultado)}")
        
        # LOG de debug para ver o que está vindo
        print(f"✓ Resultado recebido com {len(resultado)} chaves: {list(resultado.keys())}")
        
        # Estruturar resultado
        resultado_estruturado = {
            "redacao_index": idx_redacao,
            "prompt_id": prompt_id,
            "tema": tema,
            "modo_avaliacao": "com_rag" if modo_rag else "baseline",
            "nota_real": nota_real,
            "competencias_reais": competencias_reais,
            "avaliacao_sistema": resultado,
            "timestamp": datetime.now().isoformat(),
            "status": "sucesso"
        }
        
        print("✅ Avaliação concluída!")
        return resultado_estruturado
        
    except Exception as e:
        print(f"❌ Erro na avaliação: {e}")
        # Registrar erro detalhado
        resultado_com_erro = {
            "redacao_index": idx_redacao,
            "prompt_id": prompt_id,
            "tema": tema,
            "modo_avaliacao": "com_rag" if modo_rag else "baseline",
            "nota_real": nota_real,
            "competencias_reais": competencias_reais,
            "erro": str(e),
            "erro_tipo": type(e).__name__,
            "timestamp": datetime.now().isoformat(),
            "status": "erro"
        }
        return resultado_com_erro


def processar_experimento(
    csv_path: str,
    modo_rag: bool,
    output_dir: Path
):
    """
    Processa todas as redações de um CSV em um modo específico (RAG ou Baseline)
    
    Features:
    - Salvamento incremental: cada redação é salva após ser processada
    - Recuperação: se já existem resultados, continua de onde parou
    - Tratamento de erros: não para se uma redação falhar
    
    Args:
        csv_path: Caminho para o CSV com as redações
        modo_rag: True para RAG, False para Baseline
        output_dir: Diretório onde salvar os resultados
    """
    # Extrair prompt_id do nome do arquivo
    prompt_id = extrair_prompt_id_do_arquivo(csv_path)
    modo_nome = "RAG" if modo_rag else "BASELINE"
    
    print(f"\n{'#'*80}")
    print(f"# PROCESSANDO: {csv_path}")
    print(f"# PROMPT: {prompt_id} | MODO: {modo_nome}")
    print(f"{'#'*80}")
    
    # Carregar CSV
    df = carregar_csv(csv_path)
    total_redacoes = len(df)
    
    # Obter tema e textos de apoio
    tema, textos_apoio = obter_textos_apoio(prompt_id)
    print(f"\n📝 Tema: {tema}")
    print(f"📋 Textos de apoio: {len(textos_apoio)} caracteres")
    
    # Definir caminho do arquivo de saída
    nome_arquivo_saida = gerar_nome_arquivo_resultado(csv_path, modo_rag)
    output_file = output_dir / nome_arquivo_saida
    
    # Carregar resultados existentes (se houver)
    resultados = carregar_resultados_existentes(output_file)
    redacoes_processadas = len(resultados)
    
    # Verificar quais redações já foram processadas
    indices_processados = {r.get('redacao_index', -1) for r in resultados}
    
    if redacoes_processadas > 0:
        print(f"\n🔄 RECUPERAÇÃO DETECTADA: {redacoes_processadas}/{total_redacoes} redações já processadas")
        print(f"   Continuando de onde parou...")
    
    # Criar banca
    print(f"\n🎓 Criando Banca Examinadora...")
    banca = BancaExaminadora()
    
    # Processar cada redação
    for idx, row in df.iterrows():
        # Verificar se esta redação já foi processada
        if idx in indices_processados:
            print(f"\n⏭️  Redação {idx + 1}/{total_redacoes} - JÁ PROCESSADA (pulando)")
            continue
        
        print(f"\n{'─'*80}")
        print(f"📄 Processando Redação {idx + 1}/{total_redacoes}")
        print(f"{'─'*80}")
        
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
            competencias_reais=competencias_reais,
            idx_redacao=int(idx)
        )
        
        # Adicionar aos resultados
        resultados.append(resultado)
        
        # SALVAR INCREMENTALMENTE
        salvar_resultados_incrementais(resultados, output_file)
        
        # Status
        print(f"📊 Progresso: {len(resultados)}/{total_redacoes} redações processadas")
    
    # Relatório final
    print(f"\n{'='*80}")
    print(f"✅ PROCESSAMENTO CONCLUÍDO!")
    print(f"{'='*80}")
    print(f"📁 Arquivo: {csv_path}")
    print(f"🎯 Prompt: {prompt_id}")
    print(f"⚙️  Modo: {modo_nome}")
    print(f"📊 Total: {len(resultados)}/{total_redacoes} redações")
    
    # Contar sucessos e erros
    sucessos = sum(1 for r in resultados if r.get('status') == 'sucesso')
    erros = sum(1 for r in resultados if r.get('status') == 'erro')
    print(f"✅ Sucessos: {sucessos}")
    print(f"❌ Erros: {erros}")
    print(f"💾 Resultados salvos em: {output_file}")
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


def main():
    """
    Função principal com parsing de argumentos
    
    Uso:
        python processar_experimento.py --prompt redacoes_prompt_3.csv --rag
        python processar_experimento.py --prompt redacoes_prompt_3.csv --no-rag
        python processar_experimento.py --prompt redacoes_prompt_6.csv --rag
        python processar_experimento.py --prompt redacoes_prompt_6.csv --no-rag
    """
    parser = argparse.ArgumentParser(
        description='Processa experimento de avaliação automática de redações',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python processar_experimento.py --prompt redacoes_prompt_3.csv --rag
  python processar_experimento.py --prompt redacoes_prompt_3.csv --no-rag
  python processar_experimento.py --prompt redacoes_prompt_6.csv --rag
  python processar_experimento.py --prompt redacoes_prompt_6.csv --no-rag

Recursos:
  • Salvamento incremental: cada redação é salva após ser processada
  • Recuperação automática: continua de onde parou se interrompido
  • Tratamento de erros: alucinações do LLM são registradas e o processo continua
        """
    )
    
    parser.add_argument(
        '--prompt',
        type=str,
        required=True,
        help='Nome do arquivo CSV (ex: redacoes_prompt_3.csv)'
    )
    
    rag_group = parser.add_mutually_exclusive_group(required=True)
    rag_group.add_argument(
        '--rag',
        action='store_true',
        help='Processar COM RAG (com manuais oficiais do ENEM)'
    )
    rag_group.add_argument(
        '--no-rag',
        action='store_true',
        help='Processar SEM RAG / BASELINE (sem manuais, apenas conhecimento prévio)'
    )
    
    args = parser.parse_args()
    
    # Determinar modo RAG
    modo_rag = args.rag
    
    # Validar arquivo
    csv_path = Path(args.prompt)
    if not csv_path.exists():
        print(f"❌ Erro: Arquivo não encontrado: {csv_path}")
        print(f"   Certifique-se de que o arquivo existe no diretório atual")
        return
    
    print("\n" + "="*80)
    print("🚀 AVALIADOR AUTOMÁTICO DE REDAÇÕES - ENEM")
    print("="*80)
    print(f"📁 Arquivo: {csv_path}")
    print(f"⚙️  Modo: {'RAG (com manuais)' if modo_rag else 'BASELINE (sem manuais)'}")
    print("="*80)
    
    # Verificar API Key
    verificar_api_key_gemini()
    
    # Criar diretório de resultados
    output_dir = Path("resultados_experimento")
    output_dir.mkdir(exist_ok=True)
    print(f"📂 Diretório de saída: {output_dir.absolute()}")
    
    # Processar
    try:
        processar_experimento(
            csv_path=str(csv_path),
            modo_rag=modo_rag,
            output_dir=output_dir
        )
        
        print("\n🎉 PROCESSAMENTO FINALIZADO COM SUCESSO!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  INTERROMPIDO PELO USUÁRIO")
        print("💾 Resultados parciais foram salvos e podem ser retomados")
    except Exception as e:
        print(f"\n\n❌ ERRO CRÍTICO: {e}")
        print("💾 Resultados parciais (se houver) foram salvos")
        raise


def processar_teste_individual(idx_redacao: int):
    """
    Processa apenas UMA redação de teste COM RAG (para debug)
    
    Args:
        idx_redacao: índice da redação a ser avaliada no dataframe
    """
    print("\n🧪 MODO TESTE COM RAG - Uma redação do Prompt 3")
    
    # Verificar API Key do Gemini
    verificar_api_key_gemini()
    
    # Carregar apenas a primeira redação do prompt 3
    df = pd.read_csv("redacoes_prompt_3.csv")

    print(df)

    if idx_redacao < 0 or idx_redacao >= len(df):
        raise IndexError("Índice da redação inválido (fora dos limites)")
    row = df.iloc[idx_redacao]
    
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


def processar_teste_individual_baseline(idx_redacao: int):
    """
    Processa apenas UMA redação de teste SEM RAG - Baseline (para debug)

    Args:
        idx_redacao: índice da redação a ser avaliada no dataframe
    """
    print("\n🧪 MODO TESTE SEM RAG (BASELINE) - Uma redação do Prompt 3")
    
    # Verificar API Key do Gemini
    verificar_api_key_gemini()
    
    # Carregar apenas a primeira redação do prompt 3
    df = pd.read_csv("redacoes_prompt_3.csv")
    print(df)
    if idx_redacao < 0 or idx_redacao >= len(df):
        raise IndexError("Índice da redação inválido (fora dos limites)")
    row = df.iloc[idx_redacao]
    
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
    
    # Manter compatibilidade com testes antigos
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Modo teste COM RAG: processa apenas uma redação
        idx = int(sys.argv[2]) if len(sys.argv) > 2 else 0
        processar_teste_individual(idx)
    elif len(sys.argv) > 1 and sys.argv[1] == "--test-no-rag":
        # Modo teste SEM RAG (Baseline): processa apenas uma redação
        idx = int(sys.argv[2]) if len(sys.argv) > 2 else 0
        processar_teste_individual_baseline(idx)
    else:
        # Novo modo principal com argumentos --prompt e --rag/--no-rag
        main()

