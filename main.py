import gradio as gr

from groupchat import create_groupchat
from groupchat_manager import create_groupchat_manager


# =========================================================
# AUTOGEN DRIVER
# =========================================================

def run_autogen(user_message):

    if not user_message or not user_message.strip():
        raise ValueError("Can't process empty message")

    # Create AutoGen components
    groupchat = create_groupchat()
    manager = create_groupchat_manager()

    conversation = []

    print("\n" + "=" * 60)
    print("AUTOGEN MULTI-AGENT EXECUTION")
    print("=" * 60)

    print(f"\nUser: {user_message}")

    # -----------------------------------------------------
    # Run all agents
    # -----------------------------------------------------

    for agent in groupchat.agents:

        print(f"\n--- {agent.name} ---")

        response = agent.initiate_chat(
            manager,
            message=user_message
        )

        print(f"{agent.name}: {response}")

        conversation.append({
            "agent": agent.name,
            "response": str(response)
        })

    # -----------------------------------------------------
    # Store conversation
    # -----------------------------------------------------

    file_name = "conversation.txt"

    with open(
        file_name,
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

    print(f"\nConversation stored in {file_name}")

    # -----------------------------------------------------
    # Final response
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

    if not user_message or not user_message.strip():
        return (
            history,
            "",
            "Please enter a problem."
        )

    try:

        # Run AutoGen
        final_response, conversation = run_autogen(
            user_message
        )

        history = history or []

        # Add user message
        history.append({
            "role": "user",
            "content": user_message
        })

        # Add assistant response
        history.append({
            "role": "assistant",
            "content": final_response
        })

        # -------------------------------------------------
        # Build Agent Execution Trace
        # -------------------------------------------------

        trace = "## 🔍 Agent Execution Trace\n\n"

        for index, item in enumerate(
            conversation,
            start=1
        ):

            trace += (
                f"### Agent {index}: {item['agent']}\n\n"
                f"{item['response']}\n\n"
                "---\n\n"
            )

        return (
            history,
            "",
            trace
        )

    except Exception as e:

        error_message = (
            f"### ❌ Error\n\n"
            f"`{str(e)}`"
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
        # Agent Trace
        # -------------------------------------------------

        gr.Markdown(
            "## 🔍 Agent Execution Trace"
        )

        agent_trace = gr.Markdown(
            value="No agent execution yet."
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

        # -------------------------------------------------
        # Clear button
        # -------------------------------------------------

        clear_button = gr.Button(
            "Clear Conversation"
        )

        # -------------------------------------------------
        # Send button
        # -------------------------------------------------

        send_button.click(
            fn=chat,
            inputs=[
                user_input,
                chatbot
            ],
            outputs=[
                chatbot,
                user_input,
                agent_trace
            ]
        )

        # -------------------------------------------------
        # Enter / Submit
        # -------------------------------------------------

        user_input.submit(
            fn=chat,
            inputs=[
                user_input,
                chatbot
            ],
            outputs=[
                chatbot,
                user_input,
                agent_trace
            ]
        )

        # -------------------------------------------------
        # Clear
        # -------------------------------------------------

        clear_button.click(
            fn=lambda: (
                [],
                "",
                "No agent execution yet."
            ),
            inputs=[],
            outputs=[
                chatbot,
                user_input,
                agent_trace
            ]
        )

    # -----------------------------------------------------
    # Launch
    # -----------------------------------------------------

    demo.launch()


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":
    start_ui()