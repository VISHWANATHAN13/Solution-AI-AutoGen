import gradio as gr

from groupchat import create_groupchat
from groupchat_manager import create_groupchat_manager

CONVERSATION_LOG = "conversation.txt"


# =========================================================
# HELPERS
# =========================================================

def message_text(message):
    """Pull the plain text out of an AutoGen message.

    `content` is usually a string, but can be a list of content blocks when
    tool calls or multi-modal parts are involved.
    """

    content = message.get("content")

    if content is None:
        return ""

    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):

        parts = [
            block.get("text", "")
            for block in content
            if isinstance(block, dict)
        ]

        return "\n".join(part for part in parts if part).strip()

    return str(content).strip()


# =========================================================
# AUTOGEN DRIVER
# =========================================================

def run_autogen(user_message):

    if not user_message or not user_message.strip():
        raise ValueError("Can't process empty message")

    # The manager has to share this exact GroupChat instance.
    groupchat = create_groupchat()
    manager = create_groupchat_manager(groupchat)

    # agents[0] is the stakeholder proxy that seeds the discussion.
    user_proxy = groupchat.agents[0]

    print("\n" + "=" * 60)
    print("AUTOGEN MULTI-AGENT EXECUTION")
    print("=" * 60)
    print(f"\nUser: {user_message}\n")

    # -----------------------------------------------------
    # One group conversation, not one chat per agent
    # -----------------------------------------------------

    user_proxy.initiate_chat(
        manager,
        message=user_message,
        clear_history=True
    )

    # -----------------------------------------------------
    # groupchat.messages is the authoritative transcript.
    # The manager never sends the discussion back to the
    # initiator, so the returned ChatResult is not enough.
    # Message 0 is the stakeholder's own prompt, so skip it.
    # -----------------------------------------------------

    conversation = []

    for message in groupchat.messages[1:]:

        text = message_text(message)

        if not text:
            continue

        agent_name = message.get("name") or message.get("role", "agent")

        conversation.append({
            "agent": agent_name,
            "response": text
        })

        print(f"--- {agent_name} ---")
        print(text + "\n")

    # -----------------------------------------------------
    # Store conversation
    # -----------------------------------------------------

    with open(
        CONVERSATION_LOG,
        "a",
        encoding="utf-8"
    ) as f:

        f.write("\n")
        f.write("=" * 60 + "\n")
        f.write(f"USER: {user_message}\n")
        f.write("=" * 60 + "\n")

        for item in conversation:

            f.write(
                f"{item['agent']}:\n"
                f"{item['response']}\n\n"
            )

    print(f"Conversation stored in {CONVERSATION_LOG}")

    # -----------------------------------------------------
    # Final response - the summarizer's last word
    # -----------------------------------------------------

    if conversation:

        final_response = conversation[-1]["response"]

    else:

        final_response = (
            "The agents did not produce a response."
        )

    return final_response, conversation


# =========================================================
# GRADIO CALLBACK
# =========================================================

def chat(user_message, history):

    history = history or []

    if not user_message or not user_message.strip():
        return (
            history,
            "",
            "Please enter a problem."
        )

    try:

        final_response, conversation = run_autogen(
            user_message
        )

        history = history + [
            {
                "role": "user",
                "content": user_message
            },
            {
                "role": "assistant",
                "content": final_response
            }
        ]

        # -------------------------------------------------
        # Build Agent Execution Trace
        # -------------------------------------------------

        turn_counts = {}
        trace_parts = []

        for item in conversation:

            agent_name = item["agent"]

            turn_counts[agent_name] = turn_counts.get(agent_name, 0) + 1

            trace_parts.append(
                f"### {agent_name} "
                f"(turn {turn_counts[agent_name]})\n\n"
                f"{item['response']}\n"
            )

        trace = "\n---\n\n".join(trace_parts) or "No agent output."

        return (
            history,
            "",
            trace
        )

    except Exception as e:

        error_message = (
            f"### Error\n\n"
            f"`{type(e).__name__}: {e}`"
        )

        return (
            history,
            "",
            error_message
        )


# =========================================================
# GRADIO UI
# =========================================================

def start_ui():

    with gr.Blocks(
        title="AutoGen Multi-Agent Assistant"
    ) as demo:

        # -------------------------------------------------
        # Header
        # -------------------------------------------------

        gr.Markdown(
            """
            # 🤖 AutoGen Multi-Agent Assistant

            ### Multi-Agent Problem Solving System

            **6 Agents × 2 Turns**

            Submit a problem and observe how the
            multi-agent system processes it.
            """
        )

        # -------------------------------------------------
        # Chatbot
        # -------------------------------------------------

        chatbot = gr.Chatbot(
            label="Conversation",
            height=450
        )

        # -------------------------------------------------
        # User Input
        # -------------------------------------------------

        with gr.Row():

            user_input = gr.Textbox(
                placeholder="State your problem here...",
                label="Your Request",
                scale=8,
                lines=3
            )

            send_button = gr.Button(
                "Send",
                variant="primary",
                scale=1
            )

        clear_button = gr.Button(
            "Clear Conversation"
        )

        # -------------------------------------------------
        # Agent Trace
        # -------------------------------------------------

        with gr.Accordion(
            "🔍 Agent Execution Trace",
            open=True
        ):

            agent_trace = gr.Markdown(
                value="No agent execution yet."
            )

        # -------------------------------------------------
        # Wiring
        # -------------------------------------------------

        chat_inputs = [user_input, chatbot]
        chat_outputs = [chatbot, user_input, agent_trace]

        send_button.click(
            fn=chat,
            inputs=chat_inputs,
            outputs=chat_outputs
        )

        user_input.submit(
            fn=chat,
            inputs=chat_inputs,
            outputs=chat_outputs
        )

        clear_button.click(
            fn=lambda: (
                [],
                "",
                "No agent execution yet."
            ),
            inputs=[],
            outputs=chat_outputs
        )

    demo.launch()


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":
    start_ui()
