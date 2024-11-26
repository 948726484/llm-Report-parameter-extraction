import json
import os

wenben_json_directory = "./按章节拆分的文本"
biaozhu_json_directory="./获取标注"
out_dir="./为拆分后的文本添加标注"
# List to hold paths of .docx files
docx_files = []

# Walk through the directory
for root, dirs, files in os.walk(wenben_json_directory):
    for file in files:
        if file.endswith(".json") and not file.startswith("~$"):
            # Add full path of each .docx file to the list

            wenben_file=os.path.join(wenben_json_directory, file)
            biaozhu_file = os.path.join(biaozhu_json_directory, file)
            output_file = os.path.join(out_dir, file)

            with open(wenben_file, 'r', encoding='utf-8') as json_file:
                data = json.load(json_file)

            with open(biaozhu_file, 'r', encoding='utf-8') as json_file:
                pizhu_data = json.load(json_file)

            for item in data:
                content_list=item['content']
                for content in content_list:
                    text=content['text']
                    annotations=content['annotations']
                    for pizhu_item in pizhu_data:
                        pizhu_txt=pizhu_item['文本段落']
                        if pizhu_txt.strip() == text.strip():
                            annotations.append([pizhu_item['参数类型'],pizhu_item['参数值'],pizhu_item['起始点'],pizhu_item['终止点']])

            print(output_file)
            print(len(data))
            with open(output_file, 'w', encoding='utf-8') as json_file:
                json.dump(data,json_file,indent=4,ensure_ascii=False)


