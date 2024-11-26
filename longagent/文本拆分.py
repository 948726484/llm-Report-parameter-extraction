# Walk through the directory
import json
import os
import re

from api import chat_deepseek,chat_glm4
from config import chouqu_canshu
wenben_gir = "../为拆分后的文本添加标注"

for root, dirs, files in os.walk(wenben_gir):
    for file in files:
        if file.endswith("【太康】2 风能资源-20240302.json") and not file.startswith("~$"):
            # Add full path of each .docx file to the list

            file_path = os.path.join(wenben_gir, file)
            text_chunks=[]
            with open(file_path, 'r', encoding='utf-8') as json_file:
                data = json.load(json_file)
            currect_chunk = ''
            for item in data:
                title=item['title']
                if len(currect_chunk)>1000:
                    text_chunks.append(currect_chunk)
                    currect_chunk = ''
                currect_chunk+=title
                for content in item['content']:
                    currect_chunk+=content['text']
            print(file_path)
            print(len(text_chunks))
            quanwen_canshuzhi=[]
            for enter_type in chouqu_canshu:
                juhe_list=[]

                for text_chunk in text_chunks:
                    response_list=[]
                    prompt=f"""文档：{text_chunk}\n
介绍：
基于所给段落回答问题，回答必须从所给段落中抽取

问题：文本中是否直接提及【{enter_type}】的实体信息，排除相似类型，不要推断。注意区分原文和所给实体名的细微差异，如测风塔海拔高度与项目海拔高度虽然都涉及海拔高度，但主体不一样，不属于直接提及。

请使用<scratchpad>标记总结文档中与指令相关的内容，然后描述你的响应。你的响应必须遵循JSON格式：```json{{"type"： "response","content"： "your_response_content","has_answer":true or false}}```,内容必须尽可能简洁,若文本中不存在【{enter_type}】请简要说明。"""
                    respone =chat_deepseek(prompt)
                    pattern = r'```json([\s\S]*?)```'

                    response_json = re.findall(pattern, respone)[0].replace("'", '"')
                    response_json = json.loads(response_json)
                    # print(respone)
                    # print(response_json)
                    response_list.append(respone)
                    if response_json['has_answer']==True:
                        juhe_list.append([text_chunk,response_json])
                        # print(text_chunk)
                        # print(enter_type)
                        # print(respone)
                        print(response_json)
                        print("---------------------")
                if len(juhe_list)>0:
                    promt_juhe=''
                    for i,juhe in enumerate(juhe_list):
                        promt_juhe+=f"文档{i+1}：{juhe[0]}"
                        promt_juhe+="\n\n"
                    promt_juhe+=f"""上述内容是一个风电项目报告，请基于上述文本，构建全局语义信息，你的摘要应围绕风电场信息或项目信息展开，说明关键信息：{enter_type}的属性值。
                摘要："""
                    quanwen_response=chat_deepseek(promt_juhe)
                    # pattern = r'```json([\s\S]*?)```'
                    #
                    # quanwen_response_json = re.findall(pattern, quanwen_response)[0].replace("'", '"')
                    # quanwen_response_json = json.loads(quanwen_response_json)
                    # quanwen_canshuzhi.append([enter_type,quanwen_response_json])
                    print(quanwen_response)
                    print("------------------------------")







