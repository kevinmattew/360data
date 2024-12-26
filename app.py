import streamlit as st
import pandas as pd

def clean_data(file):
    try:
        # 读取 CSV 数据
        data = pd.read_csv(file)

        cleaned_data = []

        for col in data.columns:
            if col.endswith('（1'):
                new_col = col[:-3]
            else:
                new_col = col
            parts = new_col.split('.')
            if len(parts) > 1:
                sub_parts = parts[1].split(':')
                if len(sub_parts) > 1:
                    area = sub_parts[0].strip()
                    name_parts = sub_parts[1].split('-')
                    if len(name_parts) > 1:
                        name = name_parts[0].strip()
                        dimension = name_parts[1].strip()
                        for index, value in data[col].items():
                            if pd.notnull(value):
                                print(f"处理行: {index}, 列: {col}, 值: {value}, 区域: {area}, 姓名: {name}, 维度: {dimension}")  # 添加打印语句
                                existing_row = next(
                                    (r for r in cleaned_data if r['被测人员姓名'] == name and r['单位'] == area), None
                                )
                                if existing_row:
                                    print(f"更新行: {existing_row}")  # 打印更新前的行
                                    existing_row[dimension] = value
                                    print(f"更新后行: {existing_row}")  # 打印更新后的行
                                else:
                                    new_row = {'被测人员姓名': name, '单位': area, dimension: value}
                                    print(f"添加新行: {new_row}")  # 打印添加的新行
                                    cleaned_data.append(new_row)

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