import gradio as gr

from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatOllama

from modules.host import HOST_URL
from modules.autosurfer.surf_web import gen_queries, search, make_vectorstore_retriever
from modules.moderate import moderate, check_moderation

def gen_response(api_key: str, search_engine_id: str, moderator_on: bool, prompt: str, chat_history: list[list[str | None | tuple]]) -> tuple[str, list[list[str | None | tuple]]]:
    if not api_key:
        raise gr.Error('No API key provided!')
    if not search_engine_id:
        raise gr.Error('No search engine ID provided!')

    if moderator_on:
        gr.Info('Checking prompt for moderation issues...')
        check_moderation(moderate(prompt))
    else:
        gr.Warning('Moderation is disabled. Use at your own risk!')
    
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

    answer = after_rag_chain.invoke(question)

    if moderator_on:
        gr.Info('Checking answer for moderation issues...')
        check_moderation(moderate(answer), raise_error_if_moderated=False)
    
    chat_history.append((prompt, answer))

    return '', chat_history
