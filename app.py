# app.py

import streamlit as st
from data_processing import data_processing_page
from data_processing2 import data_processing_page2


def main():
    st.sidebar.title('腾讯问卷数据转化')
    page = st.sidebar.radio(
        "选择功能页面",
        ["矩阵填空数据处理","自增表格数据处理"]
    )
    
    if page == "矩阵填空数据处理":
        data_processing_page()
    elif page == "自增表格数据处理":
        data_processing_page2()
    else:
        st.error("未知页面")

if __name__ == '__main__':
    main()
