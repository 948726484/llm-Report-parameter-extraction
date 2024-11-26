import os
import re
import json
import zipfile
import xml.etree.ElementTree as ET
from docx import Document


# 一级到五级标题的正则表达式
def get_title_level(para):

    # print(para.style.name)
    if '正文' in para.style.name or 'Normal'in para.style.name or '表'in para.style.name or '图'in para.style.name :
        return None
    if para.style.name.startswith('Heading') or '标题' in para.style.name:
        if para.style.name.startswith('Heading'):
            level = int(re.search(r'Heading (\d+)', para.style.name).group(1))
        else:
            level = int(re.search(r'标题\s*(\d+)', para.style.name).group(1).strip())
        return level




    text=para.text
    TITLE_REGEX_1 = r'^\d+\s+[\u4e00-\u9fa5A-Za-z0-9\s]+.*$'
    TITLE_REGEX_2 = r'^\d+\.\d+\s+[\u4e00-\u9fa5A-Za-z0-9\s]+.*$'
    TITLE_REGEX_3 = r'^\d+\.\d+\.\d+\s+[\u4e00-\u9fa5A-Za-z0-9\s]+.*$'
    TITLE_REGEX_4 = r'^\d+\.\d+\.\d+\.\d+\s+[\u4e00-\u9fa5A-Za-z0-9\s]+.*$'
    TITLE_REGEX_5 = r'^\d+\.\d+\.\d+\.\d+\.\d+\s+[\u4e00-\u9fa5A-Za-z0-9\s]+.*$'

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

        title_level = get_title_level(para)

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
        print(len(data))
        json.dump(data, json_file, ensure_ascii=False, indent=4)


def main():
    # 设置文件路径
    directory = "./原始标注文本"
    out_dir="./按章节拆分的文本"
    # List to hold paths of .docx files
    docx_files = []

    # Walk through the directory
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".docx") and not file.startswith("~$"):
                # Add full path of each .docx file to the list
                file_path=os.path.join(root, file)
                output_file=os.path.join(out_dir, file.replace(".docx",".json"))
                chapters = process_docx(file_path)

                save_to_json(chapters, output_file)
                print(f"处理完成，结果已保存到 {output_file}")


if __name__ == "__main__":
    main()