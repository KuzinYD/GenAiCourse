import streamlit as st
import json
from utils.tools.agent import tools, client, MODEL
from utils.logger_helper import get_logger
from utils import db_helper, github_helper

logger = get_logger("genai_capstone_app")

# Page config
st.set_page_config(
    page_title="Wine Database Insights",
    page_icon="🍷",
    layout="wide"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "awaiting_ticket_details" not in st.session_state:
    st.session_state.awaiting_ticket_details = False

if "sample_query" not in st.session_state:
    st.session_state.sample_query = None

if "process_last_message" not in st.session_state:
    st.session_state.process_last_message = False

# Sidebar with business information
with st.sidebar:
    st.header("🍷 Wine Database Overview")
    
    try:
        # Get database stats
        with st.spinner("Loading database stats..."):
            total_red = db_helper.ask_database("SELECT COUNT(*) as total FROM red")
            total_white = db_helper.ask_database("SELECT COUNT(*) as total FROM white") 
            total_rose = db_helper.ask_database("SELECT COUNT(*) as total FROM rose")
            total_sparkling = db_helper.ask_database("SELECT COUNT(*) as total FROM sparkling")
            
            # Calculate total wines
            total_wines = total_red[0][0] + total_white[0][0] + total_rose[0][0] + total_sparkling[0][0]
            
            # Get unique countries
            countries_red = db_helper.ask_database("SELECT COUNT(DISTINCT Country) as countries FROM red WHERE Country IS NOT NULL AND Country != ''")
            countries_white = db_helper.ask_database("SELECT COUNT(DISTINCT Country) as countries FROM white WHERE Country IS NOT NULL AND Country != ''")
            countries_rose = db_helper.ask_database("SELECT COUNT(DISTINCT Country) as countries FROM rose WHERE Country IS NOT NULL AND Country != ''")
            countries_sparkling = db_helper.ask_database("SELECT COUNT(DISTINCT Country) as countries FROM sparkling WHERE Country IS NOT NULL AND Country != ''")
            
            # Approximate total unique countries (may have some overlap)
            total_countries = max(countries_red[0][0], countries_white[0][0], countries_rose[0][0], countries_sparkling[0][0])
            
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
    
    # Sample queries
    st.subheader("💡 Try These Queries:")
    sample_queries = [
        "Show me French red wines under $50",
        "What are the highest rated white wines?", 
        "List rosé wines from Italy with high ratings",
        "Show me the most expensive sparkling wines",
        "Find wines from Bordeaux region",
        "What's the average price of German wines?",
        "Show me wines with rating above 4.5"
    ]
    
    for i, query in enumerate(sample_queries):
        if st.button(query, key=f"sample_{i}"):
            st.session_state.sample_query = query
            st.rerun()
    
    st.divider()
    
    # Contact info
    st.subheader("📞 Need Help?")
    st.info("Ask me to 'create a support ticket' for human assistance!")
    
    # Additional database insights
    try:
        st.subheader("🏆 Quick Stats")
        
        # Get some interesting stats
        highest_rated = db_helper.ask_database("""
            SELECT Name, Rating, Country, Price FROM red 
            WHERE Rating IS NOT NULL AND Rating != '' 
            ORDER BY CAST(Rating AS DECIMAL) DESC LIMIT 1
        """)
        
        most_expensive = db_helper.ask_database("""
            SELECT Name, Price, Country FROM red 
            WHERE Price IS NOT NULL AND Price != '' 
            ORDER BY CAST(Price AS DECIMAL) DESC LIMIT 1
        """)
        
        if highest_rated and highest_rated[0]:
            wine = highest_rated[0]
            st.success(f"⭐ Highest Rated: **{wine[0]}** ({wine[1]}/5) from {wine[2]}")
            
        if most_expensive and most_expensive[0]:
            wine = most_expensive[0]
            st.success(f"💰 Most Expensive: **{wine[0]}** (${wine[1]}) from {wine[2]}")
            
    except Exception as e:
        logger.error(f"Quick stats error: {e}")

# Main chat interface
st.title("🍷 Wine Database Chat Assistant")
st.caption("🤖 Ask me anything about our wine collection!")

# Handle sample query selection
if st.session_state.sample_query:
    # Add sample query as user message
    sample_text = st.session_state.sample_query
    st.session_state.messages.append({"role": "user", "content": sample_text})
    st.session_state.sample_query = None
    
    # Show the user message immediately
    with st.chat_message("user"):
        st.markdown(sample_text)
    
    # Trigger processing by setting a flag and rerunning
    st.session_state.process_last_message = True
    st.rerun()

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle user input or process last message
prompt = None
if user_input := st.chat_input("What is up?"):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    prompt = user_input

# Also process if we have a flag set (from sample queries)
elif st.session_state.process_last_message and st.session_state.messages:
    prompt = st.session_state.messages[-1]["content"]
    st.session_state.process_last_message = False

# Process the prompt if we have one
if prompt:

    # Check if we're waiting for ticket details
    if st.session_state.awaiting_ticket_details:
        # User provided ticket details, now create the ticket
        with st.chat_message("assistant"):
            with st.spinner("Creating your support ticket..."):
                try:
                    ticket = github_helper.create_support_ticket(
                        title="User Support Request",
                        body=prompt
                    )
                    response_msg = f"✅ I've created a support ticket for you! You can track it here: {ticket['url']}\n\nOur team will review your request and get back to you soon."
                except Exception as e:
                    logger.error(f"GitHub error: {e}")
                    response_msg = f"❌ I'm sorry, there was an error creating your support ticket: {str(e)}"
                
                st.markdown(response_msg)
                st.session_state.messages.append({"role": "assistant", "content": response_msg})
        
        st.session_state.awaiting_ticket_details = False
        st.rerun()
        
    else:
        # Check if user wants to create a support ticket
        if any(keyword in prompt.lower() for keyword in ["support", "ticket", "help", "issue", "problem"]):
            response_msg = "I'd be happy to help you create a support ticket! 🎫\n\nPlease describe your issue or question in detail. Include:\n- What problem you're experiencing\n- What you were trying to do\n- Any error messages you've seen\n\nJust type your description and I'll create the ticket for you."
            
            st.session_state.messages.append({"role": "assistant", "content": response_msg})
            with st.chat_message("assistant"):
                st.markdown(response_msg)
            
            st.session_state.awaiting_ticket_details = True
            st.rerun()
        
        else:
            # Normal AI response with progress indicator
            with st.chat_message("assistant"):
                with st.spinner("🤔 Thinking..."):
                    # Get AI response
                    response = client.chat.completions.create(
                        model=MODEL,
                        messages=st.session_state.messages,
                        tools=tools,
                        tool_choice="auto"
                    )

                assistant_message = response.choices[0].message
                
                # Handle tool calls
                if assistant_message.tool_calls:
                    # Add assistant message with tool calls (but don't show to user yet)
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": assistant_message.content or "",
                        "tool_calls": [{"id": tc.id, "type": tc.type, "function": {"name": tc.function.name, "arguments": tc.function.arguments}} for tc in assistant_message.tool_calls]
                    })
                    
                    # Execute each tool call
                    for tool_call in assistant_message.tool_calls:
                        function_name = tool_call.function.name
                        function_args = json.loads(tool_call.function.arguments)
                        
                        # Show progress for tool execution
                        with st.spinner(f"🔍 Searching database..."):
                            # Execute the appropriate function
                            if function_name == "ask_database":
                                try:
                                    query = function_args["query"]
                                    db_result = db_helper.ask_database(query)
                                    # Don't show raw results to user - just log them
                                    logger.info(f"Database query returned {len(db_result)} results")
                                    tool_result = f"Database query executed successfully. Found {len(db_result)} results."
                                except Exception as e:
                                    logger.error(f"Database error: {e}")
                                    # Create support ticket automatically
                                    ticket = github_helper.create_support_ticket(
                                        title="Database Query Error",
                                        body=f"Database query failed.\n\nQuery: {query}\n\nError: {str(e)}"
                                    )
                                    tool_result = f"Database query failed. Support ticket created: {ticket['url']}"
                        
                        # Add tool result to messages (for AI context, not user display)
                        st.session_state.messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": str(db_result) if function_name == "ask_database" else tool_result
                        })
                    
                    # Get final response after tool execution
                    with st.spinner("✨ Preparing response..."):
                        final_response = client.chat.completions.create(
                            model=MODEL,
                            messages=st.session_state.messages,
                            tools=tools,
                            tool_choice="auto"
                        )
                        
                        final_message = final_response.choices[0].message.content
                        st.session_state.messages.append({"role": "assistant", "content": final_message})
                        st.markdown(final_message)
                
                else:
                    # No tool calls, just add the regular response
                    st.session_state.messages.append({"role": "assistant", "content": assistant_message.content})
                    st.markdown(assistant_message.content)