from groupchat import create_groupchat
from autogen import GroupChatManager
from llm import get_llm

def create_groupchat_manager():

    llm = get_llm()
    group_chat = create_groupchat()

    return GroupChatManager(
        groupchat=group_chat,
        llm_config = llm
    )