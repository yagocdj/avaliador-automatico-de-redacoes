#!/usr/bin/env python
"""
BANCA EXAMINADORA DIGITAL - ENEM
Sistema de Avaliação Automatizada de Redações via Arquitetura Multi-Agente

Experimentos:
- Experimento A: Avaliação COM RAG (Context Injection dos Manuais)
- Experimento B: Avaliação SEM RAG (Baseline - Conhecimento Prévio)

Autor: Samuel e Yago
"""

import sys
import warnings
import json
from datetime import datetime
from pathlib import Path

from avaliacao_automatica.crew import BancaExaminadora

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


# ============================================================================
# REDAÇÃO DE EXEMPLO PARA TESTES
# ============================================================================

REDACAO_EXEMPLO = """
A questão do lixo eletrônico no Brasil

No contexto atual, o avanço tecnológico tem proporcionado diversos benefícios
à sociedade brasileira. Entretanto, esse progresso traz consigo desafios
significativos, como o acúmulo de lixo eletrônico. Esse problema decorre não
apenas do consumismo desenfreado, mas também da falta de políticas públicas
eficientes de descarte e reciclagem.

Em primeira análise, é importante ressaltar que o Brasil é um dos maiores
geradores de lixo eletrônico da América Latina. Segundo dados da ONU, milhões
de toneladas de resíduos eletrônicos são descartados inadequadamente todos os
anos. Isso ocorre porque muitas pessoas desconhecem os impactos ambientais
causados por substâncias tóxicas presentes nesses materiais, como chumbo e
mercúrio, que contaminam o solo e a água.

Além disso, a obsolescência programada contribui para agravar o problema.
As empresas fabricam produtos com vida útil reduzida, incentivando a troca
constante de aparelhos. Dessa forma, o ciclo de consumo se perpetua sem que
haja uma infraestrutura adequada para o reaproveitamento desses materiais.

Portanto, é fundamental que o governo federal, em parceria com o setor privado,
implemente campanhas educativas sobre o descarte correto de eletrônicos e
amplie os pontos de coleta em todo o território nacional. Ademais, é necessário
incentivar a indústria da reciclagem por meio de políticas fiscais, garantindo
que os materiais sejam reaproveitados de forma sustentável. Somente assim será
possível mitigar os impactos ambientais e construir uma sociedade mais
consciente e responsável.
"""

TEMA_EXEMPLO = "Desafios do lixo eletrônico no Brasil"


# ============================================================================
# FUNÇÕES PRINCIPAIS
# ============================================================================

def run():
    """
    Executa a avaliação de uma redação COM RAG (Experimento A)
    """
    print("\n" + "=" * 80)
    print("🎓 BANCA EXAMINADORA DIGITAL - Experimento A (COM RAG)")
    print("=" * 80 + "\n")
    
    inputs = {
        'redacao': REDACAO_EXEMPLO,
        'tema': TEMA_EXEMPLO,
    }

    try:
        banca = BancaExaminadora()
        resultado = banca.avaliar_redacao(
            redacao=inputs['redacao'],
            tema=inputs['tema'],
            modo_rag=True  # COM os manuais
        )
        
        print("\n✅ Avaliação concluída com sucesso!")
        print(f"📄 Resultado salvo em: resultado_avaliacao.json")
        
    except Exception as e:
        raise Exception(f"Erro ao executar a avaliação: {e}")


def run_baseline():
    """
    Executa a avaliação de uma redação SEM RAG (Experimento B - Baseline)
    """
    print("\n" + "=" * 80)
    print("🎓 BANCA EXAMINADORA DIGITAL - Experimento B (BASELINE - SEM RAG)")
    print("=" * 80 + "\n")
    
    inputs = {
        'redacao': REDACAO_EXEMPLO,
        'tema': TEMA_EXEMPLO,
    }
    try:
        banca = BancaExaminadora()
        resultado = banca.avaliar_redacao(
            redacao=inputs['redacao'],
            tema=inputs['tema'],
            modo_rag=False  # SEM os manuais (baseline)
        )
        
        print("\n✅ Avaliação baseline concluída com sucesso!")
        print(f"📄 Resultado salvo em: resultado_avaliacao_baseline.json")
        
    except Exception as e:
        raise Exception(f"Erro ao executar a avaliação baseline: {e}")


def run_experimento_completo():
    """
    Executa AMBOS os experimentos (A e B) para comparação
    """
    print("\n" + "=" * 80)
    print("🔬 EXPERIMENTO COMPLETO: RAG vs BASELINE")
    print("=" * 80 + "\n")
    
    inputs = {
        'redacao': REDACAO_EXEMPLO,
        'tema': TEMA_EXEMPLO,
    }
    
    resultados = {}
    
    try:
        banca = BancaExaminadora()
        
        # Experimento A: COM RAG
        print("📊 Executando Experimento A (COM RAG)...\n")
        resultado_rag = banca.avaliar_redacao(
            redacao=inputs['redacao'],
            tema=inputs['tema'],
            modo_rag=True
        )
        resultados['experimento_A_com_rag'] = resultado_rag
        
        print("\n" + "=" * 80 + "\n")
        
        # Experimento B: SEM RAG (Baseline)
        print("📊 Executando Experimento B (BASELINE)...\n")
        resultado_baseline = banca.avaliar_redacao(
            redacao=inputs['redacao'],
            tema=inputs['tema'],
            modo_rag=False
        )
        resultados['experimento_B_baseline'] = resultado_baseline
        
        # Salvar comparação
        output_path = Path("comparacao_experimentos.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(resultados, f, ensure_ascii=False, indent=2)
        
        print("\n" + "=" * 80)
        print("✅ EXPERIMENTO COMPLETO CONCLUÍDO!")
        print(f"📊 Comparação salva em: {output_path}")
        print("=" * 80 + "\n")
        
    except Exception as e:
        raise Exception(f"Erro ao executar experimento completo: {e}")


def avaliar_arquivo(filepath: str, tema: str, modo_rag: bool = True):
    """
    Avalia uma redação de um arquivo .txt
    
    Args:
        filepath: Caminho para o arquivo com a redação
        tema: Tema da redação
        modo_rag: True = com RAG, False = baseline
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            redacao = f.read()
        
        banca = BancaExaminadora()
        resultado = banca.avaliar_redacao(
            redacao=redacao,
            tema=tema,
            modo_rag=modo_rag
        )
        
        print(f"\n✅ Redação de {filepath} avaliada com sucesso!")
        
    except FileNotFoundError:
        print(f"❌ Erro: Arquivo {filepath} não encontrado.")
    except Exception as e:
        raise Exception(f"Erro ao avaliar arquivo: {e}")


def train():
    """
    Treina a banca para um determinado número de iterações.
    """
    inputs = {
        "redacao": REDACAO_EXEMPLO,
        "tema": TEMA_EXEMPLO,
    }
    
    try:
        BancaExaminadora().crew().train(
            n_iterations=int(sys.argv[1]), 
            filename=sys.argv[2], 
            inputs=inputs
        )
    except Exception as e:
        raise Exception(f"Erro ao treinar a banca: {e}")


def replay():
    """
    Reproduz a execução da banca a partir de uma tarefa específica.
    """
    try:
        BancaExaminadora().crew().replay(task_id=sys.argv[1])
    except Exception as e:
        raise Exception(f"Erro ao reproduzir a banca: {e}")


def test():
    """
    Testa a execução da banca e retorna os resultados.
    """
    inputs = {
        "redacao": REDACAO_EXEMPLO,
        "tema": TEMA_EXEMPLO,
    }

    try:
        BancaExaminadora().crew().test(
            n_iterations=int(sys.argv[1]), 
            eval_llm=sys.argv[2], 
            inputs=inputs
        )
    except Exception as e:
        raise Exception(f"Erro ao testar a banca: {e}")


# ============================================================================
# MENU INTERATIVO
# ============================================================================

def menu():
    """Menu interativo para seleção de experimento"""
    print("\n" + "=" * 80)
    print("🎓 BANCA EXAMINADORA DIGITAL - SISTEMA DE AVALIAÇÃO DE REDAÇÕES ENEM")
    print("=" * 80)
    print("\nSelecione o modo de execução:\n")
    print("1. Experimento A - Avaliação COM RAG (Context Injection)")
    print("2. Experimento B - Avaliação SEM RAG (Baseline)")
    print("3. Experimento Completo - Executar AMBOS e Comparar")
    print("4. Avaliar redação de arquivo .txt")
    print("5. Sair")
    print("\n" + "=" * 80)
    
    escolha = input("\nDigite o número da opção: ").strip()
    
    if escolha == "1":
        run()
    elif escolha == "2":
        run_baseline()
    elif escolha == "3":
        run_experimento_completo()
    elif escolha == "4":
        filepath = input("Digite o caminho do arquivo .txt: ").strip()
        tema = input("Digite o tema da redação: ").strip()
        modo = input("Com RAG? (s/n): ").strip().lower()
        avaliar_arquivo(filepath, tema, modo_rag=(modo == 's'))
    elif escolha == "5":
        print("\n👋 Encerrando sistema...\n")
        sys.exit(0)
    else:
        print("\n❌ Opção inválida!")
        menu()


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    # Se executado diretamente, mostra o menu
    if len(sys.argv) == 1:
        menu()
    # Se executado via crewai run, executa o modo padrão (COM RAG)
    else:
        run()
