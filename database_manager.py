import mysql.connector
from mysql.connector import pooling, Error
import logging
import streamlit as st

# Set up logging
logging.basicConfig(
    filename='chatbot.log',
    level=logging.DEBUG,
    format='%(asctime)s:%(levelname)s:%(message)s'
)

# Database connection settings
config = {
    'host': 'localhost',
    'user': 'MAFULETI',
    'password': 'MYSQL@ROOT@188@lqsym',
    'database': 'CROQ_ASSISTANT'
}

# Create a connection pool
pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=5,
    **config
)

# Function to get a connection from the pool
def get_connection():
    return pool.get_connection()

# Function to create a new session
def create_session():
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO sessions (user_id) VALUES (1)")
        connection.commit()
        return cursor.lastrowid
    except Error as e:
        logging.error(f"Error creating session: {e}")
    finally:
        cursor.close()
        connection.close()

# Function to log an interaction
def log_interaction(session_id, user_input, ai_response):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO interactions (session_id, user_input, ai_response) VALUES (%s, %s, %s)",
            (session_id, user_input, ai_response)
        )
        connection.commit()
    except Error as e:
        logging.error(f"Error logging interaction: {e}")
    finally:
        cursor.close()
        connection.close()

# Function to log a chat message
def log_chat_message(session_id, message, role):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO chat_history (session_id, message, role) VALUES (%s, %s, %s)",
            (session_id, message, role)
        )
        connection.commit()
    except Error as e:
        logging.error(f"Error logging chat message: {e}")
    finally:
        cursor.close()
        connection.close()

# Function to get the current session ID
def get_session_id():
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM sessions WHERE end_time IS NULL")
        session_id = cursor.fetchone()
        if session_id:
            return session_id[0]
        else:
            return create_session()
    except Error as e:
        logging.error(f"Error getting session ID: {e}")
    finally:
        cursor.close()
        connection.close()

# Function to retrieve conversation history
def get_conversation_history(session_id):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT user_input, ai_response FROM interactions WHERE session_id = %s", (session_id,))
        conversation_history = cursor.fetchall()
        return conversation_history
    except Error as e:
        logging.error(f"Error retrieving conversation history: {e}")
    finally:
        cursor.close()
        connection.close()

# Function to render the chat interface
def render_chat_interface():
    st.title("Chatbot Interface")
    user_input = st.text_input("Enter your message:")
    return user_input

# Function to handle user input
def handle_user_input(session_id):
    user_input = render_chat_interface()
    if st.button("Send"):
        ai_response = "This is a response from the AI."
        log_interaction(session_id, user_input, ai_response)
        log_chat_message(session_id, user_input, "user")
        log_chat_message(session_id, ai_response, "ai")
        st.write("AI Response: ", ai_response)

# Main function
def main():
    # Initialize session state
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []

    # Get the current session ID
    session_id = get_session_id()

    # Render interface and handle user input
    handle_user_input(session_id)

if __name__ == "__main__":
    main()
