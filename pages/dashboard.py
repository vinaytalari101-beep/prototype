
import streamlit as st, pandas as pd, sqlite3
st.title('Dashboard')
conn=sqlite3.connect('inventory.db')
try:
    df=pd.read_sql_query('select * from products',conn)
    st.metric('Products',len(df))
    st.metric('Stock', int(df.stock.sum()) if len(df) else 0)
except: st.info('No data yet')
