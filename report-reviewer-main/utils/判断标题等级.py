import re

# 一级标题正则


# 测试样本
sample_texts = [
    "1     综合说明",  # 一级标题
    "1.1 概述",  # 二级标题
    "1.1.1 气象概况",  # 三级标题
    "1.1.1.1 子节",  # 四级标题
    "1.1.1.1.1 子节五",  # 五级标题
    "2 项目背景",  # 一级标题
    "2.1 市场分析",  # 二级标题
    "1.1.1.1 目标设定",  # 四级标题
    "1.2.3.4.1 目标细节"  # 五级标题
]

# 判断标题级别的函数
def get_title_level(text):
    TITLE_REGEX_1 = r'^\d+\s+[\u4e00-\u9fa5A-Za-z0-9]+.*$'

    # 二级标题正则
    TITLE_REGEX_2 = r'^\d+\.\d+\s+[\u4e00-\u9fa5A-Za-z0-9]+.*$'

    # 三级标题正则
    TITLE_REGEX_3 = r'^\d+\.\d+\.\d+\s+[\u4e00-\u9fa5A-Za-z0-9]+.*$'

    # 四级标题正则
    TITLE_REGEX_4 = r'^\d+\.\d+\.\d+\.\d+\s+[\u4e00-\u9fa5A-Za-z0-9]+.*$'

    # 五级标题正则
    TITLE_REGEX_5 = r'^\d+\.\d+\.\d+\.\d+\.\d+\s+[\u4e00-\u9fa5A-Za-z0-9]+.*$'

    if re.match(TITLE_REGEX_5, text):
        return 5
    elif re.match(TITLE_REGEX_4, text):
        return 4
    elif re.match(TITLE_REGEX_3, text):
        return 3
    elif re.match(TITLE_REGEX_2, text):
        return 2
    elif re.match(TITLE_REGEX_1, text):
        return 1
    return None  # 如果没有匹配到，则返回None

# 测试每个标题并输出标题等级
def test_title_regex():
    print("测试结果：\n")
    for text in sample_texts:
        level = get_title_level(text)
        if level:
            print(f"标题: {text} - 等级: {level}")

if __name__ == "__main__":
    test_title_regex()
