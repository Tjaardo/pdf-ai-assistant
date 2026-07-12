import streamlit as st
import requests
import os

#FASTAPI backend url
if os.getenv("DOCKER_ENV") == "true":
    BACKEND_URL = "http://backend:8000"
else:
    BACKEND_URL = "http://localhost:8000"

st.set_page_config(page_title="Consultant AI Assistant", page_icon="🤖")
st.title("Consultant AI Assistant")
st.subheader("Upload pdf and ask questions")

#Document upload
st.header("Upload document")
uploaded_file = st.file_uploader("Choose a pdf", type=["pdf"])

if uploaded_file is not None:
    if st.button("Save document on system"):
        with st.spinner("Analyse pdf..."):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
            response = requests.post(f"{BACKEND_URL}/upload", files=files)
            
            if response.status_code == 200:
                result = response.json()
                st.success(f"Loaded successfully! Cut into {result.get('generated chunks')} chunks.")
            else:
                st.error("Error Uploading the file to the backend.")

st.markdown("---")

#Question asking
st.header("Ask a question about the document")
user_question = st.text_input("Your question")

if st.button("Send Question"):
    if user_question:
        with st.spinner("thinking..."):
            payload = {"question": user_question} 
            response = requests.post(f"{BACKEND_URL}/ask", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                st.write("Response:")
                st.info(result.get("LLM_response"))
                st.caption(f"Used chunks from ducument: {result.get('Used_chunks')}")
            else:
                st.error("Error when trying to communicate with LLM")
    else:
        st.warning("Ask a question first")