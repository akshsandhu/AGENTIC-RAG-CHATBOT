import warnings
warnings.filterwarnings("ignore")

from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_core.documents import Document

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq

import pandas as pd
import os
import requests
import re


load_dotenv()

# GROQ_API_KEY is now loaded from .env via load_dotenv() above.
# Make sure your .env file contains: GROQ_API_KEY=your_key_here


# API TOOL FUNCTION


def acc_details(acc_no):

    url = "http://127.0.0.1:8002/account"

    payload = {
        "acc_no": acc_no
    }

    print(f"\n[API CALL] URL: {url}")
    print(f"[API CALL] PAYLOAD: {payload}")

    try:

        response = requests.post(
            url,
            json=payload,
            timeout=5
        )

        return response.json()

    except requests.exceptions.ConnectionError:

        return {
            "error": "API server not running"
        }

    except Exception as e:

        return {
            "error": str(e)
        }

#  To extract ACCOUNT NUMBER

def extract_account_number(question):

    match = re.search(r"\b\d{5}\b", question)

    if match:
        return match.group()

    return None


#  TO extract EMAIL ADDRESS

def extract_email(text):

    pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"

    match = re.search(pattern, text)

    if match:
        return match.group()

    return None



embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)



llm = ChatGroq(
    model_name="llama-3.3-70b-versatile",
    temperature=0.3
)


df = pd.read_csv(
    "data/new_busy_data.csv",
    encoding="utf-8"
)


documents = []

for idx, row in df.iterrows():

    content = " | ".join(
        [f"{col}: {row[col]}" for col in df.columns]
    )

    documents.append(
        Document(
            page_content=content,
            metadata={
                "source_file": "new_busy_data.csv",
                "row": idx + 1
            }
        )
    )

print("DOCUMENTS CREATED SUCCESSFULLY")


vectorstore = FAISS.from_documents(
    documents,
    embeddings
)

print("FAISS VECTOR DATABASE CREATED")


retriever = vectorstore.as_retriever(
    search_kwargs={"k": 3}
)


# =========================================
# ROUTER NODE
# =========================================

def decide_route(state):

    question = state.get("question", "")

    if state.get("verification") == "no":
        question = state.get("missing_part", question)
    else:
        question = state.get("question", "")

    state["current_question"] = question

    print(f"\n[ROUTER] QUESTION: {question}")

    router_prompt = f"""
You are an intelligent routing agent.

Your job is to decide where the question should go.

Possible routes:

1. tool
Step1: Identify if the question is related to bank account information or balance inquiries.
- Questions about bank accounts
- Balance checking
- Customer account details
- Money in account

Step2: If the question has specified an account number, route to tool
Step3: If the question does not have an account number but is related to accounts or balance, ask user to provide account number for further assistance.

2. retrieve
- Questions related to BUSY software

3. chat
- ONLY simple greetings
- ONLY small talk
- Examples:
  hi
  hello
  hey
  good morning
  good evening
  how are you
  thank you
  bye

- Do NOT select chat for:
  general knowledge questions,
  explanations,
  cities,
  technology,
  history,
  or informational queries.
# - Greetings
# - Casual conversation
# - General chatting


4.  email
- Send email
- Mail someone
- Email report
- Send balance to email
- Send account details to email


If the question asked by user is outside these three specified categories, display "OUT OF REACH QUESTION".

Return ONLY one word:
tool
retrieve
chat
email

Question:
{question}
"""

    response = llm.invoke(router_prompt)

    decision = response.content.strip().lower()

    print(f"[ROUTER DECISION]: {decision}")

    state["route"] = decision

    return state


def retrieve_documents(state):

    # question = state.get("question", "")
    question = state.get("current_question", "")

    print(f"\n[RETRIEVER] QUESTION: {question}")

    retrieved_docs = retriever.invoke(question)

    state["documents"] = retrieved_docs

    return state


# =========================================
# TOOL NODE
# =========================================

def tool_node(state):

    # question = state.get("question", "")

    question = state.get("current_question", "")

    print(f"\n[TOOL NODE] QUESTION: {question}")

    acc_no = extract_account_number(question)

    print(f"[TOOL NODE] ACCOUNT NUMBER: {acc_no}")


    if not acc_no:

        state["tool_result"] = {
            "error": "No account number found"
        }

        return state


    result = acc_details(acc_no)

    print(f"[TOOL NODE] API RESULT: {result}")

    if "error" in result:

        state["tool_result"] = result

        return state


    state["tool_result"] = result


    balance = None

    if "balance" in question.lower():

        balance = result.get("balance")

    if balance is not None:

        state["answer"] = (
            f"Account balance is ₹{balance}."
        )

    else:

        state["answer"] = (
            "Unable to fetch account balance."
        )

    return state


# =========================================
# GENERATE ANSWER
# =========================================

def generate_answer(state):

    if state.get("answer"):

        return state

    # question = state.get("question", "")

    question = state.get("current_question", "")

    docs = state.get("documents", [])

    tool_result = state.get("tool_result", {})

    context_parts = []


    if docs:

        retrieval_context = "\n\n".join(
            [doc.page_content for doc in docs]
        )

        context_parts.append(
            f"Retrieved Knowledge:\n{retrieval_context}"
        )


    if tool_result:

        if "error" in tool_result:

            context_parts.append(
                f"Tool Error:\n{tool_result['error']}"
            )

        else:

            formatted_tool_output = f"""
Account Holder: {tool_result.get('name')}

Account Balance: ₹{tool_result.get('balance')}
"""

            context_parts.append(
                f"Bank API Result:\n{formatted_tool_output}"
            )


    context = "\n\n".join(context_parts)

    if not context:

        state["answer"] = "Information not available."

        return state


    prompt = f"""
You are an intelligent Agentic RAG assistant.

Use ONLY the provided context.

Context:
{context}

Question:
{question}

Answer:
"""


    try:

        response = llm.invoke(prompt)

        new_answer = response.content
        if state.get("previous_answer"):

            state["answer"] = (
        state["previous_answer"]
        + "\n\n"
        + new_answer
    )
        else:
            state["answer"] = new_answer


        state["sources"] = [
            doc.page_content
            for doc in docs
        ]

    except Exception as e:

        state["answer"] = (
            f"LLM Error: {str(e)}"
        )

    return state


# =========================================
# ROUTE QUESTION
# =========================================

def route_question(state):

    route = state.get("route", "chat")

    print(f"\n[FINAL ROUTE]: {route}")

    if route == "tool":
        return "tool"

    elif route == "retrieve":
        return "retrieve"
    elif route == "email":
        return "email"

    return "chat"




# ========================================
#  CHAT NODE
# ========================================

def chat_node(state):

    # question = state.get("question", "")

    question = state.get("current_question", "")

    prompt = f"""
You are a friendly AI assistant.

Answer naturally.

Question:
{question}
"""

    response = llm.invoke(prompt)

    state["answer"] = response.content

    return state



# ========================================
# LLM ANSWER GENERATION NODE
# ========================================

def verify_route(state):

    verification = state.get("verification", "yes")

    retry_count = state.get("retry_count", 0)

    if verification == "yes":
        return "end"

    if retry_count >= 2:
        return "end"

    return "reroute"


def check_answer(state):

    question = state.get("question", "")

    answer = state.get("answer", "")

    sources = state.get("sources", [])

    context = "\n".join(sources)


    prompt = f"""You are an Answer Coverage Verification Agent.

Your task is to verify whether the generated answer fully and correctly addresses the user's question(s).

Before giving the final result, provide your analysis in this format:

Inputs:
Question:
{question}

Answer:
{answer}


Verification Rules:

1. Identify all distinct questions, requests, or sub-questions present in the user's question.

   * A user message may contain multiple questions.
   * Treat each question, requirement, or requested item as a separate point that must be answered.

2. Compare the answer against every identified question .

3. Return ONLY:
   yes
   if ALL of the following are true:

   * Every question/sub-question is answered.
   * No major information is missing.
   * No unsupported or hallucinated information is present.

4. If ANY of the following occur, return a corrected answer instead of "yes":

   * One or more questions/sub-questions were not answered.
   * The answer is incomplete.
   * The answer contains incorrect information.
   * The answer contains unsupported or hallucinated claims.
   * The answer only partially addresses a multi-part question.

5. When generating a corrected answer:

   * Answer ALL identified questions.
   * Keep the response concise but complete.
   * Do not explain what was wrong with the original answer.
   * Do not include verification notes, reasoning, or analysis.

Output Rules:

* Return ONLY "yes" if the answer fully covers every question.
* If something is missing:
return ONLY

MISSING:
<unanswered part>

* Do not include any additional text, labels, or explanations.
"""

    response = llm.invoke(prompt)
    result = response.content.strip()
    print(f"ANSWER VERIFICATION RESULT")

    # print(f"[CHECK RESULT]: {result}")



    if result.lower() == "yes":

         state["verification"] = "yes"
         state["missing_part"] = ""

         return state

    state["previous_answer"] = state.get("answer", "")

    state["retry_count"] = state.get("retry_count", 0) + 1

    state["verification"] = "no"

    if "MISSING:" in result:

        state["missing_part"] = (
        result.split("MISSING:")[-1]
        .strip()
    )

    return state



# ====================================
# MAIL NODE
# ====================================


from gmail_tool import send_email


def email_node(state):

    question = state.get("question", "")

    email = extract_email(question)

    print("\n EMAIL NODE EXECUTED")

    if not email:

        state["answer"] = (
            "Please provide a valid email address."
        )

        return state

    subject = "BUSYBOT Report"

    message = """
Hello,

This email was sent from BUSYBOT Agentic RAG.

Regards,
Aksh Chaudhary
"""

    try:

        send_email(
            email,
            subject,
            message
        )

        new_answer = f"Email successfully sent to {email}"


        if state.get("previous_answer"):
         state["answer"] = (
        state["previous_answer"]
        + "\n\n"
        + new_answer
    )
        else:
            state["answer"] = new_answer

    except Exception as e:

        state["answer"] = str(e)

    return state



workflow = StateGraph(dict)

workflow.add_node(
    "decide",
    decide_route
)

workflow.add_node(
    "retrieve",
    retrieve_documents
)

workflow.add_node(
    "tool",
    tool_node
)

workflow.add_node(
    "generate",
    generate_answer
)

workflow.add_node(
    "chat",
    chat_node
)

workflow.add_node(
    "email",
    email_node
)

workflow.add_node(
    "check_answer",
    check_answer
)


workflow.set_entry_point("decide")

workflow.add_conditional_edges(
    "decide",
    route_question,
    {
    "tool": "tool",
    "retrieve": "retrieve",
    "chat": "chat",
    "email": "email"
}
)

workflow.add_edge(
    "retrieve",
    "generate"
)

workflow.add_edge(
    "tool",
    "generate"
)

workflow.add_edge(
    "chat",
    "check_answer"
)

workflow.add_edge(
    "generate",
    "check_answer"
)

workflow.add_edge(
    "email",
    "check_answer"
)

workflow.add_conditional_edges(
    "check_answer",
    verify_route,
    {
        "end": END,
        "reroute": "decide"
    }
)


app = workflow.compile()




def ask_question(question):

    initial_state = {
    "question": question,
    "documents": [],
    "tool_result": {},
    "answer": "",
    "sources": [],
    "route": "",
    "retry_count": 0
}

    result = app.invoke(initial_state)

    return result




if __name__ == "__main__":

    print("\n===================================")
    print("BUSYBOT is ready to HELP YOU!")
    print("===================================")

    print("\nExamples:")
    print("- What is the balance of account 12345?")
    print("- Show account 12345")
    print("- How to generate invoice in BUSY?")
    print("\nType 'exit' to quit.\n")

    while True:

        user_query = input("\nAsk your question: ")

        if user_query.lower() == "exit":

            print("\nThank you for using BUSYBOT!")
            break

        result = ask_question(user_query)

        print("\n===================================")
        print("ANSWER")
        print("===================================\n")

        print(
            result.get(
                "answer",
                "No answer found"
            )
        )

        print("\n===================================")
        print("SOURCES")
        print("===================================\n")

        sources = result.get("sources", [])

        if sources:

            for i, source in enumerate(
                sources,
                start=1
            ):

                print(f"{i}. {source}\n")

        else:

            print("No sources found.")
