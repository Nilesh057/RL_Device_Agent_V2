import streamlit as st
import sys
import os

# Add current directory to path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from feedback import create_streamlit_interface

if __name__ == "__main__":
    create_streamlit_interface()