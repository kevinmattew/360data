# data_processing.py

import streamlit as st
import pandas as pd
from utils import process_text_count

def data_processing_page():
    st.title('矩阵填空数据处理')
    
    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False

    data_source = st.radio(
        "选择数据来源",
        ["上传原始数据进行清洗", "上传已清洗的数据表"]
    )
    
    if data_source == "上传原始数据进行清洗":
        uploaded_file = st.file_uploader("请上传CSV文件", type=['csv'], key='raw_data')
        if uploaded_file is not None and not st.session_state.data_loaded:
            from data_cleaning import clean_data
            st.session_state.df = clean_data(uploaded_file)
            st.session_state.data_loaded = True
    else:
        uploaded_file = st.file_uploader("请上传已清洗的CSV文件", type=['csv'], key='cleaned_data')
        if uploaded_file is not None and not st.session_state.data_loaded:
            st.session_state.df = pd.read_csv(uploaded_file)
            st.session_state.data_loaded = True
    
    if st.session_state.df is not None:
        st.write("处理后的数据:")
        st.dataframe(st.session_state.df)
        
        with st.expander("添加自定义列"):
            col1, col2, col3 = st.columns(3)
                
            with col1:
                new_column_name = st.text_input("新列名称")
                
            with col2:
                numeric_columns = st.session_state.df.select_dtypes(include=['float64', 'int64']).columns
                selected_columns = st.multiselect("选择要计算的列", numeric_columns)
                
            with col3:
                calc_method = st.selectbox("计算方式", ["求和", "平均值", "最大值", "最小值"])
                
            if st.button("添加新列"):
                if new_column_name and selected_columns:
                    try:
                        if calc_method == "求和":
                            st.session_state.df[new_column_name] = st.session_state.df[selected_columns].sum(axis=1)
                        elif calc_method == "平均值":
                            st.session_state.df[new_column_name] = st.session_state.df[selected_columns].mean(axis=1)
                        elif calc_method == "最大值":
                            st.session_state.df[new_column_name] = st.session_state.df[selected_columns].max(axis=1)
                        elif calc_method == "最小值":
                            st.session_state.df[new_column_name] = st.session_state.df[selected_columns].min(axis=1)
                            
                        st.success(f"已添加新列: {new_column_name}")
                    except Exception as e:
                        st.error(f"计算时发生错误: {e}")
        
        st.dataframe(st.session_state.df)
        
        if st.button('重置数据'):
            st.session_state.data_loaded = False
            st.session_state.df = None
            st.rerun()
        
        st.write("分类汇总功能:")
        col1, col2 = st.columns(2)
        
        with col1:
            group_by_columns = st.multiselect(
                "选择分组字段(可多选)",
                st.session_state.df.columns.tolist()
            )
        
        with col2:
            agg_columns = st.multiselect(
                "选择要汇总的字段(可多选)",
                [col for col in st.session_state.df.columns if col not in group_by_columns]
            )
        
        if agg_columns:
            st.write("选择每个字段的汇总方式:")
            agg_methods = {}
            for col in agg_columns:
                if st.session_state.df[col].dtype in ['float64', 'int64']:
                    method = st.selectbox(
                        f"选择 {col} 的汇总方式",
                        ["求和", "平均值", "计数", "最大值", "最小值"],
                        key=f"method_{col}"
                    )
                else:
                    method = "计数"
                    st.info(f"{col} 为文本字段，将进行计数统计")
                agg_methods[col] = method
        
        if st.button("执行汇总"):
            if group_by_columns and agg_columns:
                try:
                    from utils import process_text_count
                    agg_dict = {}
                    for col, method in agg_methods.items():
                        if st.session_state.df[col].dtype == 'object':
                            agg_dict[col] = process_text_count
                        else:
                            if method == "求和":
                                agg_dict[col] = "sum"
                            elif method == "平均值":
                                agg_dict[col] = "mean"
                            elif method == "计数":
                                agg_dict[col] = "count"
                            elif method == "最大值":
                                agg_dict[col] = "max"
                            elif method == "最小值":
                                agg_dict[col] = "min"
                    
                    summary_df = st.session_state.df.groupby(group_by_columns).agg(agg_dict)
                    
                    st.write("汇总结果:")
                    st.dataframe(summary_df)
                    
                    csv = summary_df.to_csv()
                    st.download_button(
                        label="下载汇总结果",
                        data=csv,
                        file_name='summary_data.csv',
                        mime='text/csv'
                    )
                except Exception as e:
                    st.error(f"汇总计算时发生错误: {e}")
        
        if st.button('行列互换'):
            df_transposed = st.session_state.df.transpose()
            st.write("转置后的数据:")
            st.dataframe(df_transposed)
            
            csv_transposed = df_transposed.to_csv(index=True)
            st.download_button(
                label="下载转置后的CSV文件",
                data=csv_transposed,
                file_name='transposed_data.csv',
                mime='text/csv'
            )