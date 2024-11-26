import json
from zipfile import ZipFile
from re import findall
import re

fn = r"./已标注/【太康】3 工程地质与水文-20240201.docx"
biaozhu = []
baocun=[]
with ZipFile(fn) as fp:
    try:
        # 读取 comments.xml 内容
        comments_content = fp.read('word/comments.xml').decode('utf8')
    except KeyError:
        comments_content = ''

    if not comments_content:
        print('这个文档没有批注')
    else:
        # 匹配每个 <w:comment> 块，提取 id, author 和内容
        comments = findall(r'<w:comment w:id="(\d+)" w:author="([^"]+)"[^>]*>(.*?)</w:comment>', comments_content,
                           flags=re.DOTALL)

        for comment_id, author, comment_body in comments:
            # 从 comment_body 中提取批注文本
            comment_text = ''.join(findall(r'<w:t>(.*?)</w:t>', comment_body))
            print(f"批注ID: {comment_id}")
            print(f"作者: {author}")
            print(f"批注内容: {comment_text}")
            print("-" * 30)
            biaozhu.append([comment_id, author, comment_text])

    # 读取 document.xml 内容
    document_content = fp.read('word/document.xml').decode('utf8')

    # 解析 document.xml 内容，识别批注选中的原文片段和所在的文本段落
    for comment_id, author, comment_text in biaozhu:
        # 查找批注选中的原文片段
        comment_range_start = f'<w:commentRangeStart w:id="{comment_id}"/>'
        comment_range_end = f'<w:commentRangeEnd w:id="{comment_id}"/>'
        comment_reference = f'<w:commentReference w:id="{comment_id}"/>'

        # 找到批注选中的原文片段
        start_index = document_content.find(comment_range_start)
        end_index = document_content.find(comment_range_end)

        if start_index != -1 and end_index != -1:
            # 提取原文片段
            selected_text = document_content[start_index:end_index].split('</w:t>')[-2].split('<w:t>')[1]
            biaozhu_xml_pre_len=len(document_content[start_index:end_index].split(selected_text)[0])
            print(f"批注ID: {comment_id} 选中的原文片段: {selected_text}")

            # 找到批注所在的段落
            paragraph_start = document_content.rfind('<w:p', 0, start_index)
            paragraph_end = document_content.find('</w:p>', start_index)

            if paragraph_start != -1 and paragraph_end != -1:
                paragraph_text = document_content[paragraph_start:paragraph_end]
                paragraph_text_list=findall(r'<w:t>(.*?)</w:t>', paragraph_text)
                biaozhu_xml_strat=start_index-paragraph_start
                biaozhu_xml_pre=paragraph_text[:biaozhu_xml_strat]
                biaozhu_pre_text_strat =len(''.join( findall(r'<w:t>(.*?)</w:t>', biaozhu_xml_pre)))
                biaozhu_pre_text_end=len(selected_text)+biaozhu_pre_text_strat
                paragraph_text = ''.join(paragraph_text_list)
                print(f"批注ID: {comment_id} 所在的段落: {paragraph_text}")
                print("-" * 30)
                if selected_text!=paragraph_text[biaozhu_pre_text_strat:biaozhu_pre_text_end]:
                    print(1)
                baocun.append({
                    "参数类型":comment_text,
                    "参数值":selected_text,
                "文本段落":paragraph_text,
                    "起始点":biaozhu_pre_text_strat,
                    "终止点":biaozhu_pre_text_end
                })

with open('批注信息.json', 'w', encoding='utf-8') as json_file:
    json.dump(baocun, json_file, ensure_ascii=False, indent=4)

print("批注信息已保存为 JSON 文件")

