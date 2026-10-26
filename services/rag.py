from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from services.session import (
    get_history,
    add_message,
    session_exists
)
from config import settings
from services.chroma import get_retriever
from services.session import get_history, add_message


llm = ChatGroq(
    model="openai/gpt-oss-20b",
    api_key=settings.GROQ_API_KEY
)


prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are a helpful study assistant.

Answer the user's question using only the provided context.

The context contains page numbers. If the user asks where a topic,
concept, or information is located, provide the relevant page number ans always print page increament by 1.

Use the conversation history only to understand the user's current question.
Do not use information from the conversation history as factual document
content unless it is also present in the provided context.

If the answer is not present in the provided context, say:
"I could not find the answer in the uploaded document."

Context:
{context}
"""
    ),

    MessagesPlaceholder(variable_name="history"),

    (
        "human",
        "{question}"
    )
])


rag_chain = prompt | llm | StrOutputParser()


def ask_question(question: str, session_id: str):
    if not session_exists(session_id):
        return None


    retriever = get_retriever(session_id)

    documents = retriever.invoke(question)

    context = "\n\n".join(
        f"Page {document.metadata.get('page', 'unknown')}:\n"
        f"{document.page_content}"
        for document in documents
    )

    history = get_history(session_id)

    response = rag_chain.invoke({
        "context": context,
        "history": history,
        "question": question
    })

    add_message(
        session_id,
        HumanMessage(content=question),
        
    )

    add_message(
        session_id,
        AIMessage(content=response),
       
    )

    return response