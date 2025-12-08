"""
BANCA EXAMINADORA DIGITAL - ENEM
Implementação da Arquitetura Multi-Agente com Flow para Avaliação Paralela
"""

from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List, Dict, Any

# Importar o carregador de manuais
from avaliacao_automatica.manual_loader import load_manual_simple

import os


@CrewBase
class BancaExaminadora():
    """
    Banca Examinadora Digital - Sistema Multi-Agente para Avaliação de Redações ENEM
    
    Arquitetura:
    - 5 Agentes Especialistas (um para cada competência)
    - 1 Agente Consolidador (Presidente da Banca)
    - Processo Sequencial com context sharing
    """

    agents: List[BaseAgent]
    tasks: List[Task]
    
    # Configuração do LLM
    llm = LLM(
        model=os.environ.get("MODEL", "gemini-2.5-flash"),
        temperature=0.1
    )
    
    # Controle do modo RAG (True = com manual, False = baseline)
    modo_rag: bool = True

    # ========================================================================
    # AGENTES ESPECIALISTAS
    # ========================================================================
    
    @agent
    def agente_gramatica(self) -> Agent:
        """Agente I: O Gramático - Especialista em Competência I"""
        return Agent(
            config=self.agents_config['agente_gramatica'], # type: ignore[index]
            verbose=True,
            llm=self.llm
        )

    @agent
    def agente_estrutura(self) -> Agent:
        """Agente II: O Estruturalista - Especialista em Competência II"""
        return Agent(
            config=self.agents_config['agente_estrutura'], # type: ignore[index]
            verbose=True,
            llm=self.llm
        )

    @agent
    def agente_argumentacao(self) -> Agent:
        """Agente III: O Argumentador - Especialista em Competência III"""
        return Agent(
            config=self.agents_config['agente_argumentacao'], # type: ignore[index]
            verbose=True,
            llm=self.llm
        )
    
    @agent
    def agente_coesao(self) -> Agent:
        """Agente IV: O Linguista - Especialista em Competência IV"""
        return Agent(
            config=self.agents_config['agente_coesao'], # type: ignore[index]
            verbose=True,
            llm=self.llm
        )
    
    @agent
    def agente_proposta(self) -> Agent:
        """Agente V: O Intervencionista - Especialista em Competência V"""
        return Agent(
            config=self.agents_config['agente_proposta'], # type: ignore[index]
            verbose=True,
            llm=self.llm
        )
    
    @agent
    def presidente_banca(self) -> Agent:
        """Agente VI: Presidente da Banca - Consolidador"""
        return Agent(
            config=self.agents_config['presidente_banca'], # type: ignore[index]
            verbose=True,
            llm=self.llm
        )

    # ========================================================================
    # TAREFAS DE AVALIAÇÃO
    # ========================================================================
    
    def _carregar_manual(self, competencia: int) -> str:
        """
        Carrega o manual da competência
        
        Args:
            competencia: Número da competência (1-5)
            
        Returns:
            Texto do manual ou string vazia se modo baseline
        """
        if not self.modo_rag:
            if competencia == 1:  # Mensagem apenas na primeira vez
                print("⚠️  MODO BASELINE: Não serão carregados os manuais das competências")
            return "[MODO BASELINE: Avalie utilizando seu conhecimento prévio sobre os critérios de avaliação do ENEM. NÃO há manual de referência disponível.]"
        
        # Carregar manual do PDF
        print(f"📚 Carregando manual da Competência {competencia}...")
        manual_text = load_manual_simple(competencia)
        return manual_text
    
    @task
    def tarefa_competencia1(self) -> Task:
        """Task: Avaliar Competência I (Gramática)"""
        return Task(
            config=self.tasks_config['tarefa_competencia1'], # type: ignore[index]
        )

    @task
    def tarefa_competencia2(self) -> Task:
        """Task: Avaliar Competência II (Tema e Estrutura)"""
        return Task(
            config=self.tasks_config['tarefa_competencia2'], # type: ignore[index]
        )

    @task
    def tarefa_competencia3(self) -> Task:
        """Task: Avaliar Competência III (Argumentação)"""
        return Task(
            config=self.tasks_config['tarefa_competencia3'], # type: ignore[index]
        )
    
    @task
    def tarefa_competencia4(self) -> Task:
        """Task: Avaliar Competência IV (Coesão)"""
        return Task(
            config=self.tasks_config['tarefa_competencia4'], # type: ignore[index]
        )
    
    @task
    def tarefa_competencia5(self) -> Task:
        """Task: Avaliar Competência V (Proposta)"""
        return Task(
            config=self.tasks_config['tarefa_competencia5'], # type: ignore[index]
        )
    
    @task
    def tarefa_consolidacao(self) -> Task:
        """Task: Consolidar todas as avaliações"""
        return Task(
            config=self.tasks_config['tarefa_consolidacao'], # type: ignore[index]
            output_file='resultado_avaliacao.json'
        )

    # ========================================================================
    # CREW - ORQUESTRAÇÃO
    # ========================================================================
    
    @crew
    def crew(self) -> Crew:
        """
        Cria a Banca Examinadora com processo sequencial
        
        Fluxo:
        1. Avalia Competência 1
        2. Avalia Competência 2
        3. Avalia Competência 3
        4. Avalia Competência 4
        5. Avalia Competência 5
        6. Consolida resultados (recebe context das 5 anteriores)
        """
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            output_log_file=True,
            stream=False
        )
    
    # ========================================================================
    # MÉTODOS AUXILIARES
    # ========================================================================
    
    def preparar_inputs_com_rag(
        self, 
        redacao: str, 
        tema: str,
        textos_apoio: str = "",
        modo_rag: bool = True
    ) -> Dict[str, Any]:
        """
        Prepara os inputs para o crew, incluindo os manuais (RAG) e textos de apoio
        
        Args:
            redacao: Texto da redação a ser avaliada
            tema: Tema da redação
            textos_apoio: Textos de apoio fornecidos ao estudante (contexto do ENEM)
            modo_rag: True = com manuais, False = baseline
            
        Returns:
            Dict com todos os inputs interpolados
        """
        self.modo_rag = modo_rag
        
        # Se textos_apoio não fornecidos, usar mensagem padrão
        if not textos_apoio or textos_apoio.strip() == "":
            textos_apoio = "[Nenhum texto de apoio fornecido]"
        
        inputs = {
            'redacao': redacao,
            'tema': tema,
            'textos_apoio': textos_apoio,
            'manual_competencia1': self._carregar_manual(1),
            'manual_competencia2': self._carregar_manual(2),
            'manual_competencia3': self._carregar_manual(3),
            'manual_competencia4': self._carregar_manual(4),
            'manual_competencia5': self._carregar_manual(5),
        }
        
        return inputs
    
    def avaliar_redacao(
        self,
        redacao: str,
        tema: str,
        textos_apoio: str = "",
        modo_rag: bool = True
    ) -> Dict[str, Any] | None:
        """
        Método principal para avaliar uma redação
        
        Args:
            redacao: Texto completo da redação
            tema: Tema proposto
            textos_apoio: Textos de apoio fornecidos ao estudante (contexto)
            modo_rag: True = Experimento A (com RAG), False = Experimento B (baseline)
            
        Returns:
            Dict com resultado da avaliação
        """
        print("=" * 80)
        print(f"🎓 BANCA EXAMINADORA DIGITAL - Modo: {'RAG' if modo_rag else 'BASELINE'}")
        print("=" * 80)
        print(f"📝 Tema: {tema}")
        print(f"📄 Tamanho da redação: {len(redacao)} caracteres")
        print(f"📋 Textos de apoio: {'Sim' if textos_apoio else 'Não'}")
        print("=" * 80)
        
        # Preparar inputs com ou sem manuais
        inputs = self.preparar_inputs_com_rag(redacao, tema, textos_apoio, modo_rag)
        
        # Executar a crew
        resultado = self.crew().kickoff(inputs=inputs)
        
        print("=" * 80)
        print("✅ AVALIAÇÃO CONCLUÍDA")
        print("=" * 80)
        
        return resultado.json_dict # type: ignore
