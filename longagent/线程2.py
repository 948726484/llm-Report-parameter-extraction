import json
import os
import re
import concurrent.futures

from chouqu import chat_deepseek, chat_glm4
from config import chouqu_canshu

wenben_gir = "../为拆分后的文本添加标注"

def process_text_chunk(text_chunk, enter_type):
    response_list = []
    prompt = f"""文档：{text_chunk}\n
介绍：
基于所给段落回答问题，回答必须从所给段落中抽取

问题：文本中的{enter_type}是？，排除相似类型，不要推断。注意区分原文和所给实体名的细微差异，如测风塔海拔高度与项目海拔高度虽然都涉及海拔高度，但主体不一样，属于未提及。

请使用<scratchpad>标记总结文档中与指令相关的内容，然后描述你的响应。你的响应必须遵循JSON格式：```json{{"type"： "response","content"： "your_response_content","has_answer":true or false}}```,内容必须尽可能简洁,若文本中不存在【{enter_type}】请简要说明。"""
    respone = chat_deepseek(prompt)
    pattern = r'```json([\s\S]*?)```'
    try:

        response_json = re.findall(pattern, respone)[0].replace("'", '"')
        response_json = json.loads(response_json)
        response_list.append(respone)
        if response_json['has_answer'] == True:
            return [text_chunk, response_json,enter_type]
    except:
        return None
    return None

def process_file(file_path):
    text_chunks = []
    with open(file_path, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    currect_chunk = ''
    for item in data:
        title = item['title']
        if len(currect_chunk) > 1000:
            text_chunks.append(currect_chunk)
            currect_chunk = ''
        currect_chunk += title
        for content in item['content']:
            currect_chunk += content['text']
    text_chunks.append(currect_chunk)

    print(file_path)
    print(len(text_chunks))

    quanwen_canshuzhi = []
    juhe_list=[]
    for enter_type in chouqu_canshu:


        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = []
            for text_chunk in text_chunks:
                futures.append(executor.submit(process_text_chunk, text_chunk, enter_type))

            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    juhe_list.append(result)

    if len(juhe_list) > 0:
        promt_juhe = ''
        wendang_shuxing=set()
        for i, juhe in enumerate(juhe_list):
            wendang_shuxing.add(juhe[2])
            if juhe[0] in promt_juhe:
                continue
            promt_juhe += f"文档{i + 1}：{juhe[0]}"
            promt_juhe += "\n\n"

        promt_juhe += f"""上述内容是一个风电项目报告，请基于上述文本，构建关键实体：[{wendang_shuxing}]的全局语义信息，你的摘要应围绕风电场信息或项目信息展开，将文本描述写成一段。
摘要：
"""
        quanwen_response = chat_deepseek(promt_juhe)
        print(enter_type)
        print(quanwen_response)
        print("------------------------------")

for root, dirs, files in os.walk(wenben_gir):
    for file in files:
        if file.endswith("【太康】10 环境保护与水土保持-20240202.json") and not file.startswith("~$"):
            file_path = os.path.join(wenben_gir, file)
            process_file(file_path)