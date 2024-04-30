import gradio as gr

from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatOllama

import modules.logging as log
from modules.host import HOST_URL, HOST
from modules.autosurfer.surf_web import gen_queries, search, make_vectorstore_retriever
from modules.latent_space_activation.technique01_dialog import lsa_query
from modules.moderate import moderate, check_moderation
from modules.config import CONFIG

def gen_response(
    autosurfer_model: str,
    online_mode: bool,
    moderator_on: bool,
    prompt: str,
    chat_history: list[list[str | None | tuple]],
) -> tuple[str, list[list[str | None | tuple]]]:
    if moderator_on:
        log.log_info("Autosurfer", "Checking prompt for moderation issues")
        check_moderation('Autosurfer', moderate(prompt))
    else:
        log.log_warning(
            "Autosurfer", "Moderation is disabled. Use at your own risk!"
        )

    if online_mode:
        log.log_info('Autosurfer', 'Generating search queries')
        queries = gen_queries(prompt)
        len_queries = len(queries)

        for i, query in enumerate(queries, start=1):
            log.log_info('Autosurfer', f'Query {i}/{len_queries}: {query}')
        
        log.log_info('Autosurfer', 'Searching web')
        search_docs = search(CONFIG['google_api_key'], CONFIG['google_search_engine_id'], queries)
        retriever = make_vectorstore_retriever(search_docs)

        model_local = ChatOllama(
            model=f"guardrailed_{autosurfer_model}", base_url=HOST_URL
        )
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

        log.log_info("Answering question")
        answer = after_rag_chain.invoke(question)
    else:
        answer = ""

        for message in enumerate(
            lsa_query(
                prompt, model=f"guardrailed_{autosurfer_model}", chatbot=HOST.chat
            )
        ):
            if message[0] % 2 == 0:
                log.log_info(
                    "Autosurfer", f'INTERROGATOR sent \'{message[1]["content"]}\''
                )
                answer += f'\n\nINTERROGATOR: {message[1]["content"]}'
            else:
                answer += f'\n\nCHATBOT:\n{message[1]["content"]}'

    if moderator_on:
        log.log_info("Autosurfer", "Checking answer for moderation issues")
        check_moderation('Autosurfer', moderate(answer), raise_error_if_moderated=False)

    log.log_info('Autosurfer', 'Finished generating response')
    chat_history.append((prompt, answer))
    return "", chat_history
