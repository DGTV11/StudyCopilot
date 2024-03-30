import gradio as gr

from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatOllama

from modules.host import HOST_URL
from modules.autosurfer.surf_web import gen_queries, search, make_vectorstore_retriever
from modules.moderate import moderate, check_moderation

def gen_response(api_key: str, search_engine_id: str, prompt: str, chat_history: list[list[str | None | tuple]]) -> tuple[str, list[list[str | None | tuple]]]:
    check_moderation(moderate(prompt))
    
    queries = gen_queries(prompt)
    search_docs = search(api_key, search_engine_id, queries)
    retriever = make_vectorstore_retriever(search_docs)
    
    model_local = ChatOllama(model="guardrailed_mistral", base_url=HOST_URL)
    question = prompt
    after_rag_template = """Answer the question based only on the following context:
    {context}
    Question: {question}
    """
    after_rag_prompt = ChatPromptTemplate.from_template(after_rag_template)
    after_rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | after_rag_prompt
        | model_local
        | StrOutputParser()
    )
    
    chat_history.append((prompt, after_rag_chain.invoke(question)))

    return '', chat_history
