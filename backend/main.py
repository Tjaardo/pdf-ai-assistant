import os
import shutil
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate

base_dir = Path(__file__).resolve().parent.parent
env_path = base_dir / ".env"

load_dotenv(dotenv_path=env_path)

app = FastAPI(title="Consultant AI Assistant")

llm = ChatGroq(
    model = "llama-3.3-70b-versatile",
    temperature=0.0
)

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

CHROMA_PATH = base_dir / "chroma_db"

class QueryModel(BaseModel):
    question: str
    session_id: str

class ClearModel(BaseModel):
    session_id: str

#API endpoints
@app.get("/")
async def read_root():
    return {"message": "Welcome!"}

@app.post("/upload")
async def upload_document(file: UploadFile = File(...), session_id: str = Form(...)):
    try:
        #save pdf locally (temporarily)
        temp_file_path = f"temp_{file.filename}"
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        #extract text from pdf
        loader = PyPDFLoader(temp_file_path)
        documents = loader.load()

        #chunking on the extracted text
        text_spitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        chunks = text_spitter.split_documents(documents)

        user_db_path = CHROMA_PATH / session_id

        #create and save embeddings in ChromaDB
        db = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=str(user_db_path)
        )

        os.remove(temp_file_path)

        return {
            "Status": "Saved successfully",
            "Filename": file.filename,
            "generated chunks": len(chunks)
        }


    except Exception as e:
        return {"ERROR!": f"Could not process: {str(e)}"}

@app.post("/ask")
async def ask_question(query: QueryModel):
    try:
        user_db_path = CHROMA_PATH / query.session_id

        if not user_db_path.exists():
            return {"LLM_response": "Please upload a PDF first!"}
        #load chromaDB with same embedding model as before
        db = Chroma(persist_directory=str(user_db_path), embedding_function=embeddings)

        #search db for top 3 similar chunks in pdf
        results = db.similarity_search(query.question, k=3)

        # extract texts from selected chunks and append them
        context_text = "\n\n---\n\n".join([doc.page_content for doc in results])

        #use prompt template 
        prompt_template = ChatPromptTemplate.from_template("""
        You are a highly precise and professional assistant for consultants.
        answer the user question ONLY based on the following context.
        If you can not find an answer from the given context, state clearly and openly that you do not know the answer. Do not hallucinate or make things up!
        
        CONTEXT:
        {context}
                                                
        USER QUESTION
        {question}
        """)

        chain = prompt_template | llm

        response = chain.invoke({
            "context": context_text,
            "question": query.question
        })

        return {
            "User_question": query.question,
            "LLM_response": response.content,
            "Used_chunks": len(results)
        }
    except Exception as e:
        return {"ERROR": f"No connection to Groq: {str(e)}"}
    
@app.post("/clear")
async def clear_session(data: ClearModel):
    #delete db for this specific user
    try:
        user_db_path = CHROMA_PATH / data.session_id
        if user_db_path.exists():
            shutil.rmtree(user_db_path)
            return{"status": "deleted successfully"}
    except Exception as e:
        return{"ERROR": f"could not delete memory: {str(e)}"}