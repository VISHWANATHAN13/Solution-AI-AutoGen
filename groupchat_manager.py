from autogen import GroupChatManager

from llm import get_llm


def create_groupchat_manager(groupchat):
    """Wrap an existing GroupChat.

    The manager must share the *same* GroupChat instance - and therefore the
    same agent objects - as the caller. Building a second GroupChat here would
    leave the initiating agent outside the manager's group, so no agent would
    ever be given a turn.
    """

    return GroupChatManager(
        groupchat=groupchat,
        llm_config=get_llm(),
        human_input_mode="NEVER",
    )
