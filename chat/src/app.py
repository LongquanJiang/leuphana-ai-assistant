import logging
import os
import json

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = ""
os.environ["OPENAI_API_KEY"] = "sk-"

from langchain import hub
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import JSONLoader
from langchain_openai import ChatOpenAI

from flask import Flask, jsonify, request, stream_with_context

app = Flask(__name__)

llm = ChatOpenAI(model="gpt-4o-mini")

loader = JSONLoader(
    file_path='/data/news.jsonl',
    jq_schema='.content',
    text_content=False,
    json_lines=True)

docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents(docs)
vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings())

# Retrieve and generate using the relevant snippets of the blog.
retriever = vectorstore.as_retriever()
prompt = hub.pull("rlm/rag-prompt")

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

@app.route("/ping")
def ping():
    return "This is Chatbot"

@app.route("/chat", methods=["POST", "GET"])
def chat():
    try:
        data = request.get_json(force=True)
        messages = data.get("messages")
        response = rag_chain.invoke(messages[len(messages)-1]["content"])

        rtn = {"choices":[
            {
                "index": 0,
                "delta": {
                    "content": response
                },
                "finish_reason": "stop"
            }
        ]}

        def generate():
            ss = "data: "+json.dumps(rtn) + "\n\n"
            yield ss.encode('utf-8')
            yield "data: [DONE]".encode('utf-8')

        return stream_with_context(generate())



    except Exception as ex:
        data = {}
        data["exception"] = str(ex)
        return jsonify(data)




if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port="30003")