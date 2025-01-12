# data_cleaning.py

import pandas as pd

def clean_data(file):
    try:
        data = pd.read_csv(file)
        cleaned_data = []
        
        for index, row in data.iterrows():
            current_person_data = {}
            
            for col in data.columns:
                if pd.notnull(row[col]):
                    if col.endswith('（1'):
                        col_name = col[:-3]
                    else:
                        col_name = col
                        
                    parts = col_name.split('.')
                    if len(parts) > 1:
                        question_num = parts[0]
                        sub_parts = parts[1].split(':')
                        if len(sub_parts) > 1:
                            area = sub_parts[0].strip()
                            name_parts = sub_parts[1].split('-')
                            if len(name_parts) > 1:
                                name = name_parts[0].strip()
                                dimension = name_parts[1].split('（')[0].strip()
                                value = row[col]
                                
                                if name not in current_person_data:
                                    current_person_data[name] = {
                                        '被测人员姓名': name,
                                        '单位': area,
                                        dimension: value
                                    }
                                else:
                                    current_person_data[name][dimension] = value
                                    
            cleaned_data.extend(current_person_data.values())
        
        cleaned_df = pd.DataFrame(cleaned_data)
        
        if '总体评价' not in cleaned_df.columns:
            cleaned_df['总体评价'] = ''
            
        return cleaned_df

    except Exception as e:
        print(f"数据清洗过程中出现错误: {e}")
        return None