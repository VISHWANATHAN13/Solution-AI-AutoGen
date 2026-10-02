from autogen import AssistantAgent
from llm import get_llm

llm = get_llm()

# def create_multi_agent_system():

def create_scenario_explainer():
    return AssistantAgent(
        name = "Scenario_explainer",
        llm_config =llm,
        system_message="First, Explain the current scenario in the process"
    )

def create_incident_responder():
    return AssistantAgent(
        name = "incident_responder",
        llm_config=llm,
        system_message="Clearly explain the incident occured in the problem"
    )

def create_rca_finder():
    return AssistantAgent(
        name = "rca_finder",
        llm_config=llm,
        system_message="Perform Root Cause Analysis and report the root cause of the incident."
    )

def create_immediate_fixer():
    return AssistantAgent(
        name = "immediate_fixer",
        llm_config=llm,
        system_message="Suggest the immediate fix for the problem to address the client"
    )

def create_mitigation_expert():
    return AssistantAgent(
        name = "mitigation_expert",
        llm_config=llm,
        system_message="Find the mitigation steps and report to solve the problem occured."
    )

def create_summarizer():
    return AssistantAgent(
        name = "summarizer",
        llm_config=llm,
        system_message="Summarize all the content and finish the conversaion with the stakeholkder."
    )


