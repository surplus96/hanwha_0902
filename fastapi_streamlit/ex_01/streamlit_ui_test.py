import streamlit as st
import pandas as pd
import numpy as np
import random
import time

# Streamed response emulator
def response_generator(prompt):
    if prompt and prompt.text:
        response = "LLM does not cennected yet. Please update your API-KEY settings"

        for word in response.split():
            yield word + " "
            time.sleep(0.05)
    if prompt and prompt["files"]:
        response = "Image input"
    return response

st.title("AI Chatbot Test")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])



# Accept user input
if prompt := st.chat_input(
   "Type your prompt here and/or attach an image",
    accept_file=True,
    file_type=["jpg", "jpeg", "png"],
):
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        if prompt and prompt.text:
            st.markdown(prompt.text)
        if prompt and prompt["files"]:
            st.image(prompt["files"][0])   

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        response = st.write_stream(response_generator(prompt))
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})


