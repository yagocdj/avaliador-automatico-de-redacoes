#!/bin/bash

# ============================================================================
# Script para processar todos os 4 experimentos em sequência
# ============================================================================

echo "================================================================================"
echo "🚀 PROCESSAMENTO COMPLETO DOS 4 EXPERIMENTOS"
echo "================================================================================"
echo ""
echo "Este script irá processar:"
echo "  1. Prompt 3 COM RAG     (20 redações)"
echo "  2. Prompt 3 SEM RAG     (20 redações)"
echo "  3. Prompt 6 COM RAG     (20 redações)"
echo "  4. Prompt 6 SEM RAG     (20 redações)"
echo ""
echo "Total: 80 avaliações"
echo "Tempo estimado: 2-4 horas"
echo ""
echo "✨ Recursos:"
echo "  • Salvamento incremental após cada redação"
echo "  • Recuperação automática em caso de interrupção"
echo "  • Tratamento de erros e alucinações do LLM"
echo ""
echo "================================================================================"
echo ""

# Função para mostrar tempo decorrido
start_time=$(date +%s)

# ====================
# EXPERIMENTO 1
# ====================
echo ""
echo "################################################################################"
echo "# EXPERIMENTO 1/4: Prompt 3 COM RAG"
echo "################################################################################"
echo ""

python processar_experimento.py --prompt redacoes_prompt_3.csv --rag

if [ $? -ne 0 ]; then
    echo "⚠️  Experimento 1 falhou ou foi interrompido"
    echo "💾 Progresso foi salvo. Execute novamente para continuar."
    exit 1
fi

# ====================
# EXPERIMENTO 2
# ====================
echo ""
echo "################################################################################"
echo "# EXPERIMENTO 2/4: Prompt 3 SEM RAG (Baseline)"
echo "################################################################################"
echo ""

python processar_experimento.py --prompt redacoes_prompt_3.csv --no-rag

if [ $? -ne 0 ]; then
    echo "⚠️  Experimento 2 falhou ou foi interrompido"
    echo "💾 Progresso foi salvo. Execute novamente para continuar."
    exit 1
fi

# ====================
# EXPERIMENTO 3
# ====================
echo ""
echo "################################################################################"
echo "# EXPERIMENTO 3/4: Prompt 6 COM RAG"
echo "################################################################################"
echo ""

python processar_experimento.py --prompt redacoes_prompt_6.csv --rag

if [ $? -ne 0 ]; then
    echo "⚠️  Experimento 3 falhou ou foi interrompido"
    echo "💾 Progresso foi salvo. Execute novamente para continuar."
    exit 1
fi

# ====================
# EXPERIMENTO 4
# ====================
echo ""
echo "################################################################################"
echo "# EXPERIMENTO 4/4: Prompt 6 SEM RAG (Baseline)"
echo "################################################################################"
echo ""

python processar_experimento.py --prompt redacoes_prompt_6.csv --no-rag

if [ $? -ne 0 ]; then
    echo "⚠️  Experimento 4 falhou ou foi interrompido"
    echo "💾 Progresso foi salvo. Execute novamente para continuar."
    exit 1
fi

# ====================
# RELATÓRIO FINAL
# ====================
end_time=$(date +%s)
elapsed_time=$((end_time - start_time))
hours=$((elapsed_time / 3600))
minutes=$(((elapsed_time % 3600) / 60))
seconds=$((elapsed_time % 60))

echo ""
echo "================================================================================"
echo "🎉 TODOS OS 4 EXPERIMENTOS CONCLUÍDOS!"
echo "================================================================================"
echo ""
echo "⏱️  Tempo total: ${hours}h ${minutes}m ${seconds}s"
echo ""
echo "📂 Resultados salvos em: resultados_experimento/"
echo ""
echo "Arquivos gerados:"
echo "  ✅ resultados_prompt3_rag.json"
echo "  ✅ resultados_prompt3_baseline.json"
echo "  ✅ resultados_prompt6_rag.json"
echo "  ✅ resultados_prompt6_baseline.json"
echo ""
echo "================================================================================"
echo ""
echo "📊 Próximos passos:"
echo "  1. Analisar os resultados com: jupyter notebook analise_redacoes.ipynb"
echo "  2. Ou verificar manualmente os arquivos JSON"
echo ""
echo "================================================================================"

