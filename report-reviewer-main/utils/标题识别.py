import re
import json
import zipfile
import xml.etree.ElementTree as ET
from docx import Document


# 一级到五级标题的正则表达式
def get_title_level(text):
    TITLE_REGEX_1 = r'^\d+\s+[\u4e00-\u9fa5A-Za-z0-9]+.*$'
    TITLE_REGEX_2 = r'^\d+\.\d+\s+[\u4e00-\u9fa5A-Za-z0-9]+.*$'
    TITLE_REGEX_3 = r'^\d+\.\d+\.\d+\s+[\u4e00-\u9fa5A-Za-z0-9]+.*$'
    TITLE_REGEX_4 = r'^\d+\.\d+\.\d+\.\d+\s+[\u4e00-\u9fa5A-Za-z0-9]+.*$'
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
    return None


# 从 docx 文件读取文本并按章节拆分
def process_docx(file_path):
    document = Document(file_path)

    chapters = []
    current_chapter = None

    # 遍历文档中的段落
    for para in document.paragraphs:
        text = para.text.strip()

        if not text:
            continue

        title_level = get_title_level(text)

        # 如果是标题
        if title_level:
            if current_chapter:
                chapters.append(current_chapter)  # 保存前一个章节

            current_chapter = {
                'title': text,
                'level': title_level,
                'content': []
            }
        elif current_chapter:
            # 如果是内容，添加到当前章节的内容中
            content = extract_annotation(text, file_path)  # 提取标注信息
            current_chapter['content'].append(content)

    # 添加最后一个章节
    if current_chapter:
        chapters.append(current_chapter)

    return chapters


# 提取标注信息
def extract_annotation(text, docx_file):
    annotations = []

    # 读取 docx 文件


    return {
        'text': text,
        'annotations': []
    }


# 从 XML 提取评论（批注）信息







# 保存为 JSON 文件
def save_to_json(data, output_file):
    with open(output_file, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)


def main():
    # 设置文件路径
    file_path = r"./已标注/【太康】3 工程地质与水文-20240201.docx"
    output_file = r"./【太康】3 工程地质与水文-20240201.json"

    # 处理 docx 文件并拆分章节
    chapters = process_docx(file_path)

    # 保存结果为 JSON 文件
    save_to_json(chapters, output_file)
    print(f"处理完成，结果已保存到 {output_file}")


if __name__ == "__main__":
    main()