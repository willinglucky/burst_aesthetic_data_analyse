import base64
import numpy
import os

import json
import pandas as pd

Config = '/label_config'
Result = '/label_result'
Pair_Order_Key = 'pair_order'
Label_Result = './label.txt'
File_Head ='Select_Frame/'

def get_info(dir_path):
    ret_list = []

    ret = os.path.exists(dir_path + Config)
    if ret == False:
        print('config file lack')

    ret = os.path.exists(dir_path + Result)
    if ret == False:
        print('config file lack')

    order_list = []
    with open(dir_path + Config, "r", encoding='utf-8') as label_config_file:
        f_data_list = label_config_file.readlines()

        for a in f_data_list:
            order_list.append(a.strip())  # 去掉\n strip去掉头尾默认空格或换行符

    fsize = os.path.getsize(dir_path + Result)
    if fsize == 0:
        info_dic = {}
    else:
        with open(dir_path + Result, "r", encoding='utf-8') as label_config_file:
            tmp_str = label_config_file.read()
            de = base64.b64decode(tmp_str).decode("utf-8")
            info_dic = json.loads(de)

    front_key = ''
    key = ''
    for order_key in order_list:
        front_key = key
        key = order_key
        if order_key not in info_dic:
            if front_key == '':
                key = order_list[0]
                info_dic[key] = {}
                break;

            pair_wise_info_dic = info_dic[front_key]
            if len(pair_wise_info_dic[Pair_Order_Key]) != (len(pair_wise_info_dic) - 1):
                key = front_key
                break
            info_dic[key] = {}
            break
    pair_wise_info_dic = info_dic[key]

    ret_list.append(order_list)
    ret_list.append(info_dic)
    sub_key = -1
    if len(pair_wise_info_dic) == 0:
        ret_list.append(key)
        ret_list.append(sub_key)
    elif (len(pair_wise_info_dic) - 1) < len(pair_wise_info_dic[Pair_Order_Key]):
        ret_list.append(key)
        sub_key = len(pair_wise_info_dic) - 1
        ret_list.append(sub_key)

    return True, "Initialize successfully.", ret_list


def main():
    file_list = [r'C:\Users\19938\Documents\intership\burst_dataset\数据标注已完成100组\柯飞龙100',
                 r'C:\Users\19938\Documents\intership\burst_dataset\数据标注已完成100组\王剑峰100',
                 r'C:\Users\19938\Documents\intership\burst_dataset\数据标注已完成100组\肖力玮100',
                 r'C:\Users\19938\Documents\intership\burst_dataset\数据标注已完成100组\许松100',
                 r'C:\Users\19938\Documents\intership\burst_dataset\数据标注已完成100组\张亮100']
    info_list = []
    for file_path in file_list:
        ret, ret_str, ret_list = get_info(file_path)
        info_list.append(ret_list[1])

    for key, val in info_list[0].items():
        tmp_folder_list = []
        choiced_list = []
        for i in range(0, 5):
            if key in info_list[i]:
                tmp_folder_list.append(info_list[i][key])

        if key.find('-repeat') != -1:
            continue

        for i in range(0,len(tmp_folder_list)):
            for pair_wise in tmp_folder_list[i][Pair_Order_Key]:
                score = [0, 0, 0]
                converse_pair_wise = [0, 0]
                converse_pair_wise[0] = pair_wise[1]
                converse_pair_wise[1] = pair_wise[0]
                if pair_wise in choiced_list:
                    continue
                if converse_pair_wise in choiced_list:
                    continue

                choiced_list.append(pair_wise)

                index_tmp = tmp_folder_list[i][Pair_Order_Key].index(pair_wise)
                if tmp_folder_list[i][str(index_tmp)][1] == 'A':
                    score[0] += 1
                elif tmp_folder_list[i][str(index_tmp)][1] == '0':
                    score[1] += 1
                elif tmp_folder_list[i][str(index_tmp)][1] == 'B':
                    score[2] += 1

                for j in range(i + 1, len(tmp_folder_list)):
                    if pair_wise in tmp_folder_list[j][Pair_Order_Key]:
                        index_tmp = tmp_folder_list[j][Pair_Order_Key].index(pair_wise)
                        if tmp_folder_list[j][str(index_tmp)][1] == 'A':
                            score[0] += 1
                        elif tmp_folder_list[j][str(index_tmp)][1] == '0':
                            score[1] += 1
                        elif tmp_folder_list[j][str(index_tmp)][1] == 'B':
                            score[2] += 1
                    if converse_pair_wise in tmp_folder_list[j][Pair_Order_Key]:
                        index_tmp = tmp_folder_list[j][Pair_Order_Key].index(converse_pair_wise)
                        if tmp_folder_list[j][str(index_tmp)][1] == 'A':
                            score[2] += 1
                        elif tmp_folder_list[j][str(index_tmp)][1] == '0':
                            score[1] += 1
                        elif tmp_folder_list[j][str(index_tmp)][1] == 'B':
                            score[0] += 1
                s_max = max(score)
                if (s_max == score[0] and s_max == score[1]) or (s_max == score[0] and s_max == score[2]) or (
                        s_max == score[1] and s_max == score[2]):
                    continue

                label = 0
                if s_max == score[0]:
                    label = 1
                elif s_max == score[1]:
                    label = 0
                elif s_max == score[2]:
                    label = -1
                with open(Label_Result, "a+", encoding='utf-8') as label_result_file:
                    # print(score)
                    label_result_file.write(
                        "{} {} {}".format(File_Head+(key) + '/' + pair_wise[0], File_Head+(key) + '/' + pair_wise[1], str(label)))
                    label_result_file.write('\n')


if __name__ == '__main__':
    main()
