# 🤖 BUSYBOT - Agentic RAG Chatbot

An intelligent **Agentic Retrieval-Augmented Generation (RAG) Chatbot** built using **LangGraph, LangChain, Groq LLM, FAISS Vector Database, FastAPI, and Gmail Integration**.

The chatbot automatically routes user queries to the most appropriate agent, retrieves relevant knowledge, invokes external tools, sends emails, and performs answer verification before responding.


## 🚀 Features

### ✅ Intelligent Query Routing

Uses an LLM-powered router to classify incoming queries into:

* Retrieval Agent
* Tool Agent
* Email Agent
* Chat Agent

### ✅ Retrieval-Augmented Generation (RAG)

* Loads BUSY software knowledge base from CSV
* Creates vector embeddings using HuggingFace
* Stores embeddings in FAISS
* Retrieves the most relevant documents
* Generates contextual answers using Llama 3.3 70B

### ✅ Tool Calling

Supports external API integration.

Example:

* Check account balance
* Fetch customer account details
* Retrieve banking information

### ✅ Email Automation

Users can request reports or information to be sent directly through email.

Example:

> Send account details to [abc@gmail.com](mailto:abc@gmail.com)

### ✅ Self-Verification Loop

Before returning a response, the chatbot verifies whether:

* All user questions are answered
* No information is missing
* The response is complete

If information is missing, the workflow automatically retries and improves the answer.

---

# 🏗️ System Architecture

```text
                    ┌─────────────┐
                    │   Router    │
                    └──────┬──────┘
                           │
      ┌──────────┬─────────┼─────────┬──────────┐
      ▼          ▼         ▼         ▼
   Tool      Retrieve     Chat     Email
      │          │                   │
      └──────┬───┘                   │
             ▼                       │
        Answer Generator             │
                │                    │
                └──────────┬─────────┘
                           ▼
                 Answer Verification
                           │
                ┌──────────┴──────────┐
                ▼                     ▼
              END                 Re-route
```

---

# 🛠️ Tech Stack

### AI & Agent Framework

* LangGraph
* LangChain
* Groq API
* Llama 3.3 70B

### Vector Database

* FAISS

### Embeddings

* sentence-transformers/all-MiniLM-L6-v2

### Backend

* Python
* FastAPI

### Email Service

* Gmail SMTP

### Data Processing

* Pandas

---

# 📂 Project Structure

```bash
busybot-agentic-rag/
│
├── main.py
├── account_api.py
├── gmail_tool.py
├── requirements.txt
├── .env.example
├── README.md
│
├── data/
     └── new_busy_data.csv
```

---

# ⚙️ Installation

### 1. Clone Repository

```bash
git clone https://github.com/akshsandhu/busybot-agentic-rag.git

cd busybot-agentic-rag
```

### 2. Create Virtual Environment

```bash
python -m venv venv

venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key

EMAIL_ADDRESS=your_email@gmail.com

EMAIL_PASSWORD=your_gmail_app_password
```

### 5. Start Account API

```bash
python account_api.py
```

### 6. Run Chatbot

```bash
python main.py
```

---

# 💬 Sample Queries

### Retrieval Questions

```text
How do I generate an invoice in BUSY?
```

```text
How can I file GST returns in BUSY?
```

### Tool Questions

```text
What is the balance of account 12345?
```

```text
Show details of account 67890
```

### Email Questions

```text
Send account details to abc@gmail.com
```

### Chat Questions

```text
Hello
```

```text
Thank you
```

---

# 🔍 Workflow

1. User asks a question.
2. Router identifies the correct agent.
3. Agent performs retrieval/tool/email/chat operation.
4. LLM generates answer.
5. Verification agent checks answer completeness.
6. If incomplete, chatbot retries automatically.
7. Final verified answer is returned.

---

# 🎯 Key Learnings

* Agentic AI Workflows
* Retrieval-Augmented Generation (RAG)
* LangGraph State Management
* LLM Routing Strategies
* Tool Calling
* FastAPI Integration
* Email Automation
* Vector Search using FAISS
* Answer Verification Loops

---

# 📈 Future Improvements

* Multi-tool agent support
* Conversation memory
* Authentication layer
* Web dashboard
* Database integration
* Real-time streaming responses
* Deployment on AWS/GCP

---

# 👨‍💻 Author

Aksh Sandhu

LinkedIn: www.linkedin.com/in/aksh-sandhu-8282a63b7

GitHub: https://github.com/akshsandhu
