from autogen import GroupChat

from agents import (
    create_immediate_fixer,
    create_incident_responder,
    create_mitigation_expert,
    create_rca_finder,
    create_scenario_explainer,
    create_summarizer,
    create_user_proxy,
)

# Each of the 6 specialists speaks this many times.
TURNS_PER_AGENT = 2


def _round_robin_skipping_proxy(last_speaker, groupchat):
    """Cycle through the specialists only; the stakeholder never gets a turn.

    The stakeholder is still a member of the group chat so that it receives
    every broadcast and its chat history is complete, but letting it speak
    would just inject empty auto-replies.
    """

    specialists = [
        agent
        for agent in groupchat.agents
        if agent.name != "stakeholder"
    ]

    if last_speaker not in specialists:
        return specialists[0]

    next_index = specialists.index(last_speaker) + 1

    return specialists[next_index % len(specialists)]


def create_groupchat():

    user_proxy = create_user_proxy()

    specialists = [
        create_scenario_explainer(),
        create_incident_responder(),
        create_rca_finder(),
        create_immediate_fixer(),
        create_mitigation_expert(),
        create_summarizer(),
    ]

    # Round 0 is the stakeholder's problem statement, then every specialist
    # speaks TURNS_PER_AGENT times.
    max_round = 1 + len(specialists) * TURNS_PER_AGENT

    return GroupChat(
        agents=[user_proxy] + specialists,
        messages=[],
        max_round=max_round,
        speaker_selection_method=_round_robin_skipping_proxy,
        allow_repeat_speaker=False,
    )
