from dotenv import load_dotenv
load_dotenv()

from langchain_openai import OpenAI
import streamlit as st

from agent import agent

st.set_page_config(
    page_title="RAG with Github Issues Integration",
    page_icon="🤖",
    layout="centered"
)

# Sidebar with business information
with st.sidebar:
    st.header("App overview")

    st.divider()

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Hi there! How can I help you today?"}
    ]

st.sidebar.title("⚙️ Settings")

# Main chat interface
st.title("🤖 RAG Chat Assistant")
st.caption("🤖 Ask me anything about knowledge base I am trained on")

for msg in st.session_state.messages:
    with st.chat_message("user" if msg["role"] == "user" else "assistant"):
        st.markdown(msg["content"])

if prompt := st.chat_input("Type your message..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Show assistant reply with container to avoid "ghost" messages
    with st.chat_message("assistant"):
        with st.container():
            with st.spinner("Thinking..."):
                    # Pass the full message history to the agent
                    result = agent.invoke({"messages": st.session_state.messages})

                    # If result is a list of messages, get the last AI message's content
                    if hasattr(result, "content"):
                        reply = result.content
                    elif isinstance(result, dict) and "messages" in result:
                        # Defensive: get last AI message from the list
                        ai_msgs = [m for m in result["messages"] if getattr(m, "type", None) == "ai"]
                        reply = ai_msgs[-1].content if ai_msgs else str(result)
                    else:
                        reply = str(result)

            st.markdown(reply)
                # Append to chat history *after* rendering to avoid flicker/duplication
            st.session_state.messages.append({"role": "assistant", "content": reply})