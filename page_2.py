import streamlit as st
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

api_key = "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"
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
