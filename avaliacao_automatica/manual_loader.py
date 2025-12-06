"""
Carregador de Manuais das Competências ENEM - Versão Simplificada
"""

from pathlib import Path
from PyPDF2 import PdfReader


def load_manual_simple(competencia_id: int) -> str:
    """
    Carrega o manual de uma competência específica.
    
    Args:
        competencia_id: Número da competência (1 a 5)
        
    Returns:
        str: Texto completo do manual da competência
    """
    if not 1 <= competencia_id <= 5:
        raise ValueError(f"competencia_id deve estar entre 1 e 5, recebido: {competencia_id}")
    
    # PDFs estão em: ../rag_context/Competencia_X.pdf (relativo ao módulo)
    pdf_path = Path(__file__).parent.parent / "rag_context" / f"Competencia_{competencia_id}.pdf"
    
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF não encontrado: {pdf_path}")
    
    try:
        reader = PdfReader(str(pdf_path))
        texto_completo = []
        
        for page in reader.pages:
            texto = page.extract_text()
            if texto:
                texto_completo.append(texto)
        
        resultado = "\n\n".join(texto_completo)
        
        if not resultado.strip():
            raise ValueError(f"PDF da competência {competencia_id} está vazio")
        
        return resultado
        
    except Exception as e:
        raise Exception(f"Erro ao carregar manual da competência {competencia_id}: {str(e)}")

