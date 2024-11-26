import json
from zipfile import ZipFile
from re import findall
import re
import os

from bs4 import BeautifulSoup


def extract_comments_from_docx(docx_path):
    biaozhu = []
    baocun = []

    with ZipFile(docx_path) as fp:
        try:
            # 读取 comments.xml 内容
            comments_content = fp.read('word/comments.xml').decode('utf8')
        except KeyError:
            comments_content = ''

        if not comments_content:
            print(f'{docx_path} 这个文档没有批注')
        else:
            # 匹配每个 <w:comment> 块，提取 id, author 和内容
            comments = findall(r'<w:comment w:id="(\d+)" w:author="([^"]+)"[^>]*>(.*?)</w:comment>', comments_content,
                               flags=re.DOTALL)

            for comment_id, author, comment_body in comments:
                # 从 comment_body 中提取批注文本
                comment_text = ''.join(findall(r'<w:t>(.*?)</w:t>', comment_body))
                biaozhu.append([comment_id, author, comment_text])

        # 读取 document.xml 内容
        document_content = fp.read('word/document.xml').decode('utf8')

        # 解析 document.xml 内容，识别批注选中的原文片段和所在的文本段落
        for comment_id, author, comment_text in biaozhu:
            # 查找批注选中的原文片段
            comment_range_start = f'<w:commentRangeStart w:id="{comment_id}"/>'
            comment_range_end = f'<w:commentRangeEnd w:id="{comment_id}"/>'

            # 找到批注选中的原文片段
            start_index = document_content.find(comment_range_start)
            end_index = document_content.find(comment_range_end)

            if start_index != -1 and end_index != -1:
                # 提取原文片段
                selected_text = document_content[start_index:end_index].split('</w:t>')[-2].split('<w:t>')[1]
                biaozhu_xml_pre_len = len(document_content[start_index:end_index].split(selected_text)[0])

                # 找到批注所在的段落
                paragraph_start = document_content.rfind('<w:p', 0, start_index)
                paragraph_end = document_content.find('</w:p>', start_index)

                if paragraph_start != -1 and paragraph_end != -1:
                    paragraph_text = document_content[paragraph_start:paragraph_end]
                    paragraph_text_list = re.findall(r'<w:t[^>]*>(.*?)</w:t>', paragraph_text)

                    biaozhu_xml_start = start_index - paragraph_start
                    biaozhu_xml_pre = paragraph_text[:biaozhu_xml_start]
                    biaozhu_pre_text = ''.join(findall(r'<w:t[^>]*>(.*?)</w:t>', biaozhu_xml_pre))
                    biaozhu_pre_text_strat = biaozhu_pre_text.rfind("<w:t")
                    biaozhu_pre_text_end = biaozhu_pre_text.find(">", wt_strat)
                    biaozhu_pre_text = biaozhu_pre_text[biaozhu_pre_text_end + 1:]
                    biaozhu_pre_text_start = len(''.join(findall(r'<w:t[^>]*>(.*?)</w:t>', biaozhu_xml_pre)))
                    biaozhu_pre_text_end = len(selected_text) + biaozhu_pre_text_start
                    paragraph_text = ''.join(paragraph_text_list)
                    wt_strat = paragraph_text.rfind("<w:t")
                    wt_end = paragraph_text.find(">", wt_strat)
                    paragraph_text2 = paragraph_text[wt_end + 1:]
                    if selected_text != paragraph_text2[biaozhu_pre_text_start:biaozhu_pre_text_end]:
                        print(selected_text)
                        print(paragraph_text2[biaozhu_pre_text_start:biaozhu_pre_text_end])
                        print(paragraph_text2)
                        print(f"批注ID: {comment_id} 选中的原文片段与段落不匹配")
                        print("--------------------------------------")
                    else:
                        # print(f"批注ID: {comment_id} 正确识别：{paragraph_text[biaozhu_pre_text_start:biaozhu_pre_text_end]}")
                        pass

                    baocun.append({
                        "参数类型": comment_text,
                        "参数值": selected_text,
                        "文本段落": paragraph_text2,
                        "起始点": biaozhu_pre_text_start,
                        "终止点": biaozhu_pre_text_end
                    })

    return baocun


def process_directory(directory_path, output_directory):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith("已标注【太康】8 土建工程-20240302.docx") and not file.startswith("~$"):
                docx_path = os.path.join(root, file)
                print(f"Processing {docx_path}")
                comments_info = extract_comments_from_docx(docx_path)

                if comments_info:
                    json_output_path = os.path.join(output_directory, f"{os.path.splitext(file)[0]}.json")
                    with open(json_output_path, 'w', encoding='utf-8') as json_file:
                        print(len(comments_info))
                        json.dump(comments_info, json_file, ensure_ascii=False, indent=4)
                    print(f"批注信息已保存为 {json_output_path}")
                else:
                    print(f"{docx_path} 没有批注信息")


# 指定目录路径
input_directory = r"./原始标注文本"
output_directory = r"./获取标注"

# 处理目录中的所有 .docx 文件
import json
from zipfile import ZipFile
from re import findall
import re
import os


def extract_comments_from_docx(docx_path):
    biaozhu = []
    baocun = []

    with ZipFile(docx_path) as fp:
        try:
            # 读取 comments.xml 内容
            comments_content = fp.read('word/comments.xml').decode('utf8')
        except KeyError:
            comments_content = ''

        if not comments_content:
            print(f'{docx_path} 这个文档没有批注')
        else:
            # 匹配每个 <w:comment> 块，提取 id, author 和内容
            comments = findall(r'<w:comment w:id="(\d+)" w:author="([^"]+)"[^>]*>(.*?)</w:comment>', comments_content,
                               flags=re.DOTALL)

            for comment_id, author, comment_body in comments:
                # 从 comment_body 中提取批注文本
                comment_text = ''.join(findall(r'<w:t>(.*?)</w:t>', comment_body))
                biaozhu.append([comment_id, author, comment_text])

        # 读取 document.xml 内容
        document_content = fp.read('word/document.xml').decode('utf8')

        # 解析 document.xml 内容，识别批注选中的原文片段和所在的文本段落
        for comment_id, author, comment_text in biaozhu:
            # 查找批注选中的原文片段
            comment_range_start = f'<w:commentRangeStart w:id="{comment_id}"/>'
            comment_range_end = f'<w:commentRangeEnd w:id="{comment_id}"/>'

            # 找到批注选中的原文片段
            start_index = document_content.find(comment_range_start)
            end_index = document_content.find(comment_range_end)

            if start_index != -1 and end_index != -1:
                # 提取原文片段
                selected_text = document_content[start_index:end_index].split('</w:t>')[-2].split('<w:t>')[1]
                selected_text = ''.join(findall(r'(?<=<w:t>).*?(?=</w:t>)', document_content[start_index:end_index]))
                biaozhu_xml_pre_len = len(document_content[start_index:end_index].split(selected_text)[0])

                # 找到批注所在的段落
                paragraph_start = document_content.rfind('<w:p', 0, start_index)
                paragraph_end = document_content.find('</w:p>', start_index)

                if paragraph_start != -1 and paragraph_end != -1:
                    paragraph_text_xml = document_content[paragraph_start:paragraph_end]
                    # paragraph_text_list = re.findall(r'>(.*?)<\/w:t>', paragraph_text_xml)
                    soup = BeautifulSoup(paragraph_text_xml, 'html.parser')
                    paragraph_text_list = [t_tag.get_text(strip=False) for t_tag in soup.find_all('w:t')]

                    biaozhu_xml_start = start_index - paragraph_start
                    biaozhu_xml_pre = paragraph_text_xml[:biaozhu_xml_start]

                    soup = BeautifulSoup(biaozhu_xml_pre, 'html.parser')
                    biaozhu_xml_pre_list = [t_tag.get_text(strip=False) for t_tag in soup.find_all('w:t')]

                    biaozhu_xml_pre_text = ''.join(biaozhu_xml_pre_list)

                    biaozhu_pre_text_start = len(biaozhu_xml_pre_text)
                    biaozhu_pre_text_end = len(selected_text) + biaozhu_pre_text_start
                    paragraph_text = ''.join(paragraph_text_list)
                    wt_strat = paragraph_text.rfind("<w:t")
                    wt_end = paragraph_text.find(">", wt_strat)
                    paragraph_text2 = paragraph_text[wt_end + 1:]
                    if selected_text != paragraph_text2[biaozhu_pre_text_start:biaozhu_pre_text_end]:
                        print(selected_text)
                        print(paragraph_text2[biaozhu_pre_text_start:biaozhu_pre_text_end])
                        print(paragraph_text2)
                        print(f"批注ID: {comment_id} 选中的原文片段与段落不匹配")
                        print("--------------------------------------")
                    else:
                        # print(f"批注ID: {comment_id} 正确识别：{paragraph_text[biaozhu_pre_text_start:biaozhu_pre_text_end]}")
                        pass

                    baocun.append({
                        "参数类型": comment_text,
                        "参数值": selected_text,
                        "文本段落": paragraph_text2,
                        "起始点": biaozhu_pre_text_start,
                        "终止点": biaozhu_pre_text_end
                    })

    return baocun


def process_directory(directory_path, output_directory):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".docx") and not file.startswith("~$"):
                docx_path = os.path.join(root, file)
                print(f"Processing {docx_path}")
                comments_info = extract_comments_from_docx(docx_path)

                if comments_info:
                    json_output_path = os.path.join(output_directory, f"{os.path.splitext(file)[0]}.json")
                    with open(json_output_path, 'w', encoding='utf-8') as json_file:
                        print(len(comments_info))
                        json.dump(comments_info, json_file, ensure_ascii=False, indent=4)
                    print(f"批注信息已保存为 {json_output_path}")
                else:
                    print(f"{docx_path} 没有批注信息")


# 指定目录路径
input_directory = r"./原始标注文本"
output_directory = r"./获取标注"

# 处理目录中的所有 .docx 文件
process_directory(input_directory, output_directory)