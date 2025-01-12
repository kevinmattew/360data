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
    st.sidebar.title('导航菜单')
    page = st.sidebar.radio(
        "选择功能页面",
        ["数据处理", "多角色赋分折算"]  # 更新页面名称
    )
    
    if page == "数据处理":
        data_processing_page()
    elif page == "多角色赋分折算":
        role_weight_calculation_page()  # 更新函数名
    else:
        st.error("未知页面")

def data_processing_page():
    """原有的数据处理功能"""
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

def handle_new_table_upload(file, role_name, weight):
    """处理新表格上传"""
    try:
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
        
        st.session_state.uploaded_tables.append({
            'name': role_name,
            'weight': weight,
            'df': df
        })
        st.success(f"成功添加 {role_name} 的评分表")
    except Exception as e:
        st.error(f"上传文件时发生错误: {e}")

def single_weight_mode():
    """单一权重模式处理"""
    # 初始化session state
    if 'uploaded_tables' not in st.session_state:
        st.session_state.uploaded_tables = []
        
    # 上传表格和设置权重
    with st.form("upload_single_form"):
        uploaded_file = st.file_uploader("上传评分表", type=['csv', 'xlsx', 'xls'])
        role_name = st.text_input("角色名称")
        weight = st.number_input("权重", 0.0, 1.0, 1.0, 0.1)
        
        if st.form_submit_button("添加表格"):
            if uploaded_file and role_name:
                handle_new_table_upload(uploaded_file, role_name, weight)
    
    # 显示已上传的表格
    show_uploaded_tables()
    
    # 显示维度计算功能
    if st.session_state.uploaded_tables:
        show_dimension_calculation()

def role_weight_calculation_page():
    """多角色赋分折算功能"""
    st.title('多角色赋分折算')
    
    # 选择权重模式
    weight_mode = st.radio(
        "选择权重模式",
        ["单一权重模式", "多权重模式"]
    )
    
    if weight_mode == "单一权重模式":
        single_weight_mode()
    else:
        multiple_weight_mode()

def multiple_weight_mode():
    """多权重模式处理"""
    if 'uploaded_tables' not in st.session_state:
        st.session_state.uploaded_tables = []
    
    # 批量上传表格
    uploaded_files = st.file_uploader(
        "批量上传评分表", 
        type=['csv', 'xlsx', 'xls'],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        for file in uploaded_files:
            if not any(table['name'] == file.name for table in st.session_state.uploaded_tables):
                try:
                    df = pd.read_csv(file) if file.name.endswith('.csv') else pd.read_excel(file)
                    st.session_state.uploaded_tables.append({
                        'name': file.name,
                        'df': df,
                        'rules': []
                    })
                except Exception as e:
                    st.error(f"处理 {file.name} 时发生错误: {e}")
    
    # 显示和编辑已上传表格
    for i, table in enumerate(st.session_state.uploaded_tables):
        with st.expander(f"表格 #{i+1}"):
            # 表格名称编辑
            new_name = st.text_input("表格名称", table['name'], key=f"name_{i}")
            if new_name != table['name']:
                st.session_state.uploaded_tables[i]['name'] = new_name
            
            # 显示表格数据
            st.dataframe(table['df'])
            
            # 添加权重规则
            with st.form(f"rule_form_{i}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    rule_column = st.selectbox(
                        "选择判定列",
                        table['df'].columns,
                        key=f"col_{i}"
                    )
                with col2:
                    keyword = st.text_input(
                        "关键词",
                        key=f"keyword_{i}"
                    )
                with col3:
                    weight = st.number_input(
                        "权重",
                        0.0, 1.0, 0.2, 0.1,
                        key=f"weight_{i}"
                    )
                
                if st.form_submit_button("添加规则"):
                    table['rules'].append({
                        'column': rule_column,
                        'keyword': keyword,
                        'weight': weight
                    })
            
            # 显示已添加的规则
            if table['rules']:
                st.write("已添加的权重规则：")
                for rule in table['rules']:
                    st.write(f"列：{rule['column']} | 关键词：{rule['keyword']} | 权重：{rule['weight']}")
            
            # 删除表格按钮
            if st.button("删除此表格", key=f"delete_{i}"):
                st.session_state.uploaded_tables.pop(i)
                st.rerun()
    
    # 批量处理按钮
    if st.session_state.uploaded_tables:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("批量预处理"):
                for i, table in enumerate(st.session_state.uploaded_tables):
                    processed_df = preprocess_single_table(table['df'])
                    if processed_df is not None:
                        st.session_state.uploaded_tables[i]['df'] = processed_df
                st.success("批量处理完成")
                st.rerun()
        
        with col2:
            if st.button("执行多权重计算"):
                results = process_multiple_weights()
                if results:
                    for category, df in results.items():
                        st.write(f"类别：{category}")
                        st.dataframe(df)
                        
                        csv = df.to_csv(index=False)
                        st.download_button(
                            f"下载{category}结果",
                            csv,
                            f"{category}_results.csv",
                            "text/csv"
                        )

def process_multiple_weights():
    """处理多权重计算"""
    try:
        # 选择需要计算的维度
        if len(st.session_state.uploaded_tables) == 0:
            st.warning("请先上传表格")
            return None
            
        first_df = st.session_state.uploaded_tables[0]['df']
        numeric_cols = first_df.select_dtypes(include=['float64', 'int64']).columns
        selected_dims = st.multiselect(
            "选择需要计算的维度",
            numeric_cols
        )
        
        if not selected_dims:
            st.warning("请选择需要计算的维度")
            return None
        
        results = {}
        
        # 处理每张表格
        for table in st.session_state.uploaded_tables:
            df = table['df'].copy()
            
            # 获取姓名和单位列
            name_col = next((col for col in df.columns if "姓名" in col), None)
            unit_col = next((col for col in df.columns if "单位" in col), None)
            
            if not name_col or not unit_col:
                st.error(f"表格 {table['name']} 缺少姓名或单位列")
                continue
            
            # 按规则分组处理
            for rule in table['rules']:
                mask = df[rule['column']].str.contains(rule['keyword'], na=False)
                category_df = df[mask].copy()
                
                if category_df.empty:
                    continue
                
                # 按姓名和单位分组计算平均值
                group_cols = [name_col, unit_col]
                agg_dict = {col: 'mean' for col in selected_dims}
                processed_df = category_df.groupby(group_cols).agg(agg_dict).reset_index()
                
                # 添加权重和来源表信息
                processed_df['权重'] = rule['weight']
                processed_df['来源表'] = table['name']
                
                # 合并到结果
                category = rule['keyword']
                if category not in results:
                    results[category] = processed_df
                else:
                    results[category] = pd.concat([results[category], processed_df])
        
        # 对每个类别进行最终计算
        final_results = {}
        for category, df in results.items():
            # 按姓名和单位合并计算加权得分
            grouped = df.groupby([name_col, unit_col])
            final_df = pd.DataFrame()
            
            # 添加基础信息列
            final_df[name_col] = grouped[name_col].first()
            final_df[unit_col] = grouped[unit_col].first()
            
            # 计算每个维度的加权得分
            for dim in selected_dims:
                weighted_scores = []
                for _, row in df.iterrows():
                    weighted_scores.append(row[dim] * row['权重'])
                final_df[f"{dim}_加权得分"] = grouped.apply(
                    lambda x: sum(x[dim] * x['权重']) / sum(x['权重'])
                )
            
            final_results[category] = final_df.reset_index(drop=True)
        
        return final_results
        
    except Exception as e:
        st.error(f"多权重计算过程中发生错误: {e}")
        return None

def calculate_category_weights(df):
    """计算单个类别的权重"""
    try:
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
        numeric_cols = [col for col in numeric_cols if col != '权重']
        
        # 计算加权得分
        for col in numeric_cols:
            df[f"{col}_加权得分"] = df[col] * df['权重']
            
        return df
        
    except Exception as e:
        st.error(f"类别权重计算过程中发生错误: {e}")
        return None

def show_uploaded_tables():
    """显示已上传的表格"""
    total_weight = sum(table['weight'] for table in st.session_state.uploaded_tables)
    st.info(f"当前权重总和: {total_weight}")
    
    # 显示表格列表
    for i, table in enumerate(st.session_state.uploaded_tables):
        st.subheader(f"{table['name']} (权重: {table['weight']})")
        st.dataframe(table['df'])
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"处理表格 #{i+1}", key=f"process_{i}"):
                processed_df = preprocess_single_table(table['df'])
                if processed_df is not None:
                    st.session_state.uploaded_tables[i]['df'] = processed_df
                    st.success(f"表格 #{i+1} 处理完成")
                    st.rerun()  # 使用st.rerun()替代experimental_rerun
        with col2:
            if st.button(f"删除表格 #{i+1}", key=f"delete_{i}"):
                st.session_state.uploaded_tables.pop(i)
                st.rerun()  # 使用st.rerun()替代experimental_rerun

def preprocess_single_table(df):
    """对单张表格进行预处理"""
    try:
        # 过滤无效列
        df = df.loc[:, ~df.columns.str.contains('Unnamed|序号', na=False)]
        df = df.dropna(axis=1, how='all')
        
        # 查找包含"姓名"和"单位"的列
        name_col = next((col for col in df.columns if "姓名" in col), None)
        unit_col = next((col for col in df.columns if "单位" in col), None)
        
        if not name_col or not unit_col:
            st.error("未找到姓名或单位相关列")
            return None
            
        # 获取数值列和文本列
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
        text_cols = df.select_dtypes(include='object').columns
        text_cols = [col for col in text_cols if col not in [name_col, unit_col]]
        
        # 构建聚合字典
        agg_dict = {}
        for col in numeric_cols:
            agg_dict[col] = 'mean'
        for col in text_cols:
            agg_dict[col] = process_text_count
        
        # 按姓名和单位分组汇总
        processed_df = df.groupby([name_col, unit_col]).agg(agg_dict).reset_index()
        return processed_df
        
    except Exception as e:
        st.error(f"预处理过程中发生错误: {e}")
        return None

def calculate_weighted_scores(selected_dims):
    """计算加权得分"""
    try:
        final_df = None
        
        for table in st.session_state.uploaded_tables:
            df = table['df']
            name_col = next((col for col in df.columns if "姓名" in col), None)
            unit_col = next((col for col in df.columns if "单位" in col), None)
            
            if final_df is None:
                final_df = df.copy()
                final_df['角色'] = table['name']
                final_df['权重'] = table['weight']
            else:
                final_df = pd.merge(
                    final_df,
                    df,
                    on=[name_col, unit_col],
                    how='outer',
                    suffixes=('', f'_{table["name"]}')
                )
        
        # 计算加权得分
        for dim in selected_dims:
            weighted_sum = pd.Series(0, index=final_df.index)
            for table in st.session_state.uploaded_tables:
                weight = table['weight']
                role = table['name']
                dim_col = f"{dim}_{role}" if role in final_df.columns else dim
                if dim_col in final_df.columns:
                    weighted_sum += final_df[dim_col].fillna(0) * weight
            
            final_df[f"{dim}_加权总分"] = weighted_sum
            
        return final_df
        
    except Exception as e:
        st.error(f"权重计算过程中发生错误: {e}")
        return None

def show_dimension_calculation():
    """显示维度计算功能"""
    st.subheader("维度计算")
    
    # 获取第一个表的数值列作为可选维度
    first_df = st.session_state.uploaded_tables[0]['df']
    numeric_cols = first_df.select_dtypes(include=['float64', 'int64']).columns
    
    selected_dims = st.multiselect(
        "选择需要计算的维度", 
        numeric_cols
    )
    
    if selected_dims and st.button("执行权重计算"):
        final_df = calculate_weighted_scores(selected_dims)
        if final_df is not None:
            st.success("计算完成")
            st.dataframe(final_df)
            
            # 下载结果
            csv = final_df.to_csv(index=False)
            st.download_button(
                "下载计算结果",
                csv,
                "weighted_results.csv",
                "text/csv"
            )

def process_single_table(df):
    """处理单个数据表的功能"""
    st.write("数据处理选项:")
    
    # 添加自定义列
    with st.expander("添加自定义列"):
        col1, col2, col3 = st.columns(3)
        with col1:
            new_column_name = st.text_input("新列名称")
        with col2:
            numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns
            selected_columns = st.multiselect("选择要计算的列", numeric_columns)
        with col3:
            calc_method = st.selectbox("计算方式", ["求和", "平均值", "最大值", "最小值"])
    
    # 分类汇总功能
    with st.expander("分类汇总"):
        col1, col2 = st.columns(2)
        with col1:
            group_by_columns = st.multiselect("选择分组字段", df.columns)
        with col2:
            agg_columns = st.multiselect(
                "选择要汇总的字段",
                [col for col in df.columns if col not in group_by_columns]
            )

if __name__ == '__main__':
    # 初始化session state
    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    
    main()
