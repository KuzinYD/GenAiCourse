import streamlit as st
from utils.logger_helper import get_logger
from capstone_i.utils.tools.agent import MODEL, run_agent_conversation
from capstone_i.utils.db_helper import ask_database


logger = get_logger("genai_capstone_app")

st.set_page_config(
    page_title="Wine Database Insights",
    page_icon="🍷",
    layout="centered"
)

# Sidebar with business information
with st.sidebar:
    st.header("🍷 Wine Database Overview")

    try:
        # Get database stats
        with st.spinner("Loading database stats..."):
            total_red = ask_database("SELECT COUNT(*) as total FROM red")
            total_white = ask_database("SELECT COUNT(*) as total FROM white")
            total_rose = ask_database("SELECT COUNT(*) as total FROM rose")
            total_sparkling = ask_database("SELECT COUNT(*) as total FROM sparkling")

            # Calculate total wines
            total_wines = total_red[0][0] + total_white[0][0] + total_rose[0][0] + total_sparkling[0][0]

            # Get unique countries
            countries_red = ask_database(
                "SELECT COUNT(DISTINCT Country) as countries FROM red WHERE Country IS NOT NULL AND Country != ''")
            countries_white = ask_database(
                "SELECT COUNT(DISTINCT Country) as countries FROM white WHERE Country IS NOT NULL AND Country != ''")
            countries_rose = ask_database(
                "SELECT COUNT(DISTINCT Country) as countries FROM rose WHERE Country IS NOT NULL AND Country != ''")
            countries_sparkling = ask_database(
                "SELECT COUNT(DISTINCT Country) as countries FROM sparkling WHERE Country IS NOT NULL AND Country != ''")

            # Approximate total unique countries (may have some overlap)
            total_countries = max(countries_red[0][0], countries_white[0][0], countries_rose[0][0],
                                  countries_sparkling[0][0])

            # Display metrics
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Wines", f"{total_wines:,}")
                st.metric("Red Wines", f"{total_red[0][0]:,}")
            with col2:
                st.metric("Countries", f"{total_countries}+")
                st.metric("White Wines", f"{total_white[0][0]:,}")

            # Additional wine types
            col3, col4 = st.columns(2)
            with col3:
                st.metric("Rosé Wines", f"{total_rose[0][0]:,}")
            with col4:
                st.metric("Sparkling", f"{total_sparkling[0][0]:,}")

    except Exception as e:
        st.error("Unable to load database stats")
        logger.error(f"Stats error: {e}")

    st.divider()

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Hi there! How can I help you today?"}
    ]

st.sidebar.title("⚙️ Settings")
st.sidebar.markdown(f"Using internal model: **{MODEL or 'not set'}**")

# Main chat interface
st.title("🍷 Wine Database Chat Assistant")
st.caption("🤖 Ask me anything about our wine collection!")

for msg in st.session_state.messages:
    with st.chat_message("user" if msg["role"] == "user" else "assistant"):
        st.markdown(msg["content"])

if prompt := st.chat_input("Type your message..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            reply = run_agent_conversation(st.session_state.messages)
            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
