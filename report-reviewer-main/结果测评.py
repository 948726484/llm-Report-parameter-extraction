import json
import os
import csv

wenben_gir = "./为拆分后的文本添加标注"

# List to hold paths of .docx files
docx_files = []
chouqu_canshu_dict = {
    "项目名称": "项目-项目名称",
    "项目地点": "项目-项目地点（省市县）",
    "项目地址": "项目-项目地点（省市县）",
    "项目业主单位名称": "项目-项目业主单位名称",
    "规划装机容量": "项目-规划装机容量",
    "规划装机规模": "项目-规划装机容量",
    "场区跨度": "项目-场区跨度",
    "场区跨度（东西）":"项目-场区跨度",
    "场区跨度（南北）": "项目-场区跨度",
    "场区跨度（南北向）": "项目-场区跨度",
    "场区跨度（东西向）": "项目-场区跨度",
    "海拔高度": "项目-海拔高度",
    "风机型号": "项目-风机型号",
    "单机容量": "项目-单机容量",
    "风轮直径": "项目-叶轮直径",
    "轮毂高度": "项目-轮毂高度",
    "风电机组数量": "项目-风电机组台数",
    "风电机组台数":"项目-风电机组台数",
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
    "长期贷款利率-待确认": "财务-长期贷款利率",
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

param_metrics_all = {}
for canshu in chouqu_canshu_dict.values():
    param_metrics_all[canshu] = {'correct': 0, 'total_annotations': 0, 'total_predictions': 0}

def remove_duplicates(lst_of_lsts):
    seen = set()
    unique_lst_of_lsts = []
    for sublist in lst_of_lsts:
        sublist_tuple = tuple(sublist)
        if sublist_tuple not in seen:
            seen.add(sublist_tuple)
            unique_lst_of_lsts.append(sublist)
    return unique_lst_of_lsts

# Open the CSV file for writing
with open('results.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['文件路径', '标记总数', '预测总数', '预测正确数', '召回率', '准确率', '参数名', '标记总数', '预测总数', '预测正确数', '参数召回率', '参数准确率']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    # Walk through the directory
    for root, dirs, files in os.walk(wenben_gir):
        for file in files:
            if file.endswith(".json") and not file.startswith("~$"):
                wenben_path = os.path.join(root, file)
                biaoji_total = 0
                yuce_total = 0
                yuce_correct = 0
                yiyuce_list = []

                with open(wenben_path, 'r', encoding='utf-8') as json_file:
                    wenben_data = json.load(json_file)

                param_metrics = {}
                for canshu in chouqu_canshu_dict.values():
                    param_metrics[canshu] = {'correct': 0, 'total_annotations': 0, 'total_predictions': 0}

                for wenben_item in wenben_data[:]:
                    content_list = wenben_item['content']
                    annotations_list = []
                    shuchushiti_list = []
                    for content in content_list:
                        annotations = content['annotations']
                        for annotation in annotations:
                            annotations_list.append([annotation[0], annotation[1]])
                    if 'moxingshuchu' not in wenben_item:
                        continue
                    for shuchu_list in wenben_item['moxingshuchu']:
                        shuchu_key = shuchu_list[0]
                        shuchu_value_list = shuchu_list[1]
                        for value in shuchu_value_list:
                            shuchushiti_list.append([shuchu_key, value])

                    annotations_list = remove_duplicates(annotations_list)
                    shuchushiti_list = remove_duplicates(shuchushiti_list)

                    biaoji_total += len(annotations_list)
                    yuce_total += len(shuchushiti_list)
                    for annotation_biaozhu in annotations_list:
                        biaozhu_leixing, biaozhu_zhi = annotation_biaozhu
                        biaozhu_leixing = chouqu_canshu_dict[biaozhu_leixing]
                        param_metrics[biaozhu_leixing]['total_annotations'] += 1
                        param_metrics_all[biaozhu_leixing]['total_annotations'] += 1

                    for yuce in shuchushiti_list:
                        leixing, zhi = yuce
                        param_metrics[leixing]['total_predictions'] += 1
                        param_metrics_all[leixing]['total_predictions'] += 1
                        for annotation_biaozhu in annotations_list:
                            biaozhu_leixing, biaozhu_zhi = annotation_biaozhu
                            biaozhu_leixing = chouqu_canshu_dict[biaozhu_leixing]
                            zhi = str(zhi)
                            if biaozhu_zhi in zhi and biaozhu_leixing == leixing:
                                param_metrics[leixing]['correct'] += 1
                                param_metrics_all[leixing]['correct'] += 1
                                yuce_correct += 1
                                yiyuce_list.append([biaozhu_zhi, zhi])
                                break
                            if zhi in biaozhu_zhi and biaozhu_leixing == leixing:
                                param_metrics[leixing]['correct'] += 1
                                param_metrics_all[leixing]['correct'] += 1
                                yuce_correct += 1
                                yiyuce_list.append([biaozhu_zhi, zhi])
                                break
                if biaoji_total == 0:
                    continue
                if yuce_total == 0:
                    continue
                recall = yuce_correct / biaoji_total
                accuracy = yuce_correct / yuce_total

                print(wenben_path)
                print(f"标记总数：{biaoji_total}")
                print(f"预测总数：{yuce_total}")
                print(f"预测正确数：{yuce_correct}")
                print(f"召回率{recall}")
                print(f"准确率{accuracy}")

                # Write the overall metrics to the CSV file
                writer.writerow({
                    '文件路径': wenben_path,
                    '标记总数': biaoji_total,
                    '预测总数': yuce_total,
                    '预测正确数': yuce_correct,
                    '召回率': recall,
                    '准确率': accuracy
                })

                for param_name, param_zhi in param_metrics.items():
                    try:
                        if param_zhi['total_annotations'] == 0 and param_zhi['total_predictions'] == 0:
                            continue
                        if param_zhi['total_annotations'] != 0:
                            param_recall = param_zhi['correct'] / param_zhi['total_annotations']
                        else:
                            param_recall = ''
                        if param_zhi['total_predictions'] != 0:
                            param_accuracy = param_zhi['correct'] / param_zhi['total_predictions']
                        else:
                            param_accuracy = ''

                        # Write the parameter metrics to the CSV file
                        writer.writerow({
                            '文件路径': '',
                            '标记总数': '',
                            '预测总数': '',
                            '预测正确数': '',
                            '召回率': '',
                            '准确率': '',
                            '参数名': param_name,
                            '标记总数': param_zhi['total_annotations'],
                            '预测总数': param_zhi['total_predictions'],
                            '预测正确数': param_zhi['correct'],
                            '参数召回率': param_recall,
                            '参数准确率': param_accuracy
                        })

                    except:
                        continue

                print("-----------------------------")

    # Write the overall param_metrics_all results to the CSV file
    for param_name, param_zhi in param_metrics_all.items():
        try:
            if param_zhi['total_annotations'] == 0 and param_zhi['total_predictions'] == 0:
                continue
            if param_zhi['total_annotations'] != 0:
                param_recall = param_zhi['correct'] / param_zhi['total_annotations']
            else:
                param_recall = ''
            if param_zhi['total_predictions'] != 0:
                param_accuracy = param_zhi['correct'] / param_zhi['total_predictions']
            else:
                param_accuracy = ''

            # Write the parameter metrics to the CSV file
            writer.writerow({
                '文件路径': '总体',
                '标记总数': '',
                '预测总数': '',
                '预测正确数': '',
                '召回率': '',
                '准确率': '',
                '参数名': param_name,
                '标记总数': param_zhi['total_annotations'],
                '预测总数': param_zhi['total_predictions'],
                '预测正确数': param_zhi['correct'],
                '参数召回率': param_recall,
                '参数准确率': param_accuracy
            })

        except:
            continue