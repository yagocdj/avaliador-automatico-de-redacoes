"""
SCRIPT DE ANÁLISE DE MÉTRICAS - VERSÃO SIMPLIFICADA
Calcula as 5 métricas essenciais: MAE, RMSE, QWK, Acurácia Exata, Acurácia Adjacente

Compara:
- RAG vs Ground Truth
- Baseline vs Ground Truth

Uso:
    python analisar_metricas.py --prompt 3
    python analisar_metricas.py --prompt 6
    python analisar_metricas.py --prompt 3 --export resultados_prompt3.csv
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
import argparse
from sklearn.metrics import cohen_kappa_score, mean_absolute_error


def carregar_resultados(arquivo):
    """Carrega arquivo JSON de resultados"""
    with open(arquivo, 'r', encoding='utf-8') as f:
        return json.load(f)


def extrair_notas(resultados):
    """Extrai notas reais e preditas dos resultados"""
    dados = []
    
    for r in resultados:
        if r['status'] == 'sucesso':
            av = r['avaliacao_sistema']
            
            # Verificar se avaliacao_sistema não é None
            if av is None:
                print(f"⚠️  Aviso: redacao_index {r['redacao_index']} tem avaliacao_sistema NULL")
                continue
            
            dados.append({
                'index': r['redacao_index'],
                'nota_real': r['nota_real'],
                'nota_pred': av['nota_final'],
                'comp1_real': r['competencias_reais'][0],
                'comp1_pred': av['competencias']['competencia_1']['nota'],
                'comp2_real': r['competencias_reais'][1],
                'comp2_pred': av['competencias']['competencia_2']['nota'],
                'comp3_real': r['competencias_reais'][2],
                'comp3_pred': av['competencias']['competencia_3']['nota'],
                'comp4_real': r['competencias_reais'][3],
                'comp4_pred': av['competencias']['competencia_4']['nota'],
                'comp5_real': r['competencias_reais'][4],
                'comp5_pred': av['competencias']['competencia_5']['nota'],
            })
    
    return pd.DataFrame(dados)


def calcular_metricas_gerais(df, prefixo=''):
    """
    Calcula as 5 métricas essenciais para nota total
    
    Métricas:
    1. MAE - Mean Absolute Error
    2. RMSE - Root Mean Squared Error
    3. QWK - Quadratic Weighted Kappa
    4. Acurácia Exata - Exact Match
    5. Acurácia Adjacente - Adjacent Match (±40 pontos)
    """
    notas_reais = df['nota_real'].values
    notas_pred = df['nota_pred'].values
    
    # 1. MAE - Erro Médio Absoluto
    mae = mean_absolute_error(notas_reais, notas_pred)
    
    # 2. RMSE - Raiz do Erro Quadrático Médio
    rmse = np.sqrt(np.mean((notas_pred - notas_reais) ** 2))
    
    # 3. QWK - Quadratic Weighted Kappa
    # Converter notas para níveis (escala de 40 pontos: 0-25 níveis)
    niveis_reais = notas_reais // 40
    niveis_pred = notas_pred // 40
    qwk = cohen_kappa_score(niveis_reais, niveis_pred, weights='quadratic')
    
    # 4. Acurácia Exata (Exact Match)
    acuracia_exata = np.mean(notas_pred == notas_reais)
    
    # 5. Acurácia Adjacente (±40 pontos de tolerância)
    acuracia_adjacente = np.mean(np.abs(notas_pred - notas_reais) <= 40)
    
    metricas = {
        f'{prefixo}MAE': mae,
        f'{prefixo}RMSE': rmse,
        f'{prefixo}QWK': qwk,
        f'{prefixo}Acurácia_Exata': acuracia_exata,
        f'{prefixo}Acurácia_Adjacente': acuracia_adjacente,
    }
    
    return metricas


def calcular_metricas_por_competencia(df, prefixo=''):
    """
    Calcula MAE para cada competência (C1 a C5)
    """
    metricas_comp = {}
    
    for i in range(1, 6):
        comp_real = df[f'comp{i}_real'].values
        comp_pred = df[f'comp{i}_pred'].values
        
        # MAE por competência
        mae = mean_absolute_error(comp_real, comp_pred)
        metricas_comp[f'{prefixo}Comp{i}_MAE'] = mae
    
    return metricas_comp


def comparar_rag_baseline(df_rag, df_baseline):
    """
    Compara desempenho entre RAG e Baseline (ambos vs Ground Truth)
    Retorna diferenças simples sem testes estatísticos complexos
    """
    
    # Calcular erros absolutos
    erros_rag = np.abs(df_rag['nota_pred'].values - df_rag['nota_real'].values)
    erros_baseline = np.abs(df_baseline['nota_pred'].values - df_baseline['nota_real'].values)
    
    comparacao = {
        'MAE_RAG': np.mean(erros_rag),
        'MAE_Baseline': np.mean(erros_baseline),
        'Diferença_MAE': np.mean(erros_rag) - np.mean(erros_baseline),
        'RAG_melhor': np.mean(erros_rag) < np.mean(erros_baseline),
    }
    
    return comparacao


def gerar_relatorio_completo(prompt_id, exportar_csv=None):
    """Gera relatório completo de todas as métricas"""
    
    print("="*80)
    print(f"📊 RELATÓRIO DE MÉTRICAS - PROMPT {prompt_id}")
    print("="*80)
    
    # Carregar dados
    rag_file = f'resultados_experimento/resultados_prompt{prompt_id}_rag.json'
    baseline_file = f'resultados_experimento/resultados_prompt{prompt_id}_baseline.json'
    
    if not Path(rag_file).exists():
        print(f"\n❌ Arquivo não encontrado: {rag_file}")
        return None
    
    if not Path(baseline_file).exists():
        print(f"\n❌ Arquivo não encontrado: {baseline_file}")
        return None
    
    res_rag = carregar_resultados(rag_file)
    res_baseline = carregar_resultados(baseline_file)
    
    df_rag = extrair_notas(res_rag)
    df_baseline = extrair_notas(res_baseline)
    
    print(f"\n✅ Sucessos RAG: {len(df_rag)}/{len(res_rag)}")
    print(f"✅ Sucessos Baseline: {len(df_baseline)}/{len(res_baseline)}")
    
    if len(df_rag) == 0 or len(df_baseline) == 0:
        print("\n❌ Erro: Não há dados suficientes para análise")
        return None
    
    # ========== MÉTRICAS GERAIS ==========
    print("\n" + "="*80)
    print("📈 MÉTRICAS GERAIS - RAG vs BASELINE vs GROUND TRUTH")
    print("="*80)
    
    metricas_rag = calcular_metricas_gerais(df_rag, 'RAG_')
    metricas_baseline = calcular_metricas_gerais(df_baseline, 'Baseline_')
    
    # Tabela comparativa das 5 métricas essenciais
    print(f"\n{'Métrica':<30} {'RAG':>15} {'Baseline':>15} {'Melhor':>12}")
    print("-"*75)
    
    # Lista das métricas a apresentar
    metricas_labels = [
        ('MAE', 'menor', 'pontos'),
        ('RMSE', 'menor', 'pontos'),
        ('QWK', 'maior', 'score'),
        ('Acurácia_Exata', 'maior', 'percent'),
        ('Acurácia_Adjacente', 'maior', 'percent'),
    ]
    
    for label, criterio, formato in metricas_labels:
        val_rag = metricas_rag[f'RAG_{label}']
        val_baseline = metricas_baseline[f'Baseline_{label}']
        
        # Determinar qual é melhor
        if criterio == 'menor':
            melhor = 'RAG' if val_rag < val_baseline else 'Baseline'
        else:
            melhor = 'RAG' if val_rag > val_baseline else 'Baseline'
        
        # Formatação de saída
        if formato == 'percent':
            print(f"{label:<30} {val_rag*100:>14.1f}% {val_baseline*100:>14.1f}% {melhor:>12}")
        else:
            print(f"{label:<30} {val_rag:>15.3f} {val_baseline:>15.3f} {melhor:>12}")
    
    # ========== MÉTRICAS POR COMPETÊNCIA ==========
    print("\n" + "="*80)
    print("📊 MÉTRICAS POR COMPETÊNCIA - MAE")
    print("="*80)
    
    metricas_comp_rag = calcular_metricas_por_competencia(df_rag, 'RAG_')
    metricas_comp_baseline = calcular_metricas_por_competencia(df_baseline, 'Baseline_')
    
    print(f"\n{'Competência':<25} {'MAE RAG':>12} {'MAE Baseline':>12} {'Diferença':>12} {'Melhor':>12}")
    print("-"*75)
    
    competencias = [
        'C1 (Gramática)',
        'C2 (Estrutura)',
        'C3 (Argumentação)',
        'C4 (Coesão)',
        'C5 (Proposta)',
    ]
    
    for i, nome_comp in enumerate(competencias, 1):
        mae_rag = metricas_comp_rag[f'RAG_Comp{i}_MAE']
        mae_baseline = metricas_comp_baseline[f'Baseline_Comp{i}_MAE']
        diff = mae_baseline - mae_rag  # Positivo = RAG melhor
        melhor = 'RAG' if mae_rag < mae_baseline else 'Baseline'
        
        print(f"{nome_comp:<25} {mae_rag:>12.2f} {mae_baseline:>12.2f} {diff:>+12.2f} {melhor:>12}")
    
    # ========== TESTES ESTATÍSTICOS ==========
    print("\n" + "="*80)
    print("📊 COMPARAÇÃO RESUMIDA: RAG vs BASELINE")
    print("="*80)
    
    comparacao = comparar_rag_baseline(df_rag, df_baseline)
    
    print(f"\nMAE RAG:          {comparacao['MAE_RAG']:.2f} pontos")
    print(f"MAE Baseline:     {comparacao['MAE_Baseline']:.2f} pontos")
    print(f"Diferença:        {comparacao['Diferença_MAE']:+.2f} pontos")
    
    if comparacao['RAG_melhor']:
        print(f"\n✅ RAG teve MELHOR desempenho (MAE {abs(comparacao['Diferença_MAE']):.2f} pontos menor)")
    else:
        print(f"\n⚠️  Baseline teve MELHOR desempenho (MAE {abs(comparacao['Diferença_MAE']):.2f} pontos menor)")
    
    print("\n" + "="*80)
    
    # ========== EXPORTAR CSV (OPCIONAL) ==========
    if exportar_csv:
        # Combinar dados para análise
        df_completo = pd.DataFrame({
            'index': df_rag['index'],
            'nota_real': df_rag['nota_real'],
            'nota_pred_rag': df_rag['nota_pred'],
            'nota_pred_baseline': df_baseline['nota_pred'],
            'erro_rag': df_rag['nota_pred'] - df_rag['nota_real'],
            'erro_baseline': df_baseline['nota_pred'] - df_baseline['nota_real'],
            'erro_abs_rag': np.abs(df_rag['nota_pred'] - df_rag['nota_real']),
            'erro_abs_baseline': np.abs(df_baseline['nota_pred'] - df_baseline['nota_real']),
        })
        
        # Adicionar competências
        for i in range(1, 6):
            df_completo[f'comp{i}_real'] = df_rag[f'comp{i}_real']
            df_completo[f'comp{i}_pred_rag'] = df_rag[f'comp{i}_pred']
            df_completo[f'comp{i}_pred_baseline'] = df_baseline[f'comp{i}_pred']
        
        df_completo.to_csv(exportar_csv, index=False)
        print(f"\n💾 Dados exportados para: {exportar_csv}")
    
    # Retornar dados para uso posterior
    return {
        'df_rag': df_rag,
        'df_baseline': df_baseline,
        'metricas_rag': metricas_rag,
        'metricas_baseline': metricas_baseline,
        'metricas_comp_rag': metricas_comp_rag,
        'metricas_comp_baseline': metricas_comp_baseline,
        'comparacao': comparacao,
    }


def main():
    parser = argparse.ArgumentParser(
        description='Analisa métricas dos experimentos de avaliação automatizada',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python analisar_metricas.py --prompt 3
  python analisar_metricas.py --prompt 6
  python analisar_metricas.py --prompt 3 --export resultados_prompt3.csv
        """
    )
    
    parser.add_argument(
        '--prompt',
        type=int,
        required=True,
        choices=[3, 6],
        help='ID do prompt a analisar (3 ou 6)'
    )
    
    parser.add_argument(
        '--export',
        type=str,
        help='Exportar dados para CSV (opcional)'
    )
    
    args = parser.parse_args()
    
    # Gerar relatório
    resultado = gerar_relatorio_completo(args.prompt, args.export)
    
    if resultado is None:
        print("\n❌ Falha ao gerar relatório")
        return 1
    
    print("\n✅ Análise concluída!")
    return 0


if __name__ == "__main__":
    exit(main())

