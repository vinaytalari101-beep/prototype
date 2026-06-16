
import streamlit as st
from database import init_db
from auth import login
init_db()
st.set_page_config(page_title='Smart Inventory System',layout='wide')
login()
st.title('📦 Smart Inventory System')
st.write('Use the Pages menu on the left.')
