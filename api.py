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
        model="glm-4-air",
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


