from typing import Optional, Dict, Any, List
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.messages import HumanMessage, AIMessage


class ConversationalRAGChain:
    """
    RAG chain with conversational memory for multi-turn interactions.

    Implements:
    - Retrieval-Augmented Generation (RAG)
    - Conversational memory using LangChain message history
    - Multi-turn question answering
    """

    def __init__(
        self,
        vectorstore: Chroma,
        model_name: str = "gpt-5-mini",
        temperature: float = 0,
        k: int = 4,
        api_key: Optional[str] = None
    ):
        self.vectorstore = vectorstore
        self.k = k
        self.chat_history: List = []  # LangChain message history

        self.retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k}
        )

        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=api_key
        )

        # Prompt with conversational memory support
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful assistant. Use the following context to answer the user's question.
If you cannot find the answer in the context, say so clearly.
You can reference previous conversation when relevant.

Context:
{context}"""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{question}")
        ])

        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        self.chain = (
            {
                "context": self.retriever | format_docs,
                "question": RunnablePassthrough(),
                "chat_history": lambda _: self.chat_history
            }
            | self.prompt
            | self.llm
            | StrOutputParser()
        )

    def query(self, question: str) -> str:
        """
        Query with conversational memory.
        Automatically stores question and answer in history.
        """
        answer = self.chain.invoke(question)

        # Store in conversational memory
        self.chat_history.append(HumanMessage(content=question))
        self.chat_history.append(AIMessage(content=answer))

        return answer

    def query_with_sources(self, question: str) -> Dict[str, Any]:
        """Query and return answer with source documents"""
        retrieved_docs = self.retriever.invoke(question)
        answer = self.query(question)  # Uses conversational memory

        sources = [
            {
                "content": doc.page_content,
                "metadata": doc.metadata
            }
            for doc in retrieved_docs
        ]

        return {
            "answer": answer,
            "sources": sources
        }

    def stream_query(self, question: str):
        """Stream the response with conversational memory"""
        chunks = []
        for chunk in self.chain.stream(question):
            chunks.append(chunk)
            yield chunk

        # Store in memory after streaming completes
        full_answer = "".join(chunks)
        self.chat_history.append(HumanMessage(content=question))
        self.chat_history.append(AIMessage(content=full_answer))

    def clear_history(self):
        """Clear conversation history"""
        self.chat_history = []

    def get_history(self) -> List[Dict[str, str]]:
        """Get conversation history in readable format"""
        history = []
        for msg in self.chat_history:
            if isinstance(msg, HumanMessage):
                history.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                history.append({"role": "assistant", "content": msg.content})
        return history
