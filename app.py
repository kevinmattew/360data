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

def main():
    """
    Streamlit 主程序
    """
    st.title("数据清洗与转换工具")
    st.subheader("上传 CSV 文件进行数据清洗")

    # 文件上传组件
    uploaded_file = st.file_uploader("选择一个 CSV 文件", type=["csv"])

    if uploaded_file is not None:
        # 数据清洗
        data = clean_data(uploaded_file)

        if data is not None:
            st.success("数据清洗成功！")
            st.dataframe(data)

            # 提供文件下载
            csv = data.to_csv(index=False)
            st.download_button("下载清洗后的数据", csv, "cleaned_data.csv", "text/csv")

if __name__ == "__main__":
    main()
