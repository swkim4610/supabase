import streamlit as st 
from supabase import create_client
import pandas as pd
from datetime import datetime
from pytz import timezone

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"] # url을 secret 기능으로 가져옴
    key = st.secrets["SUPABASE_KEY"] # key을 secret 기능으로 가져옴
    return create_client(url, key)

supabase = init_connection()
seoul = timezone('Asia/Seoul')

st.title("마당 서점 관리 시스템")

_tmp = supabase.table("Customer").select("name").execute()
customers = ['고객선택'] + [row['name'] for row in _tmp.data]
_tmp = supabase.table("Book").select("bookid", "bookname").execute()
books = [str(row['bookid']) + "." + row['bookname'] for row in _tmp.data]


tab1, tab2 = st.tabs(["고객조회", "거래 입력"])
result =pd.DataFrame()

name = tab1.selectbox("고객명", customers)

if name != '고객선택':
    _tmp = supabase.rpc('get_transactions_by_name', {'name_param': name}).execute()

    result = pd.DataFrame(_tmp.data, columns=['custid', 'name', 'bookname', 'orderdate', 'saleprice'])
    if len(result) == 0:
        tab1.write("거래 내역이 없습니다.")
    else:
        tab1.write(result)
        custid = result['custid'][0]
        tab2.write("고객번호: " + str(custid))
        tab2.write("고객명: " + name)
        select_book = tab2.selectbox("구매 서적:",books)

        if select_book is not None:
                bookid = select_book.split(".")[0]
                now = datetime.now(seoul)
                dt = now.strftime('%Y-%m-%d')
                _tmp = supabase.table('Orders').select('orderid').order('orderid', desc=True).limit(1).execute()
                orderid = _tmp.data[0]['orderid'] + 1
                price = tab2.text_input("금액")
                if tab2.button('거래 입력'):
                    data = {
                        "orderid": int(orderid),
                        "custid": int(custid),
                        "bookid": int(bookid),
                        "saleprice": int(price),
                        "orderdate": dt
                    }
                    print(data)
                    insert_response = supabase.table("Orders").insert(data).execute()
                    tab2.write('거래가 입력되었습니다.')