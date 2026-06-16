
import streamlit as st, sqlite3, pandas as pd
st.title('Inventory')
conn=sqlite3.connect('inventory.db')
with st.form('f'):
    n=st.text_input('Name')
    c=st.text_input('Category')
    p=st.number_input('Price')
    s=st.number_input('Stock',step=1)
    if st.form_submit_button('Add'):
        conn.execute('insert into products(name,category,price,stock) values(?,?,?,?)',(n,c,p,s)); conn.commit()
df=pd.read_sql_query('select * from products',conn)
st.dataframe(df,use_container_width=True)
