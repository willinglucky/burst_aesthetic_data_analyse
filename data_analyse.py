import base64
import numpy
import os

import json
import pandas as pd

Config = '/label_config'
Result = '/label_result'
Pair_Order_Key = 'pair_order'


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


def picked_dic(info_dict):
    pic_dic = {}
    for key, val in info_dict.items():
        if Pair_Order_Key not in info_dict[key]:
            continue
        pic_dic[key] = []
        tmp_dic = {}
        for pair_list in info_dict[key][Pair_Order_Key]:
            if pair_list[0] in tmp_dic.keys():
                tmp_dic[pair_list[0]] += 1
            else:
                tmp_dic[pair_list[0]] = 0

            if pair_list[1] in tmp_dic.keys():
                tmp_dic[pair_list[1]] += 1
            else:
                tmp_dic[pair_list[1]] = 0
        if len(info_dict[key][Pair_Order_Key]) == 17:
            flag = 2
        elif len(info_dict[key][Pair_Order_Key]) == 24:
            flag = 3
        else:
            flag = 4
        for sub_key, sub_val in tmp_dic.items():
            if sub_val > flag:
                pic_dic[key].append(sub_key)
    # print(pic_dic)
    for key, val in pic_dic.items():
        if len(val) > 4 or len(val) < 2:
            print("error")
            break
    return pic_dic


def topk_consistency(info_dict_1, info_dict_2):
    pic_dic_1 = picked_dic(info_dict_1)
    pic_dic_2 = picked_dic(info_dict_2)
    consistency_dic = {}
    for key, val in pic_dic_1.items():
        count = 0
        if key in pic_dic_2.keys():
            for elem in val:
                if elem in pic_dic_2[key]:
                    count += 1
        else:
            continue
        consistency_dic[key] = []
        consistency_dic[key].append((2 * count) / (len(val) + len(pic_dic_2[key])))

    sum = 0.0
    for key, val in consistency_dic.items():
        sum += val[0]
    if len(consistency_dic) != 0:
        tmp = sum / len(consistency_dic)
    else:
        tmp = 0
    consistency_dic['mean'] = []
    consistency_dic['mean'].append(tmp)

    df = pd.DataFrame(data=consistency_dic)
    return df


def person_consistency(info_dict):
    pic_dic = picked_dic(info_dict)
    consistency_dic = {}
    for key, val in pic_dic.items():
        count = 0
        if key.find('repeat') != -1:
            tmp_key = key.replace('-repeat', '')
            for elem in val:
                if elem in pic_dic[tmp_key]:
                    count += 1
        else:
            continue
        consistency_dic[key] = []
        consistency_dic[key].append((2 * count) / (len(val) + len(pic_dic[tmp_key])))

    for key_info, val_info in info_dict.items():
        count = 0
        if key_info.find('repeat') == -1:
            continue
        tmp_key = key_info.replace('-repeat', '')
        if tmp_key not in info_dict.keys():
            continue
        else:
            if Pair_Order_Key not in info_dict[key_info]:
                continue

            pair_num = 0
            pair_score = 0
            for pair_wise in val_info[Pair_Order_Key]:
                flag = 0
                converse_pair_wise = [0, 0]
                converse_pair_wise[0] = pair_wise[1]
                converse_pair_wise[1] = pair_wise[0]
                if pair_wise in info_dict[tmp_key][Pair_Order_Key]:
                    flag = 0
                    index_repeat = val_info[Pair_Order_Key].index(pair_wise)
                    index_original = info_dict[tmp_key][Pair_Order_Key].index(pair_wise)
                elif converse_pair_wise in info_dict[tmp_key][Pair_Order_Key]:
                    flag = 1
                    index_repeat = val_info[Pair_Order_Key].index(pair_wise)
                    index_original = info_dict[tmp_key][Pair_Order_Key].index(converse_pair_wise)
                else:
                    continue

                score_repeat = []
                score_original = []

                if str(index_repeat) not in val_info.keys():
                    continue
                if str(index_original) not in info_dict[tmp_key].keys():
                    continue

                if flag == 0:
                    for elem in val_info[str(index_repeat)]:
                        if elem == 'A':
                            score_repeat.append(1)
                        elif elem == '0':
                            score_repeat.append(0)
                        elif elem == 'B':
                            score_repeat.append(-1)
                    for elem in info_dict[tmp_key][str(index_original)]:
                        if elem == 'A':
                            score_original.append(1)
                        elif elem == '0':
                            score_original.append(0)
                        elif elem == 'B':
                            score_original.append(-1)
                elif flag == 1:
                    for elem in val_info[str(index_repeat)]:
                        if elem == 'A':
                            score_repeat.append(1)
                        elif elem == '0':
                            score_repeat.append(0)
                        elif elem == 'B':
                            score_repeat.append(-1)
                    for elem in info_dict[tmp_key][str(index_original)]:
                        if elem == 'A':
                            score_original.append(-1)
                        elif elem == '0':
                            score_original.append(0)
                        elif elem == 'B':
                            score_original.append(1)
                score_sum = 0.0
                for score_index in range(len(score_repeat)):
                    tmp = (score_repeat[score_index] - score_original[score_index])
                    if tmp < 0:
                        tmp = tmp * (-1)

                    score_sum += tmp
                score_sum = score_sum / (2 * len(score_repeat))
                pair_num += 1
                pair_score += score_sum
            if pair_num != 0:
                consistency_dic[key_info].append(pair_score / pair_num)
            else:
                consistency_dic[key_info].append(0)
            consistency_dic[key_info].append(pair_num)
            consistency_dic[key_info].append(pair_score)

    sum = [0.0,0.0,0.0,0.0]
    tmp = [0.0, 0.0, 0.0, 0.0]
    for key, val in consistency_dic.items():
        sum[0] += val[0]
        if len(val) > 1:
            print(val)
            sum[1] += val[1]
            sum[2] += val[2]
            sum[3] += val[3]
    if len(consistency_dic) != 0:
        tmp[0] = sum[0] / len(consistency_dic)
        tmp[1] = sum[1] / len(consistency_dic)
        tmp[2] = sum[2] / len(consistency_dic)
        tmp[3] = sum[3] / len(consistency_dic)
    consistency_dic['mean'] = []
    consistency_dic['mean'].append(tmp[0])
    consistency_dic['mean'].append(tmp[1])
    consistency_dic['mean'].append(tmp[2])
    consistency_dic['mean'].append(tmp[3])

    df = pd.DataFrame(data=consistency_dic)
    return df


def pair_consistency(info_dic_1, info_dic_2):
    consistency_dic = {}
    for key_out, val_out in info_dic_1.items():
        count = 0
        if Pair_Order_Key not in val_out.keys():
            continue
        if key_out in info_dic_2.keys():
            consistency_dic[key_out] = {}
            if Pair_Order_Key not in info_dic_2[key_out]:
                continue

            for pair_wise in val_out[Pair_Order_Key]:
                flag = 0
                converse_pair_wise = [0, 0]
                converse_pair_wise[0] = pair_wise[1]
                converse_pair_wise[1] = pair_wise[0]
                if pair_wise in info_dic_2[key_out][Pair_Order_Key]:
                    flag = 0
                    index_out = val_out[Pair_Order_Key].index(pair_wise)
                    index_in = info_dic_2[key_out][Pair_Order_Key].index(pair_wise)
                elif converse_pair_wise in info_dic_2[key_out][Pair_Order_Key]:
                    flag = 1
                    index_out = val_out[Pair_Order_Key].index(pair_wise)
                    index_in = info_dic_2[key_out][Pair_Order_Key].index(converse_pair_wise)
                else:
                    continue

                score_out = []
                score_in = []

                if str(index_out) not in val_out.keys():
                    continue
                if str(index_in) not in info_dic_2[key_out].keys():
                    continue

                if flag == 0:
                    for elem in val_out[str(index_out)]:
                        if elem == 'A':
                            score_out.append(1)
                        elif elem == '0':
                            score_out.append(0)
                        elif elem == 'B':
                            score_out.append(-1)
                    for elem in info_dic_2[key_out][str(index_in)]:
                        if elem == 'A':
                            score_in.append(1)
                        elif elem == '0':
                            score_in.append(0)
                        elif elem == 'B':
                            score_in.append(-1)
                elif flag == 1:
                    for elem in val_out[str(index_out)]:
                        if elem == 'A':
                            score_out.append(1)
                        elif elem == '0':
                            score_out.append(0)
                        elif elem == 'B':
                            score_out.append(-1)
                    for elem in info_dic_2[key_out][str(index_in)]:
                        if elem == 'A':
                            score_in.append(-1)
                        elif elem == '0':
                            score_in.append(0)
                        elif elem == 'B':
                            score_in.append(1)
                score_sum = 0.0
                for score_index in range(len(score_out)):
                    tmp = (score_out[score_index] - score_in[score_index])
                    if tmp < 0:
                        tmp = tmp * (-1)

                    score_sum += tmp
                score_sum = score_sum / (2 * len(score_out))
                consistency_dic[key_out][pair_wise[0] + '-' + pair_wise[1]] = []
                consistency_dic[key_out][pair_wise[0] + '-' + pair_wise[1]].append(score_sum)
        else:
            continue

    sum = 0.0
    count = 0

    for key_video, val_pair_list in consistency_dic.items():
        for key_pair, val_pair in val_pair_list.items():
            sum += val_pair[0]
            count += 1
    if count != 0:
        tmp = sum / count
    else:
        tmp = 0
    consistency_dic['mean'] = []
    consistency_dic['mean'].append(tmp)

    return consistency_dic


def dataframe(info_dict):
    new_dic = {'整图美感评价': [], '姿态美感': [], '面部美感': [], '全图清晰度': [], '全图光照': [], '面部清晰度': [], '面部光照': []}
    for key in info_dict.keys():
        for sub_key, sub_val in info_dict[key].items():
            if sub_key == Pair_Order_Key:
                continue
            for index_num in range(len(sub_val)):
                if sub_val[index_num] == 'A':
                    sub_val[index_num] = 1
                elif sub_val[index_num] == '0':
                    sub_val[index_num] = 0
                else:
                    sub_val[index_num] = -1

            new_dic['整图美感评价'].append(sub_val[0])
            new_dic['姿态美感'].append(sub_val[1])
            new_dic['面部美感'].append(sub_val[2])
            new_dic['全图清晰度'].append(sub_val[3])
            new_dic['全图光照'].append(sub_val[4])
            new_dic['面部清晰度'].append(sub_val[5])
            new_dic['面部光照'].append(sub_val[6])
    df = pd.DataFrame(data=new_dic)
    return df


def main():
    # file_list = ['C:\\Users\\19938\\PycharmProjects\\label_GUI\\标注结果\\数据标注前20组20191203\\张亮20',
    #              'C:\\Users\\19938\\PycharmProjects\\label_GUI\\标注结果\\数据标注前20组20191203\\许松20',
    #              'C:\\Users\\19938\\PycharmProjects\\label_GUI\\标注结果\\数据标注前20组20191203\\肖力玮20',
    #              'C:\\Users\\19938\\PycharmProjects\\label_GUI\\标注结果\\数据标注前20组20191203\\王剑峰20',
    #              'C:\\Users\\19938\\PycharmProjects\\label_GUI\\标注结果\\数据标注前20组20191203\\柯飞龙20']
    file_list = [r'C:\Users\19938\Documents\intership\burst_dataset\数据标注已完成100组\柯飞龙100',
                 r'C:\Users\19938\Documents\intership\burst_dataset\数据标注已完成100组\王剑峰100',
                 r'C:\Users\19938\Documents\intership\burst_dataset\数据标注已完成100组\肖力玮100',
                 r'C:\Users\19938\Documents\intership\burst_dataset\数据标注已完成100组\许松100',
                 r'C:\Users\19938\Documents\intership\burst_dataset\数据标注已完成100组\张亮100']
    df_list = []
    # argv = 'consistency'
    argv = 'person_consistency'
    if argv == 'corr':
        for file_path in file_list:
            ret, ret_str, ret_list = get_info(file_path)
            # print(ret_str)
            # print(ret_list[0])
            #
            # print(ret_list[1])
            # print(ret_list[2])
            # print(ret_list[3])

            # print(ret_list[0].index(ret_list[2]))
            df = dataframe(ret_list[1])
            df_list.append(df)
            save_path = file_path[file_path.rfind('\\') + 1:] + '.csv'
            print(save_path)
            df.corr().to_csv(save_path, encoding='utf_8_sig')
        hol_df = pd.concat(df_list)
        hol_df.corr().to_csv('hol_corr.csv', encoding='utf_8_sig')
    elif argv == 'topk_consistency':
        for index_out in range(len(file_list) - 1):
            ret_out, ret_str_out, ret_list_out = get_info(file_list[index_out])
            for index_in in range(index_out + 1, len(file_list)):
                ret_in, ret_str_in, ret_list_in = get_info(file_list[index_in])
                df = topk_consistency(ret_list_out[1], ret_list_in[1])
                save_path = file_list[index_out][file_list[index_out].rfind('\\') + 1:] + '-' + file_list[index_in][
                                                                                                file_list[
                                                                                                    index_in].rfind(
                                                                                                    '\\') + 1:] + '.csv'
                df_list.append(df)
                # df.to_csv(save_path, encoding='utf_8_sig', index=0)
                print(save_path, df.std(axis=1))
        hol_df = pd.concat(df_list)
        print('hol:', hol_df.std(axis=1))
        hol_df.to_csv('topk_hol_corr.csv', encoding='utf_8_sig')
    elif argv == 'pair_consistency':
        count = 0
        sum = 0.0
        for index_out in range(len(file_list) - 1):
            ret_out, ret_str_out, ret_list_out = get_info(file_list[index_out])
            s_list = []
            for index_in in range(index_out + 1, len(file_list)):
                ret_in, ret_str_in, ret_list_in = get_info(file_list[index_in])
                pair_consistency_dic = pair_consistency(ret_list_out[1], ret_list_in[1])
                save_path = file_list[index_out][file_list[index_out].rfind('\\') + 1:] + '-' + file_list[index_in][
                                                                                                file_list[
                                                                                                    index_in].rfind(
                                                                                                    '\\') + 1:]
                for key, main_dict in pair_consistency_dic.items():
                    if key == 'mean':
                        continue
                    for sub_key, sub_list in main_dict.items():
                        s_list.append(sub_list[0])

                print(save_path, ":", numpy.std(s_list, ddof=1), pair_consistency_dic['mean'])

                sum += pair_consistency_dic['mean'][0]
                count += 1
        print(sum / count)
    elif argv == 'person_consistency':
        for index in range(len(file_list)):
            ret, ret_str, ret_list = get_info(file_list[index])
            df = person_consistency(ret_list[1])
            save_path = file_list[index][file_list[index].rfind('\\') + 1:] + '-persion_consistency.csv'
            print(save_path)
            df_list.append(df)
            df.to_csv(save_path, encoding='utf_8_sig', index=0)
    else:
        num = 0
        for file_path in file_list:
            ret, ret_str, ret_list = get_info(file_path)
            for key, val in ret_list[1].items():
                if Pair_Order_Key in val.keys():
                    num += len(val[Pair_Order_Key])
        print(num)
        print(num // 5)


if __name__ == '__main__':
    main()
