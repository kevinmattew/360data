import streamlit as st
import pandas as pd

def clean_data(file):
    try:
        # 读取 CSV 数据
        data = pd.read_csv(file)
        cleaned_data = []
        
        # 按行遍历数据
        for index, row in data.iterrows():
            # 存储当前行的处理结果
            current_person_data = {}
            
            for col in data.columns:
                if pd.notnull(row[col]):  # 检查单元格是否有值
                    # 解析列名
                    if col.endswith('（1'):
                        col_name = col[:-3]
                    else:
                        col_name = col
                        
                    parts = col_name.split('.')
                    if len(parts) > 1:
                        question_num = parts[0]  # 题号
                        sub_parts = parts[1].split(':')
                        if len(sub_parts) > 1:
                            area = sub_parts[0].strip()  # 区域
                            name_parts = sub_parts[1].split('-')
                            if len(name_parts) > 1:
                                name = name_parts[0].strip()  # 姓名
                                dimension = name_parts[1].split('（')[0].strip()  # 评测维度
                                value = row[col]
                                
                                # 如果这个人的数据还没有创建，则创建新记录
                                if name not in current_person_data:
                                    current_person_data[name] = {
                                        '被测人员姓名': name,
                                        '单位': area,
                                        dimension: value
                                    }
                                else:
                                    # 如果已存在这个人的记录，则添加新的维度数据
                                    current_person_data[name][dimension] = value
            
            # 将当前行处理的所有人员数据添加到结果列表
            cleaned_data.extend(current_person_data.values())
        
        # 转换为 DataFrame
        cleaned_df = pd.DataFrame(cleaned_data)
        
        if '总体评价' not in cleaned_df.columns:
            cleaned_df['总体评价'] = ''
            
        return cleaned_df

    except Exception as e:
        st.error(f"数据清洗过程中出现错误: {e}")
        return None

def aggregate_data(df, group_by_columns, agg_dict):
    """
    执行数据汇总
    """
    try:
        for col, method in agg_dict.items():
            if df[col].dtype == 'object':  # 文本字段
                agg_dict[col] = process_text_count
        
        # 执行分组汇总
        result = df.groupby(group_by_columns).agg(agg_dict)
        return result
    except Exception as e:
        st.error(f"汇总计算时发生错误: {e}")
        return None

def process_text_count(series):
    """处理文本字段的计数统计
    返回格式如：继续任职 2、不能胜任 1
    """
    # 使用value_counts直接统计每个值的出现次数
    value_counts = series.value_counts()
    # 转换成"文本 数量"的格式
    result = "、".join([f"{key} {value}" for key, value in value_counts.items()])
    return result

def main():
    st.title('360度评估数据处理工具')
    
    # 初始化session state
    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False

    # 添加数据来源选择
    data_source = st.radio(
        "选择数据来源",
        ["上传原始数据进行清洗", "上传已清洗的数据表"]
    )
    
    if data_source == "上传原始数据进行清洗":
        uploaded_file = st.file_uploader("请上传CSV文件", type=['csv'], key='raw_data')
        if uploaded_file is not None and not st.session_state.data_loaded:
            st.session_state.df = clean_data(uploaded_file)
            st.session_state.data_loaded = True
    else:
        uploaded_file = st.file_uploader("请上传已清洗的CSV文件", type=['csv'], key='cleaned_data')
        if uploaded_file is not None and not st.session_state.data_loaded:
            st.session_state.df = pd.read_csv(uploaded_file)
            st.session_state.data_loaded = True
    
    if st.session_state.df is not None:
        # 显示当前数据
        st.write("处理后的数据:")
        st.dataframe(st.session_state.df)
        
        # 添加自定义列功能
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
        # 显示更新后的数据框
        st.dataframe(st.session_state.df)
        
        # 重置数据上传状态按钮
        if st.button('重置数据'):
            st.session_state.data_loaded = False
            st.session_state.df = None
            st.experimental_rerun()
        
        # 分类汇总功能
        st.write("分类汇总功能:")
        col1, col2 = st.columns(2)
        
        with col1:
            group_by_columns = st.multiselect(
                "选择分组字段(可多选)",
                st.session_state.df.columns.tolist()  # 使用session_state
            )
        
        with col2:
            agg_columns = st.multiselect(
                "选择要汇总的字段(可多选)",
                [col for col in st.session_state.df.columns if col not in group_by_columns]  # 使用session_state
            )
        
        # 为每个选择的汇总字段选择汇总方式
        agg_methods = {}
        if agg_columns:
            st.write("选择每个字段的汇总方式:")
            for col in agg_columns:
                if st.session_state.df[col].dtype in ['float64', 'int64']:  # 使用session_state
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
                    agg_dict = {}
                    for col, method in agg_methods.items():
                        if st.session_state.df[col].dtype == 'object':  # 文本字段
                            agg_dict[col] = process_text_count
                        else:  # 数值字段
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
        
        # 转置功能
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

if __name__ == '__main__':
    main()
