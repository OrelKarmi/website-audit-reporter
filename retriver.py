
from crawler import fetch_urls
from langchain_openai import OpenAIEmbeddings
from crawler import fetch_urls
from langchain_core.vectorstores import InMemoryVectorStore
from helper import load_urls

class Retriver:
    def __init__(self, url):
        self.urls = fetch_urls(url)
        self.docs = load_urls(self.urls)
        self.vectorstore = InMemoryVectorStore.from_documents(
            documents=self.docs, embedding=OpenAIEmbeddings()
        )
        self.retriver = self.vectorstore.as_retriever()

    def get_relevant_documents(self, question):
        docs = self.retriver.invoke(question)
        return self.format_docs(docs)

    def format_docs(self, docs):
        return "\n\n".join(doc.page_content for doc in docs)


    

