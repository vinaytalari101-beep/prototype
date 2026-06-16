
import streamlit as st, sqlite3, pandas as pd
st.title('POS')
conn=sqlite3.connect('inventory.db')
df=pd.read_sql_query('select * from products',conn)
if len(df):
    p=st.selectbox('Product',df['name'])
    q=st.number_input('Qty',1)
    if st.button('Sell'):
        row=df[df['name']==p].iloc[0]
        if row.stock>=q:
            conn.execute('update products set stock=? where id=?',(int(row.stock-q),int(row.id))); conn.commit()
            st.success('Sold')
