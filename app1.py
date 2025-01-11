import streamlit as st
import pandas as pd

# 设置页面标题
st.title("问卷数据分割与汇总工具")

# 创建文件上传器
file = st.file_uploader("上传CSV文件", type=["csv"])

if file is not None:
    # 读取CSV文件，注意编码格式
    df = pd.read_csv(file, encoding='utf-8-sig')
    
    # 显示原始数据
    st.write("原始数据:")
    st.dataframe(df)
    
    # 选择要处理的列
    selected_column = st.selectbox("选择要处理的列", df.columns)
    
    # 获取用户输入的分隔符
    top_delimiter = st.text_input("输入顶级分隔符（分隔不同干部）", value="|")
    sub_delimiter = st.text_input("输入次级分隔符（分隔姓名、职位、评价）", value=",")
    
    # 处理数据
    processed_data = []
    for index, row in df.iterrows():
        text = row[selected_column]
        # 按顶级分隔符分割
        parts = text.split(top_delimiter)
        for part in parts:
            # 按次级分隔符分割，最多分三部分
            sub_parts = part.split(sub_delimiter, 2)
            if len(sub_parts) >= 3:
                name = sub_parts[0].strip()
                position = sub_parts[1].strip()
                evaluation = sub_parts[2].strip()
                processed_data.append({
                    '编号': row['编号'],
                    '姓名': name,
                    '职位': position,
                    '评价': evaluation
                })
    
    # 创建处理后的DataFrame
    processed_df = pd.DataFrame(processed_data)
    
    # 显示处理后的数据
    st.write("处理后的数据:")
    st.dataframe(processed_df)
    
    # 提供下载选项
    st.download_button(
        label="下载处理后的数据",
        data=processed_df.to_csv(index=False),
        file_name='processed_data.csv',
        mime='text/csv'
    )
