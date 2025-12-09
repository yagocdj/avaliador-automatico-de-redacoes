"""
VERIFICAÇÃO PRÉ-EXPERIMENTO
Script para verificar se tudo está configurado corretamente
"""

import sys
from pathlib import Path


def verificar_arquivos():
    """Verifica se todos os arquivos necessários existem"""
    print("=" * 80)
    print("🔍 VERIFICANDO ARQUIVOS NECESSÁRIOS")
    print("=" * 80)
    
    arquivos_obrigatorios = [
        "redacoes_prompt_3.csv",
        "redacoes_prompt_6.csv",
        "processar_experimento.py",
        "avaliacao_automatica/config/tasks.yaml",
        "avaliacao_automatica/crew.py",
    ]
    
    todos_ok = True
    
    for arquivo in arquivos_obrigatorios:
        caminho = Path(arquivo)
        if caminho.exists():
            print(f"✅ {arquivo}")
        else:
            print(f"❌ {arquivo} - NÃO ENCONTRADO")
            todos_ok = False
    
    return todos_ok


def verificar_csv_estrutura():
    """Verifica se os CSVs têm a estrutura correta"""
    print("\n" + "=" * 80)
    print("📊 VERIFICANDO ESTRUTURA DOS CSVs")
    print("=" * 80)
    
    try:
        import pandas as pd
        
        for prompt_id, arquivo in [(3, "redacoes_prompt_3.csv"), (6, "redacoes_prompt_6.csv")]:
            print(f"\n📄 {arquivo}:")
            
            df = pd.read_csv(arquivo)
            
            # Verificar colunas
            colunas_esperadas = {'prompt', 'title', 'essay', 'competence', 'score'}
            colunas_presentes = set(df.columns)
            
            if colunas_esperadas == colunas_presentes:
                print(f"   ✅ Colunas corretas: {list(df.columns)}")
            else:
                print("   ❌ Colunas incorretas!")
                print(f"      Esperado: {colunas_esperadas}")
                print(f"      Encontrado: {colunas_presentes}")
                return False
            
            # Verificar quantidade
            print(f"   ✅ Quantidade de redações: {len(df)}")
            
            # Verificar prompt_id
            prompts_unicos = df['prompt'].unique()
            if len(prompts_unicos) == 1 and prompts_unicos[0] == prompt_id:
                print(f"   ✅ Prompt ID correto: {prompt_id}")
            else:
                print(f"   ❌ Prompt ID incorreto: {prompts_unicos}")
                return False
            
            # Verificar temas
            temas_unicos = df['title'].nunique()
            print(f"   ℹ️  Temas únicos: {temas_unicos}")
            
            # Verificar notas
            print(f"   ℹ️  Nota mínima: {df['score'].min()}")
            print(f"   ℹ️  Nota máxima: {df['score'].max()}")
            print(f"   ℹ️  Nota média: {df['score'].mean():.2f}")
        
        return True
        
    except ImportError:
        print("❌ Pandas não instalado. Instale com: pip install pandas")
        return False
    except Exception as e:
        print(f"❌ Erro ao verificar CSVs: {e}")
        return False


def verificar_tasks_yaml():
    """Verifica se tasks.yaml foi atualizado corretamente"""
    print("\n" + "=" * 80)
    print("📝 VERIFICANDO tasks.yaml")
    print("=" * 80)
    
    try:
        caminho_tasks = Path("avaliacao_automatica/config/tasks.yaml")
        
        if not caminho_tasks.exists():
            print("❌ tasks.yaml não encontrado")
            return False
        
        conteudo = caminho_tasks.read_text(encoding='utf-8')
        
        # Verificar se "nivel" foi removido
        if '"nivel"' in conteudo or "'nivel'" in conteudo:
            print("⚠️  ATENÇÃO: Ainda há referências a 'nivel' no arquivo!")
            print("   Verifique se todas foram removidas corretamente.")
            return False
        else:
            print("✅ Campo 'nivel' removido corretamente")
        
        # Verificar se os intervalos estão explícitos
        if "0, 40, 80, 120, 160 ou 200" in conteudo:
            print("✅ Intervalos de nota explicitados")
        else:
            print("⚠️  ATENÇÃO: Intervalos de nota não encontrados")
            return False
        
        # Verificar número de competências
        count_competencia = conteudo.count("tarefa_competencia")
        if count_competencia >= 5:
            print(f"✅ {count_competencia} tarefas de competências encontradas")
        else:
            print(f"❌ Apenas {count_competencia} tarefas encontradas")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar tasks.yaml: {e}")
        return False


def verificar_dependencias():
    """Verifica se as dependências Python estão instaladas"""
    print("\n" + "=" * 80)
    print("📦 VERIFICANDO DEPENDÊNCIAS")
    print("=" * 80)
    
    dependencias = [
        ("crewai", "CrewAI"),
        ("pandas", "Pandas"),
        ("pathlib", "Pathlib (built-in)"),
    ]
    
    todos_ok = True
    
    for modulo, nome in dependencias:
        try:
            __import__(modulo)
            print(f"✅ {nome}")
        except ImportError:
            print(f"❌ {nome} - NÃO INSTALADO")
            todos_ok = False
    
    return todos_ok


def verificar_textos_apoio():
    """Verifica se o arquivo de textos de apoio existe e está correto"""
    print("\n" + "=" * 80)
    print("📋 VERIFICANDO TEXTOS DE APOIO")
    print("=" * 80)
    
    try:
        from textos_apoio import obter_textos_apoio
        
        print("✅ Módulo textos_apoio importado com sucesso")
        
        # Verificar Prompt 3
        try:
            tema3, textos3 = obter_textos_apoio(3)
            if tema3 == "Ciência, tecnologia e superação dos limites humanos":
                print("✅ Prompt 3 - Tema correto")
                print(f"   {tema3}")
            else:  # FIXME - Dúvida: o retorno deveria ser `False`?
                print("⚠️  Prompt 3 - Tema diferente do esperado:")
                print("   Esperado: Ciência, tecnologia e superação dos limites humanos")
                print(f"   Encontrado: {tema3}")
            
            print(f"   Textos de apoio: {len(textos3)} caracteres")
        except Exception as e:
            print(f"❌ Erro ao carregar Prompt 3: {e}")
            return False
        
        # Verificar Prompt 6
        try:
            tema6, textos6 = obter_textos_apoio(6)
            if tema6 == "Preservação da Amazônia: Desafio brasileiro ou internacional?":
                print("✅ Prompt 6 - Tema correto")
                print(f"   {tema6}")
            else:  # FIXME - Dúvida: o retorno deveria ser `False`?
                print("⚠️  Prompt 6 - Tema diferente do esperado:")
                print("   Esperado: Preservação da Amazônia: Desafio brasileiro ou internacional?")
                print(f"   Encontrado: {tema6}")
            
            print(f"   Textos de apoio: {len(textos6)} caracteres")
        except Exception as e:
            print(f"❌ Erro ao carregar Prompt 6: {e}")
            return False
        
        return True
        
    except ImportError as e:
        print(f"❌ Erro ao importar textos_apoio: {e}")
        print("   Certifique-se de que o arquivo textos_apoio.py existe")
        return False


def verificar_ambiente():
    """Verifica variáveis de ambiente"""
    print("\n" + "=" * 80)
    print("🔐 VERIFICANDO AMBIENTE - GOOGLE GEMINI")
    print("=" * 80)
    
    import os
    
    # Verificar API Key do Gemini (prioritário para o experimento)
    gemini_keys = ["GEMINI_API_KEY", "GOOGLE_API_KEY"]
    
    gemini_key_encontrada = False
    
    for key_name in gemini_keys:
        if key_name in os.environ:
            valor = os.environ[key_name]
            if len(valor) > 8:
                print(f"✅ {key_name} configurada (***{valor[-8:]})")
                gemini_key_encontrada = True
            else:
                print(f"⚠️  {key_name} configurada mas parece inválida")
    
    if not gemini_key_encontrada:
        print("❌ GEMINI_API_KEY ou GOOGLE_API_KEY não encontrada!")
        print("\n📝 INSTRUÇÕES:")
        print("   1. Obtenha sua chave em: https://makersuite.google.com/app/apikey")
        print("   2. Configure a variável de ambiente:")
        print("\n   Windows PowerShell:")
        print('      $env:GEMINI_API_KEY="sua-chave-aqui"')
        print("\n   Linux/Mac:")
        print('      export GEMINI_API_KEY="sua-chave-aqui"')
        print("\n   Ou crie arquivo .env com:")
        print('      GEMINI_API_KEY=sua-chave-aqui')
        return False
    
    return True


def main():
    """Executa todas as verificações"""
    print("\n" + "#" * 80)
    print("# VERIFICAÇÃO PRÉ-EXPERIMENTO")
    print("#" * 80)
    
    resultados = []
    
    # Executar verificações
    resultados.append(("Arquivos", verificar_arquivos()))
    resultados.append(("Estrutura CSVs", verificar_csv_estrutura()))
    resultados.append(("tasks.yaml", verificar_tasks_yaml()))
    resultados.append(("Textos de Apoio", verificar_textos_apoio()))
    resultados.append(("Dependências", verificar_dependencias()))
    resultados.append(("Gemini API Key", verificar_ambiente()))
    
    # Resumo final
    print("\n" + "=" * 80)
    print("📋 RESUMO DA VERIFICAÇÃO")
    print("=" * 80)
    
    todos_ok = all(resultado for _, resultado in resultados)
    
    for nome, ok in resultados:
        status = "✅" if ok else "❌"
        print(f"{status} {nome}")
    
    print("\n" + "=" * 80)
    
    if todos_ok:
        print("🎉 TUDO PRONTO! Você pode executar o experimento com Google Gemini.")
        print("\n📝 Lembre-se:")
        print("  - Modelo configurado: gemini/gemini-1.5-flash")
        print("  - Rate limit gratuito: 15 requisições/minuto")
        print("  - Tempo estimado: 30-60 minutos para experimento completo")
        print("\nComandos:")
        print("  python processar_experimento.py --test    # Teste com 1 redação")
        print("  python processar_experimento.py            # Experimento completo")
    else:
        print("⚠️  PROBLEMAS ENCONTRADOS! Corrija antes de executar.")
        print("\nVeja mais detalhes em: CONFIGURACAO_GEMINI.md")
        return 1
    
    print("=" * 80)
    return 0


if __name__ == "__main__":
    sys.exit(main())

