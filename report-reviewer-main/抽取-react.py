import os
import json
import re
from concurrent.futures import ThreadPoolExecutor
from docx import Document
from docx.shared import RGBColor
from openai import OpenAI

import utils
from config import chouqu_canshu, chouqu_shili

all_text = ""
correct = 0
cuowu = 0
zongshu = 0
total = 0
chouqu_canshu_dict = {
    "项目名称": "项目-项目名称",
    "项目地点": "项目-项目地点（省市县）",
    "项目地址": "项目-项目地点（省市县）",
    "项目业主单位名称": "项目-项目业主单位名称",
    "规划装机容量": "项目-规划装机容量",
    "场区跨度": "项目-场区跨度",
    "场区跨度（南北向）": "项目-场区跨度",
    "场区跨度（东西向）": "项目-场区跨度",
    "海拔高度": "项目-海拔高度",
    "风机型号": "项目-风机型号",
    "单机容量": "项目-单机容量",
    "风轮直径": "项目-叶轮直径",
    "轮毂高度": "项目-轮毂高度",
    "风电机组数量": "项目-风电机组台数",
    "风电机组台数": "项目-风电机组台数",
    "年上网电量": "规划-年上网电量",
    "年上网电量（考虑限电）": "规划-年上网电量",
    "年等效满负荷小时数": "规划-年等效满负荷小时数",
    "年等效满负荷小时数（考虑限电）": "规划-年等效满负荷小时数",
    "风电机组变流器额定电压": "电气-电压等级-风电机组变流器额定电压（网侧）",
    "升压站电压等级": "升压站电压等级",
    "并网点电压水平": "并网点电压水平",
    "母线电压": "母线电压",
    "集电线路进线回数": "集电线路进线回数",
    "集电线路进线回路": "集电线路进线回数",
    "升压站系统出线回路数": "升压站系统出线回路数",
    "升压站系统出现回路数": "升压站系统出线回路数",
    "储能进线数": "储能进线数",
    "站区命名方式": "电气-站区命名方式",
    "抗震设防烈度": "土建-抗震设防烈度",
    "基本地震动峰值加速度": "土建-基本地震动峰值加速度",
    "地震动峰值加速度": "土建-基本地震动峰值加速度",
    "基本地震动加速度反应谱特征周期": "土建-基本地震动加速度反应谱特征周期",
    "设计地震分组": "土建-设计地震分组",
    "资本金比例": "财务-资本金比例",
    "长期贷款利率": "财务-长期贷款利率",
    "施工辅助工程费": "概算-施工辅助工程费",
    "设备及安装工程费": "概算-设备及安装工程费",
    "建筑工程费": "概算-建筑工程费",
    "其它费用": "概算-其它费用",
    "基本预备费": "概算-基本预备费",
    "建设期贷款利息": "概算-建设期贷款利息",
    "风电场动态总投资": "概算-风电场动态总投资",
    "风电场静态千瓦动态投资": "概算-风电场静态千瓦动态投资",
    "风电场静态千瓦静态投资": "概算-风电场静态千瓦静态投资",
    "风电场建设期利息": "概算-风电场建设期利息",
    "送出工程静态总投资": "概算-送出工程静态总投资",
    "送出工程建设期利息": "概算-送出工程建设期利息",
    "送出工程动态投资": "概算-送出工程动态投资",
    "项目静态总投资": "概算-项目静态总投资",
    "项目建设期利息": "概算-项目建设期利息",
    "项目动态总投资": "概算-项目动态总投资（不含流动资金）",
    "项目单位千瓦静态投资": "概算-项目单位千瓦静态投资",
    "项目单位千瓦动态投资": "概算-项目单位千瓦动态投资"
}


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


def chat_entity_task(all_text, enter_type, cunzaishiti_list):
    global correct
    global cuowu
    global total
    if all_text.strip() == '':
        return {enter_type: []}
    geshi = {enter_type: []}
    # 定义实体抽取任务的提示词

    response1=utils.cunzaixing(all_text,enter_type)
    response2=utils.panduanyizhixing(all_text, enter_type,response1)
    response3=utils.shengchengshiti(all_text, enter_type,response1,response2)


    pattern = r'```json([\s\S]*?)```'

    response_json = re.findall(pattern, response3)[-1].replace("'", '"')
    response_json = json.loads(response_json)


    shiti_list=[]
    for shiti in response_json[enter_type]:
        if str(shiti) in all_text:
            shiti_list.append(str(shiti))

    print("--------------------------")
    print(1)
    print(response1)
    print(2)
    print(response2)
    print(3)
    print(response3)
    print(4)

    print("json")
    print(shiti_list)
    print("--------------------------")
    return [enter_type, shiti_list]

    # print(all_text)
    # print(response1)
    # print("-----------------------------")


def process_content(content, chouqu_canshu, item, cunzaishiti_list):
    text = content
    if text.strip() == "":
        return

    item['moxingshuchu'] = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(chat_entity_task, text, enter_type, cunzaishiti_list) for enter_type in
                   chouqu_canshu[:]]
        for future in futures:
            response = future.result()

            if response[1] != []:
                item['moxingshuchu'].append(response)


wenben_gir = "./为拆分后的文本添加标注"
# List to hold paths of .docx files
docx_files = []

# Walk through the directory
for root, dirs, files in os.walk(wenben_gir):
    for file in files:
        if file.endswith(".json") and not file.startswith("~$"):
            # Add full path of each .docx file to the list

            file_path = os.path.join(root, file)

            with open(file_path, 'r', encoding='utf-8') as json_file:
                data = json.load(json_file)
            print(file_path)
            for item in data[:]:
                cunzaishiti_list = []
                contents = item['content']
                all_text = ""
                for content in contents:
                    all_text += content['text']
                    all_text += "\n"
                    for annotation in content['annotations']:
                        cunzaishiti_list.append(chouqu_canshu_dict[annotation[0]])

                try:
                    cunzaishiti_list = list(set(cunzaishiti_list))
                    zongshu += len(cunzaishiti_list)
                    process_content(all_text, chouqu_canshu, item, cunzaishiti_list)
                except:
                    continue

            with open(file_path, 'w', encoding='utf-8') as json_file:
                json.dump(data, json_file, ensure_ascii=False, indent=4)

