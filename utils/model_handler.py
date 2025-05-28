from langchain_ollama import ChatOllama
import streamlit as st
from langchain_core.runnables import Runnable

class HuggingFaceModel(Runnable):
    def __init__(self, client):
        self.client = client

    def invoke(self, input, config=None):
        return self.client.text_generation(input, temperature=0.7)


@st.cache_resource
def get_ollama_model():
    return ChatOllama(model="llava", temperature=0.7)