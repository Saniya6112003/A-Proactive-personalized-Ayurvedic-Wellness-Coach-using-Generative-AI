import json
import streamlit as st
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
# --- FIX 1: Using ChatOllama is the modern standard for chat models ---
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# Highly likely scenario for v1.0 simplification:
from langchain import create_history_aware_retriever, create_stuff_documents_chain
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory

@st.cache_resource
def load_and_process_kb():
    """Loads the Ayurvedic knowledge base, processes it into documents, and creates a retriever."""
    with open('ayurvedic_kb.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    documents = []

    # Flatten all data into searchable documents
    for dosha in data['doshas']:
        content = f"Dosha Information for {dosha['name']}: Elements are {', '.join(dosha['elements'])}. Qualities are {', '.join(dosha['qualities'])}. It governs {dosha['governing_principle']}. Balanced traits include {', '.join(dosha['balanced_traits'])}. Physical imbalance symptoms are {', '.join(dosha['imbalance_symptoms']['physical'])}. Mental/emotional imbalance symptoms include {', '.join(dosha['imbalance_symptoms']['mental_emotional'])}."
        documents.append(Document(page_content=content, metadata={"source": "doshas", "topic": dosha['name']}))
    for category, items in data['foods'].items():
        for item in items:
            effects = ', '.join([f"{d} is {e}" for d, e in item['effects_on_doshas'].items()])
            content = f"Food Item: {item['name']} (Category: {category}). Qualities: {', '.join(item['gunas'])}. Tastes: {', '.join(item['rasas'])}. Effects on Doshas: {effects}."
            documents.append(Document(page_content=content, metadata={"source": "foods", "topic": item['name']}))
    for herb in data['herbs']:
        effects = ', '.join([f"{d} is {e}" for d, e in herb['effects_on_doshas'].items()])
        content = f"Herb: {herb['name']}. Description: {herb['description']}. Qualities: {', '.join(herb['gunas'])}. Tastes: {', '.join(herb['rasas'])}. Effects on Doshas: {effects}."
        documents.append(Document(page_content=content, metadata={"source": "herbs", "topic": herb['name']}))
    for asana in data['yoga_asanas']:
        content = f"Yoga Asana: {asana['name']} ({asana['sanskrit_name']}). Description: {asana['description']}. It is balancing for the following doshas: {', '.join(asana['balancing_for_doshas'])}."
        documents.append(Document(page_content=content, metadata={"source": "yoga_asanas", "topic": asana['name']}))
    for practice in data['pranayama']:
        content = f"Pranayama (Breathing Exercise): {practice['name']} ({practice['sanskrit_name']}). Description: {practice['description']}. It is balancing for: {', '.join(practice['balancing_for_doshas'])}."
        documents.append(Document(page_content=content, metadata={"source": "pranayama", "topic": practice['name']}))

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma.from_documents(documents=documents, embedding=embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    return retriever

# In-memory store for session histories
store = {}
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

# --- FIX 1: ADD THIS FUNCTION ---
@st.cache_resource
def get_llm():
    """Loads the LLM model once and caches it."""
    # This print statement will only run the first time the app loads
    print("--- LOADING LLM MODEL (this should only run once) ---")
    return ChatOllama(model="llama3")

def create_rag_chain(retriever, user_dosha, holistic_prompt_addition):
    """Creates a history-aware RAG chain."""
    
    # --- FIX 2: CHANGE THIS LINE ---
    # Instead of creating a new model, get the cached one.
    llm = get_llm()

    # This prompt helps the AI reformulate the user's question to be standalone
    contextualize_q_system_prompt = ("Given a chat history and the latest user question which might reference context in the chat history, formulate a standalone question which can be understood without the chat history. Do NOT answer the question, just reformulate it if needed and otherwise return it as is.")
    contextualize_q_prompt = ChatPromptTemplate.from_messages([("system", contextualize_q_system_prompt), MessagesPlaceholder("chat_history"), ("human", "{input}")])
    history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)
    
    # The variables {user_dosha} and {holistic_prompt} will be passed in the final input.
    qa_system_prompt = """You are an expert Ayurvedic wellness assistant. Your tone is professional, knowledgeable, and empathetic. The user you are speaking with has a dominant '{user_dosha}' dosha. Answer the user's question based ONLY on the provided context. Provide actionable and clear advice. Do not make up information. {holistic_prompt}

Context:
{context}"""
    
    qa_prompt = ChatPromptTemplate.from_messages([("system", qa_system_prompt), MessagesPlaceholder("chat_history"), ("human", "{input}")])
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
    
    return rag_chain

# --- Streamlit App UI ---
st.set_page_config(page_title="Chat with Your Coach", page_icon="💬")
st.title("💬 Chat with Your Ayurvedic Coach")

if st.session_state.get('dosha') is None:
    st.warning("Please complete the 'Dosha Analysis' first for a personalized chat experience.")
else:
    user_dosha = st.session_state.dosha
    user_name = st.session_state.user_name
    st.info(f"Welcome, {user_name}! I'm here to help. Your dominant dosha is **{user_dosha}**, so my advice will be tailored for you.")

    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [{"role": "assistant", "content": "Namaste! How can I help you achieve balance today?"}]

    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Load the retriever once
    retriever = load_and_process_kb()

    symptom_keywords = {
        "Vata": ["anxiety", "dry skin", "constipation", "bloating", "insomnia", "restless"],
        "Pitta": ["heartburn", "acidity", "inflammation", "rash", "irritable", "anger"],
        "Kapha": ["lethargy", "sluggish", "congestion", "weight gain", "motivation", "heavy"]
    }

    if prompt := st.chat_input("What would you like to know?"):
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        holistic_prompt_addition = ""
        for dosha_key, keywords in symptom_keywords.items():
            if any(keyword in prompt.lower() for keyword in keywords):
                holistic_prompt_addition = f"After answering the user's primary question, ALSO provide two additional, proactive lifestyle recommendations (like a diet tip or a daily routine adjustment) to help pacify their {dosha_key} dosha, as their question indicates a possible {dosha_key} imbalance."
                break
        
        # --- FIX 3: LOAD THE CHAIN ONCE ---
        # We also cache the RAG chain so it's not rebuilt on every message.
        # We can't cache it at the top because it depends on user_dosha.
        # But we can cache it here *inside* the main app logic.
        @st.cache_resource
        def get_rag_chain(_retriever, _user_dosha, _holistic_prompt):
             print("--- CREATING RAG CHAIN (this should only run once per prompt style) ---")
             return create_rag_chain(_retriever, _user_dosha, _holistic_prompt)

        conversational_rag_chain = get_rag_chain(retriever, user_dosha, holistic_prompt_addition)
        
        chat_history = get_session_history("streamlit_session_chat")
        
        chain_input = {
            "input": prompt,
            "chat_history": chat_history.messages,
            "user_dosha": user_dosha,
            "holistic_prompt": holistic_prompt_addition
        }

        with st.chat_message("assistant"):
            with st.spinner("Your coach is thinking..."):
                response = conversational_rag_chain.invoke(chain_input)
                st.markdown(response["answer"])
                with st.expander("View Sources"):
                    for doc in response["context"]:
                        st.info(f"Source: {doc.metadata.get('source', 'N/A')} - Topic: {doc.metadata.get('topic', 'N/A')}")

        # Add messages to history
        st.session_state.chat_messages.append({"role": "assistant", "content": response["answer"]})
        chat_history.add_user_message(prompt)
        chat_history.add_ai_message(response["answer"])



