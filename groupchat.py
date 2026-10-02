from autogen import GroupChat, GroupChatManager
from agents import  create_immediate_fixer,create_incident_responder,create_mitigation_expert,create_rca_finder,create_scenario_explainer,create_summarizer


def create_groupchat():
    scenario_explainer = create_scenario_explainer()
    incident_responder = create_incident_responder()
    rca_finder = create_rca_finder()
    immediate_fixer = create_immediate_fixer()
    mitigation_expert = create_mitigation_expert()
    summarizer = create_summarizer()

    return GroupChat(
            agents = [scenario_explainer,incident_responder,rca_finder,immediate_fixer,mitigation_expert,summarizer],
            messages= [],
            max_round=2
        )