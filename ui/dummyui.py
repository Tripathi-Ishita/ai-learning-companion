import streamlit as st
print("Script ran because i am cool hehehe")
st.title("Hello, Streamlit!")
if "count" not in st.session_state:
    st.session_state.count = 0
plain_counter=0
if st.button("Click me"):
    st.session_state.count += 1
    plain_counter+=1

st.write("session state count:", st.session_state.count)
st.write("plain counter:", plain_counter)
