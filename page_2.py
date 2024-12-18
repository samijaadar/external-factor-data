import streamlit as st
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

from main import api_key

part1 = "sk-proj-DsYD4SszhsAoHln6ah9xiWafRC7DoiYDjb9HbGOcnO4xv8OWrttqIWy"
part2 = "_VMOguzMT6N_JEH3sqLT3BlbkFJOUoEXEZvK_dqSAnzmlfxOvN53niOFEP1C"
part3 = "o2tt2GI1ZcBJvkis2Hq-LnGtyG7UHpNw8i0Bqk5cA"
api_key = part1 + part2 + part3

llm = OpenAI(openai_api_key=api_key)

template = """
You are an expert assistant. Based on the context below, answer the user's question as accurately as possible.

Context: {context}
Question: {question}

Answer:"""

prompt = PromptTemplate(
    input_variables=["context", "question"],
    template=template
)

qa_chain = LLMChain(llm=llm, prompt=prompt)

st.title("LangChain Q&A App")
st.write("Provide context and a question below to get an AI-powered answer.")

context = st.text_input("Context", placeholder="Enter the background information here...")
question = st.text_area("Question", placeholder="Enter your question here...")

if st.button("Get Answer"):
    if context and question:
        answer = qa_chain.run({"context": context, "question": question})
        st.write("### Answer")
        st.write(answer)
    else:
        st.write("Please provide both context and a question.")
