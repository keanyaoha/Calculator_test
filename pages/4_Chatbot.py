# Import necessary libraries
from llama_index.llms.huggingface import HuggingFaceInferenceAPI
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import StorageContext, load_index_from_storage
from llama_index.core.chat_engine import ContextChatEngine
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.base.llms.types import ChatMessage, MessageRole
import streamlit as st
import os


# --- App Config ---
st.set_page_config(
    page_title="Green Tomorrow",
    page_icon="🌿",
    layout="centered"
)

# --- Force Logo to Appear at Top of Sidebar ---
st.markdown(
    """
    <style>
        [data-testid="stSidebar"]::before {
            content: "";
            display: block;
            background-image: url('https://raw.githubusercontent.com/GhazalMoradi8/Carbon_Footprint_Calculator/main/GreenPrint_logo.png');
            background-size: 90% auto;
            background-repeat: no-repeat;
            background-position: center;
            height: 140px;
            margin: 1.5rem auto -4rem auto;  /* SUPER tight top & bottom spacing */
        }

        section[data-testid="stSidebar"] {
            background-color: #d6f5ec;
        }

        .stApp {
            background-color: white;
        }
    </style>
    """,
    unsafe_allow_html=True
)


# --- Configuration ---

# LLM Configuration (Fixed)
hf_model = "mistralai/Mistral-7B-Instruct-v0.3"
llm = HuggingFaceInferenceAPI(model_name=hf_model)

# Embeddings Configuration
embedding_model = "sentence-transformers/all-MiniLM-l6-v2"
embeddings = HuggingFaceEmbedding(model_name=embedding_model)

# Vector Database Configuration
persist_directory = "vector_index"

if not os.path.exists(persist_directory):
    st.error(f"❌ Error: Vector index directory '{persist_directory}' not found. Make sure it's in your GitHub repository root.")
    st.stop()

try:
    storage_context = StorageContext.from_defaults(persist_dir=persist_directory)
    vector_index = load_index_from_storage(storage_context, embed_model=embeddings)
except Exception as e:
    st.error(f"❌ Error loading vector index from '{persist_directory}': {e}")
    st.stop()

# Retriever Configuration
retriever = vector_index.as_retriever(similarity_top_k=2)

# Prompt Configuration
prompts = [
    ChatMessage(role=MessageRole.SYSTEM, content="You are a nice chatbot having a conversation with a human."),
    ChatMessage(role=MessageRole.SYSTEM, content="Answer the question based only on the following context and previous conversation."),
    ChatMessage(role=MessageRole.SYSTEM, content="Keep your answers short and succinct.")
]

# Memory Configuration
memory = ChatMemoryBuffer.from_defaults()

# --- Bot Initialization ---
@st.cache_resource
def init_bot():
    try:
        engine = ContextChatEngine.from_defaults(
            llm=llm,
            retriever=retriever,
            memory=memory,
            prefix_messages=prompts,
            verbose=True
        )
        return engine
    except Exception as e:
        st.error(f"❌ Failed to initialize chatbot engine: {e}")
        return None

rag_bot = init_bot()

if rag_bot is None:
    st.stop()

# --- Streamlit UI ---
st.title("💬 CarbonFootprint Chatbot")

# Display chat messages from history
if hasattr(rag_bot, 'chat_history') and rag_bot.chat_history:
    for message in rag_bot.chat_history:
        role = getattr(message, 'role', 'unknown')
        content = ""
        if hasattr(message, 'content'):
            content = message.content
        elif hasattr(message, 'blocks') and message.blocks:
            content = getattr(message.blocks[0], 'text', '')

        with st.chat_message(role.name if hasattr(role, 'name') else str(role)):
            st.markdown(content)

# User input and response handling
if prompt := st.chat_input("Curious minds wanted!"):
    st.chat_message("user").markdown(prompt)
    with st.spinner("🔍 Digging for answers..."):
        try:
            answer = rag_bot.chat(prompt)
            response_text = getattr(answer, 'response', '❌ Sorry, I could not process that.')
            with st.chat_message("assistant"):
                st.markdown(response_text)
        except Exception as e:
            st.error(f"Error during chat processing: {e}")
            with st.chat_message("assistant"):
                st.markdown("❌ Sorry, an error occurred while trying to get an answer.")
