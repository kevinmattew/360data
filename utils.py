# utils.py

def process_text_count(series):
    """处理文本字段的计数统计
    返回格式如：继续任职 2、不能胜任 1
    """
    value_counts = series.value_counts()
    result = "、".join([f"{key} {value}" for key, value in value_counts.items()])
    return result