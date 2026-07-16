# PDF AI Assistant
This is a small RAG-based assistant system. You upload a PDF and ask questions concerning the content. An LLM gives precise responses that are purely based on the context of the uploaded document.

You can access the deployed tool under: http://51.21.194.93:8501

## System Architecture
```mermaid
%%{init: {'theme': 'default', 'themeVariables': { 'background': '#ffffff'}}}%%
flowchart TD
    User(("User\n(Browser)"))
    
    subgraph AWS ["AWS EC2 Instance (Linux)"]
        direction TB
        
        subgraph Docker ["Docker Compose Network"]
            direction LR
            FE["Frontend\n(Streamlit)"]
            BE["Backend API\n(FastAPI)"]
            DB[("Vector Database\n(ChromaDB)")]
            HF["Embedding Model\n(HuggingFace)"]
        end
    end

    GroqCloud(("Groq Cloud API\n(Llama 3 LLM)"))

    %% Connections and Data Flow
    User -- "1. Upload PDF & Ask Question\n(Port 8501)" --> FE
    
    FE -- "2. HTTP POST Request\n(incl. Session ID)" --> BE
    
    BE -- "3. Vectorize Text" --> HF
    HF -. "4. Return Embeddings" .-> BE
    
    BE -- "5. Store & Similarity Search" --> DB
    DB -. "6. Return Context Chunks" .-> BE
    
    BE -- "7. Send Prompt + Context" --> GroqCloud
    GroqCloud -. "8. Stream LLM Response" .-> BE
    
    BE -. "9. Return JSON Response" .-> FE
    FE -. "10. Display Answer" .-> User

    %% Styling
    style AWS fill:#fef3c7,stroke:#d97706,stroke-width:2px,color:#000
    style Docker fill:#e0f2fe,stroke:#0284c7,stroke-width:2px,color:#000
    style FE fill:#ffffff,stroke:#ef4444,stroke-width:2px,color:#000
    style BE fill:#ffffff,stroke:#10b981,stroke-width:2px,color:#000
    style DB fill:#ffffff,stroke:#8b5cf6,stroke-width:2px,color:#000
    style HF fill:#ffffff,stroke:#f59e0b,stroke-width:2px,color:#000
    style User fill:#dcfce7,stroke:#16a34a,stroke-width:2px,color:#000
    style GroqCloud fill:#fae8ff,stroke:#c026d3,stroke-width:2px,color:#000
```

## Tech Stack
Frontend:
  - Streamlit (UI)
  - Requests (API communication)

Backend:
  - FastAPI (RESTful API)
  - LangChain (orchestration)
  - ChromaDB (Vector database)
  - Groq API (LLM: llama-3.3-70b-versatile)
  - HuggingFace (Embeddings: all-MiniLM-L6-v2)

Infrastructure:
  - Docker
  - I used AWS EC2 for deployment

