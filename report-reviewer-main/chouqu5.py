import os
import json
import re
from concurrent.futures import ThreadPoolExecutor
from docx import Document
from docx.shared import RGBColor
from openai import OpenAI
from config import chouqu_canshu

all_text = ""

def chat_glm4(instruction):
    from zhipuai import ZhipuAI

    # Initialize the ZhipuAI client
    api_key = "8e37d7388acc98f5b181617b2af2f2f1.YFGRZ2IXZkKM2CeC"
    zhipu_client = ZhipuAI(api_key=api_key)

    response = zhipu_client.chat.completions.create(
        model="glm-4-flash",
        messages=[
            {"role": "user", "content": instruction},
        ],
        stream=False,
    )
    result = response.choices[0].message.content.strip()
    return result

def chat_deepseek(instruction):
    # Initialize the ZhipuAI client
    api_key = "8e37d7388acc98f5b181617b2af2f2f1.YFGRZ2IXZkKM2CeC"
    client = OpenAI(api_key="sk-13b18196a98041f7a3c616bcc99a9592", base_url="https://api.deepseek.com")

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "user", "content": instruction},
        ],
        stream=False,
    )
    result = response.choices[0].message.content.strip()
    return result


def chat_entity_task(all_text, enter_type):
    if all_text.strip() == '':
        return {enter_type: []}
    # 定义实体抽取任务的提示词
    instruction = f"""

文本内容：{all_text}

问题：文本中是否直接提及【{enter_type}】的实体信息，排除相似类型，不要推断,。
回复格式：说明文本中是否直接提及了【{enter_type}】的实体信息，具体信息是什么。
注意区分原文和所给实体名的细微差异，如测风塔海拔高度与项目海拔高度不一致。"""

    response1 = chat_deepseek(instruction.strip())
    # print(response1)
    # print("---------------------")

    instruction = f"""文本中{enter_type}的具体实体信息或数值是？{response1}\n\n在上述回答基础上，判断文本中是否包含“{enter_type}”的具体实体信息，实体信息应与实体类型直接对应而不是相关，输出True或False。"""
    response2 = chat_deepseek(instruction)
    # print(response2)
    # print("---------------------")

    if "True" in response2:
        geshi = {enter_type: []}
        instruction = f"""任务描述：
1. 请从上述文本中提取与“{enter_type}”相关的所有实体值，实体值是指实体的某个具体属性或特征的值，这些词汇或短语可以是人名、地名、组织机构名、时间、日期、数量等，排除形容词实体值。
2. 请以JSON格式输出结果，列表中直接存储实体信息的字符串，格式为：```json{geshi}```。
3. 如果文本中不存在“{enter_type}”的相关信息，请维持json空列表```json{geshi}```。
4.规范实体信息界限，如{{"集电线路根数": ["风电场分别共设12回35kV集电线路"]}}应改为{{"集电线路根数 ": ["12回"]}}


问题：文本中是否直接提及【{enter_type}】的实体值？回答：{response1}

文本内容：{all_text}"""
        response3 = chat_deepseek(instruction)
        # response3 = response3.replace("```json", "").replace("```", "")
        # response3 = json.loads(response3)

        pattern = r'```json([\s\S]*?)```'

        response3 = re.findall(pattern, response3)[0].replace("'", '"')
        response3 = json.loads(response3)
        print(all_text)
        print(response1)
        print(response2)
        print(response3)
        print("---------------------")
        chouqu_enter_list = response3[enter_type]
        for chouqu_enter in chouqu_enter_list:
            if chouqu_enter not in all_text:
                print("校正实体抽取结果")
                instruction = f"""文本内容：{all_text}

实体抽取结果：{response3}  

抽取的实体信息{response3[enter_type]}在文本中不存在，请对齐文本字符，并规范实体范围。如{{'抗震设防烈度':'7'}}"""
                response4 = chat_deepseek(instruction)
                response4 = response4.replace("```json", "").replace("```", "").replace("‘", '"')
                response3 = json.loads(response4)
                print(f"校正实体抽取结果：{response3}")
                break

        return [enter_type, response3[enter_type]]
    else:

        pass
    return [enter_type, []]

def process_content(content, chouqu_canshu,item):
    text = content
    if text.strip() == "":
        return

    item['moxingshuchu']=[]
    with ThreadPoolExecutor(max_workers=len(chouqu_canshu)) as executor:
        futures = [executor.submit(chat_entity_task, text, enter_type) for enter_type in chouqu_canshu]
        for future in futures:
            response = future.result()
            if response[1] != []:
                item['moxingshuchu'].append(response)

file_path = r"./【太康】3 工程地质与水文-20240201.json"
file_path2 = r"./output2.json"
with open(file_path, 'r', encoding='utf-8') as json_file:
    data = json.load(json_file)

for item in data:
    contents = item['content']
    all_text=""
    for content in contents:
        all_text+=content['text']
        all_text +="\n"
    try:
        process_content(all_text, chouqu_canshu,item)
    except:
        continue

with open(file_path2, 'w', encoding='utf-8') as json_file:
    json.dump(data, json_file, ensure_ascii=False, indent=4)
