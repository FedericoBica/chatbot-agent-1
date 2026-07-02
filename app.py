from agentic_chatbot_backend import chatbot, get_all_threads
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import streamlit as st
import uuid

def generate_thread_id():
    return str(uuid.uuid4())

# Add a new thread ID to the conversation list
def add_thread(thread_id):
     # Prevent the same thread from being added multiple times
     if thread_id not in st.session_state["chat_threads"]:
         st.session_state["chat_threads"].append(thread_id)

# Create a completely new chat conversation
def reset_chat():
    # Generate and assign a new thread ID
    st.session_state['thread_id'] = generate_thread_id()
    # Clear the current chat messages from the UI
    st.session_state['message_history'] = []
    # Add the new thread to the conversation list
    add_thread(st.session_state['thread_id'])

def load_conversation(thread_id):
    state = chatbot.get_state(
        config={
            'configurable': {
                'thread_id': thread_id
            }
        }
    )

    return state.values.get('messages',[])

# Streamlit recorre el script en cada interacción.
# Por eso guardamos el historial en session_state.
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

# create a list for storing all conversation thread IDs
if "chat_threads" not in st.session_state:
    st.session_state["chat_threads"] = get_all_threads()

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread_id()

# add the current thread to the conversation list
add_thread(st.session_state['thread_id'])

st.title("Agentic CHatbot with LAngraph")

# ======================= Sidebar threading feature ========

st.sidebar.title("My conversations")

if st.sidebar.button('New Chat'):
    reset_chat()
    st.rerun()

# Display all conversation threads in reverse order
# This shows the newest conversation first
for thread_id in st.session_state["chat_threads"][::-1]:
     # Create one sidebar button for every conversation
    if st.sidebar.button(str(thread_id), key=thread_id):
        # Set the selected thread as the current thread
        st.session_state["thread_id"] = thread_id
        # Load the messages saved under the selected thread
        messages = load_conversation(thread_id)
        # Load the messages saved under the selected thread into Streamlit's required message format
        temp_messages = [] 

        # Loop through all saved messages
        for message in messages:
            # Check whether the message was sent by the user
            if isinstance(message, HumanMessage):
                role = 'user'
            # Check whether the message was sent by the AI
            elif isinstance(message, AIMessage):
                role = 'assistant'
            # Ignore other message types, such as ToolMessage
            else:
                continue
            # Convert the LangChain message into a dictionary
            temp_messages.append({
                "role": role,
                "content": message.content
            })
        # Replace the current UI history with the selected conversation
        st.session_state["message_history"] = temp_messages

        # Rerun the application to display the loaded messages
        st.rerun()

# ========================= Main chat interface =========================

# Mostrar mensajes anteriores
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

# Input del usuario
user_input = st.chat_input('Type here')

# Si el usuario escribió algo
if user_input:
    # Guardar mensaje del usuario
    st.session_state['message_history'].append({'role':'user', 'content': user_input})
    # Mostrar mensaje del usuario
    with st.chat_message('user'):
        st.text(user_input)
    
    CONFIG = {
        "configurable": {
            "thread_id": st.session_state["thread_id"]
        }
    }

    # Ejecutar chatbot y mostrar respuesta en streaming
    with st.chat_message('assistant'):
        ai_message = st.write_stream(
            # return only the content of AI message chatbot
            message_chunk.content 
            # stram messages from the langGraph chatbot
            for message_chunk, metadata in chatbot.stream(
                {'messages':[HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode='messages'
            )
            # display only AI messages
            if isinstance(message_chunk, AIMessage)
        )
    
    # Guardar respuesta del assistant
    st.session_state['message_history'].append({
        'role':'assistant',
        'content': ai_message
    })
