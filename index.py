import streamlit as st

pg = st.navigation([
        st.Page("main.py", title="External Factor Data"),
        st.Page("page_2.py", title="LangChain"),
        st.Page("page_3.py", title="Supplier Data"),
    ])
pg.run()
