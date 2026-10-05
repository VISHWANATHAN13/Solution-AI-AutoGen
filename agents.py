from autogen import AssistantAgent, UserProxyAgent

from llm import get_llm

llm = get_llm()


def _assistant(name, system_message, description):
    """All specialists share the same wiring: LLM only, never ask a human."""

    return AssistantAgent(
        name=name,
        llm_config=llm,
        system_message=system_message,
        description=description,
        human_input_mode="NEVER",
        code_execution_config=False,
    )


def create_scenario_explainer():
    return _assistant(
        name="Scenario_explainer",
        description="Explains the current scenario and the process involved.",
        system_message=(
            "You are the Scenario Explainer.\n"
            "Describe the current scenario and the process in which the "
            "problem occurred: the systems involved, the actors, and the "
            "normal expected behaviour.\n"
            "Keep it factual, use short markdown bullets, and stay under "
            "200 words. Do not perform root cause analysis - a later agent "
            "owns that."
        ),
    )


def create_incident_responder():
    return _assistant(
        name="incident_responder",
        description="States clearly what the incident is and its impact.",
        system_message=(
            "You are the Incident Responder.\n"
            "State clearly what the incident is, when it surfaced, who is "
            "affected, and the severity. Call out the business and security "
            "impact explicitly.\n"
            "Use short markdown bullets and stay under 200 words. Do not "
            "propose fixes - later agents own that."
        ),
    )


def create_rca_finder():
    return _assistant(
        name="rca_finder",
        description="Performs root cause analysis on the incident.",
        system_message=(
            "You are the Root Cause Analyst.\n"
            "Build on what the previous agents said. Work backwards from the "
            "symptom to the most likely root cause, listing the contributing "
            "factors you ruled in and out.\n"
            "End with a single line: 'Root cause: <one sentence>'.\n"
            "Use short markdown bullets and stay under 250 words."
        ),
    )


def create_immediate_fixer():
    return _assistant(
        name="immediate_fixer",
        description="Proposes immediate containment actions for the client.",
        system_message=(
            "You are the Immediate Fixer.\n"
            "Given the root cause above, list the immediate containment "
            "actions to take now, in priority order. For each one give the "
            "action, the owner role, and the expected time to complete.\n"
            "Use a numbered markdown list and stay under 200 words."
        ),
    )


def create_mitigation_expert():
    return _assistant(
        name="mitigation_expert",
        description="Proposes long-term mitigation and prevention measures.",
        system_message=(
            "You are the Mitigation Expert.\n"
            "Propose the long-term measures that stop this class of problem "
            "from recurring: controls, tests, monitoring, and process "
            "changes. Distinguish short-term hardening from structural "
            "fixes.\n"
            "Use short markdown bullets and stay under 250 words."
        ),
    )


def create_summarizer():
    return _assistant(
        name="summarizer",
        description="Summarises the whole discussion for stakeholders.",
        system_message=(
            "You are the Summarizer.\n"
            "Write the stakeholder-facing summary of everything discussed "
            "above, using these markdown sections:\n"
            "**Incident** / **Root cause** / **Impact** / "
            "**Immediate actions** / **Long-term measures** / "
            "**Open questions**\n"
            "Be concrete and reference what the other agents actually said. "
            "Stay under 350 words."
        ),
    )


def create_user_proxy():
    """Seeds the conversation. Never speaks again and never blocks on input."""

    return UserProxyAgent(
        name="stakeholder",
        description="The stakeholder who raised the problem.",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=0,
        code_execution_config=False,
        default_auto_reply="",
        llm_config=False,
    )
