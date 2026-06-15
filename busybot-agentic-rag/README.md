# BUSYBOT — Agentic RAG Chatbot

An agentic RAG (Retrieval-Augmented Generation) chatbot built with **LangGraph**, **LangChain**, and **Groq (Llama 3.3 70B)**.

BUSYBOT routes incoming user queries to one of four specialized nodes, generates an answer, and self-verifies the answer's coverage before responding.

## Architecture

```
                ┌─────────┐
                │ decide  │  (router)
                └────┬────┘
       ┌─────┬───────┼───────┬─────┐
       ▼     ▼       ▼       ▼     
    tool  retrieve  chat   email
       │     │               │
       └──┬──┘               │
          ▼                  │
       generate               │
          │                  │
          └────────┬──────────┘
                    ▼
              check_answer
              /          \
            end        reroute (back to decide)
```

- **decide**: routes the question to `tool`, `retrieve`, `chat`, or `email` using the LLM
- **tool**: extracts an account number and calls a local bank account API
- **retrieve**: performs similarity search over BUSY software documentation (FAISS)
- **generate**: combines retrieved context / tool output and asks the LLM for an answer
- **chat**: handles greetings and small talk
- **email**: sends the generated report/answer to a provided email address
- **check_answer**: verifies the answer covers all parts of the question; reroutes (up to 2 retries) if something is missing

## Setup

1. Clone the repository
   ```bash
   git clone https://github.com/<your-username>/busybot-agentic-rag.git
   cd busybot-agentic-rag
   ```

2. Create a virtual environment and install dependencies
   ```bash
   python -m venv venv
   source venv/bin/activate   # on Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Configure environment variables
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` and fill in:
   - `GROQ_API_KEY` — get one from [console.groq.com](https://console.groq.com)
   - `GMAIL_ADDRESS` — your Gmail address (for the email feature)
   - `GMAIL_APP_PASSWORD` — a Gmail App Password ([generate here](https://myaccount.google.com/apppasswords))

4. Start the mock account API (in a separate terminal)
   ```bash
   python account_api.py
   ```

5. Run BUSYBOT
   ```bash
   python main.py
   ```

## Example Queries

- `What is the balance of account 12345?`
- `Show account 67890`
- `How to generate invoice in BUSY?`
- `How to file GST return in BUSY?`
- `Send my account details to someone@example.com`
- `hello` / `thank you`

## Tech Stack

- [LangGraph](https://github.com/langchain-ai/langgraph) — agent workflow orchestration
- [LangChain](https://github.com/langchain-ai/langchain) — RAG components
- [Groq](https://groq.com/) — Llama 3.3 70B inference
- [FAISS](https://github.com/facebookresearch/faiss) — vector similarity search
- [HuggingFace Embeddings](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) — `all-MiniLM-L6-v2`
- [FastAPI](https://fastapi.tiangolo.com/) — mock account API

## Notes

- Replace `data/new_busy_data.csv` with your own BUSY knowledge base data.
- Replace the sample accounts in `account_api.py` with a real database/API in production.
- The answer-verification loop in `check_answer` is capped at 2 retries to avoid infinite loops.
