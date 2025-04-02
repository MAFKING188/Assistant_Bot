import os
import streamlit as st
from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
import logging
from datetime import datetime
import time
import database_manager

#TESTING

# Set up logging
logging.basicConfig(
    filename='chatbot.log',
    level=logging.DEBUG,
    format='%(asctime)s:%(levelname)s:%(message)s'
)

# Load API key from environment variable
def load_api_key():
    """Load the GROQ API key from environment variables."""
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        logging.error("GROQ_API_KEY is not set.")
        st.error("API key not found. Please set the GROQ_API_KEY environment variable.")
        return None
    return api_key

# Initialize chat client
def initialize_chat(api_key):
    """Initialize the Groq chat client."""
    try:
        return ChatGroq(groq_api_key=api_key, model_name='llama-3.3-70b-versatile')
    except Exception as e:
        logging.error(f"Failed to initialize Groq chat: {e}")
        st.error("Failed to connect to the chat service. Please try again later.")
        return None

# Set up conversation memory
def setup_chat_memory(session_id):
    """Set up conversation memory for storing chat history."""
    conversation_history = database_manager.get_conversation_history(session_id)
    return conversation_history

# Build prompt with system message and user input
def build_prompt(system_message, user_input, conversation_history):
    """Build the prompt with system message and user input."""
    messages = [
        SystemMessage(content=system_message),
    ]
    for user, assistant in conversation_history:
        # Wrap each message with HumanMessage
        messages.append(HumanMessage(content=user))
        messages.append(HumanMessage(content=assistant))  # Assuming 'assistant' is the response
    messages.append(HumanMessage(content=user_input))  # User's current input
    return ChatPromptTemplate.from_messages(messages)

# Process user input and generate chatbot response
def process_user_input(user_input, groq_chat, conversation_history):
    """Process user input and return the chatbot's response."""
    system_prompt = (
        "You are a highly knowledgeable, professional, and objective life assistant, capable of providing expert guidance across a wide range of subjects. Your areas of expertise span all possible topics, including but not limited to education, financial planning, health advice, and current events.\n\n"
        "Your primary objective is to offer personalized, actionable advice that is tailored to each user's unique needs and preferences. Before providing any advice, you will ask clarifying questions to ensure that you fully understand the user's needs and that the response you give aligns with their expectations. If you're ever uncertain about the user's intent or if a situation requires nuanced guidance, always ask for additional context before proceeding with an answer.\n\n"
        "You strive to keep your responses clear and concise while ensuring that they remain well-informed and fact-based. Adapt your tone and content based on the conversation history and any preferences the user may have shared. Additionally, ensure that you include relevant resources or citations when appropriate, and guide the user toward further exploration if it helps them.\n\n"
        "You are respectful of boundaries and will not give advice on sensitive topics such as legal matters, sensitive health issues, or anything that falls outside your area of expertise. If unsure, you will ask for clarification from the user before proceeding.\n\n"
        "Remember, you are here to support the user and make sure your advice is actionable, trustworthy, and relevant.\n"
    )

    prompt = build_prompt(system_prompt, user_input, conversation_history)

    try:
        conversation = LLMChain(
            llm=groq_chat,
            prompt=prompt,
            verbose=False,
        )
        return conversation.predict()
    except Exception as e:
        logging.error(f"Error during conversation: {e}")
        st.error("An error occurred while processing your request. Please try again.")
        return None

# Render chat interface
def render_chat_interface():
    """Render the chat interface."""
    st.title("MAFULETI: Your Life Assistant Chatbot")
    st.markdown(
        """ Hello! I'm MAFULETI, your intelligent life assistant. I can help you with education, finance, health, and current events. Think of me as your personal advisor, providing insights and support across all areas of your life. """
    )

    st.write("### Chat with MAFKING")

# Handle user input
def handle_user_input(groq_chat, session_id):
    """Handle user input and update chat history."""
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = setup_chat_memory(session_id)

    if 'user_input' not in st.session_state:
        st.session_state.user_input = ""

    def render_text_area():
        user_input = st.text_area("Ask a question:", value=st.session_state.user_input, height=200, key="text_area")
        return user_input

    user_input = render_text_area()

    if st.button("Send"):
        if user_input.strip():
            logging.info(f"User: {user_input}")
            response = process_user_input(user_input, groq_chat, st.session_state.conversation_history)
            if response:
                logging.info(f"Assistant: {response}")
                database_manager.log_interaction(session_id, user_input, response)
                database_manager.log_chat_message(session_id, user_input, "user")
                database_manager.log_chat_message(session_id, response, "ai")
                st.session_state.conversation_history.append((user_input, response))
                st.session_state.conversation_history = st.session_state.conversation_history[-10:]  # Limit chat history to 10 messages
                st.session_state.user_input = ""
        else:
            st.error("Please enter a valid question.")

    if st.button("Clear Conversation History"):
        st.session_state.conversation_history = []
        st.session_state.user_input = ""
        database_manager.clear_conversation_history(session_id)

    st.write("### Conversation History:")
    for user_input, response in reversed(st.session_state.conversation_history):
        st.write(f"**You:** {user_input}")
        st.write(f"**Assistant:** {response}")

# Main function
def main():
    """Main function to run the Streamlit app."""
    # Initialize session state
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []

    api_key = load_api_key()
    if api_key is None:
        return

    groq_chat = initialize_chat(api_key)
    if groq_chat is None:
        return

    session_id = database_manager.get_session_id()
    render_chat_interface()
    handle_user_input(groq_chat, session_id)

if __name__ == "__main__":
    main()
