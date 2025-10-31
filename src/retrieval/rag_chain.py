from typing import Optional, Dict, Any
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough


class RAGChain:
    """Simple RAG chain for question answering over documents"""

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

        self.retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k}
        )

        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=api_key
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful assistant. Use the following context to answer the user's question.
If you cannot find the answer in the context, say so clearly.

Context:
{context}"""),
            ("user", "{question}")
        ])

        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        self.chain = (
            {
                "context": self.retriever | format_docs,
                "question": RunnablePassthrough()
            }
            | prompt
            | self.llm
            | StrOutputParser()
        )

    def query(self, question: str) -> str:
        """Query the RAG system"""
        return self.chain.invoke(question)

    def query_with_sources(self, question: str) -> Dict[str, Any]:
        """Query and return answer with source documents"""
        retrieved_docs = self.retriever.invoke(question)
        answer = self.chain.invoke(question)

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
        """Stream the response"""
        for chunk in self.chain.stream(question):
            yield chunk
