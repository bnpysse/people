import urllib.parse
import pprint
import itertools

# region Word list, and combine of word list AB,AC,ABC
A = ["克林顿", "布什", "奥巴马", "特朗普", "蓬佩奥", "世界警察", "西方", "强盗", "势力", "政客"]
B = ['枪支', "暴力", "人权", "单边主义", "保护主义", "帝国主义", "贸易", "新冷战", "倾销", "补贴", "关税", "种族"]
C = ['强权', '霸权', '干涉', '谴责', '打压', '敦促', '勾连', '政治操弄', '虚伪', '双重标准', '嘴脸', '愤慨', '拙劣', '伪善', '抹黑', '歪曲', '别有用心', '污名化',
     '丑化', '捕风捉影', '捏造', '图谋', '霸凌', '践踏', '敌对', '仇视', '指责']
# endregion

base_url = 'http://data.people.com.cn.proxy.library.georgetown.edu/sc/ss2018?qs='

# region 从 chrome 中获取的查询串
qs = {"cIds": "23,", "cds": [
    {"cdr": "AND", "cds": [
        {"fld": "dataTime.start", "cdr": "AND", "hlt": "false", "vlr": "OR", "val": "1993-01-01"},
        {"fld": "dataTime.end", "cdr": "AND", "hlt": "false", "vlr": "OR", "val": "2020-06-10"}]},
    {"cdr": "AND", "cds": [
        {"cdr": "AND", "cds": [
            {"cdr": "AND",
             "cds": [{"fld": "title", "cdr": "OR", "hlt": "true", "vlr": "AND", "val": "克林顿"},
                     {"fld": "subTitle", "cdr": "OR", "hlt": "true", "vlr": "AND", "val": "克林顿"},
                     {"fld": "introTitle", "cdr": "OR", "hlt": "true", "vlr": "AND", "val": "克林顿"},
                     {"fld": "contentText", "cdr": "OR", "hlt": "true", "vlr": "AND", "val": "克林顿"}]},
            {"cdr": "AND",
             "cds": [{"fld": "title", "cdr": "OR", "hlt": "true", "vlr": "AND", "val": "暴力"},
                     {"fld": "subTitle", "cdr": "OR", "hlt": "true", "vlr": "AND", "val": "暴力"},
                     {"fld": "introTitle", "cdr": "OR", "hlt": "true", "vlr": "AND", "val": "暴力"},
                     {"fld": "contentText", "cdr": "OR", "hlt": "true", "vlr": "AND", "val": "暴力"}]}]}]}],
      "obs": [{"fld": "dataTime", "drt": "DESC"}, {"fld": "orderId", "drt": "DESC"}, {"fld": "seqid", "drt": "DESC"}]}
# endregion

# region 测试查询字典的关键字位置
print(urllib.parse.urlencode(qs))
print(str(qs).replace('\'', '\"'))
print(urllib.parse.quote(str(qs).replace('\'', '\"')))
# 第一个关键字
print('{}'.format(qs['cds'][1]['cds'][0]['cds'][0]['cds'][0]['val']))  # title
print('{}'.format(qs['cds'][1]['cds'][0]['cds'][0]['cds'][1]['val']))  # subTitle
print('{}'.format(qs['cds'][1]['cds'][0]['cds'][0]['cds'][2]['val']))  # introTitle
print('{}'.format(qs['cds'][1]['cds'][0]['cds'][0]['cds'][3]['val']))  # contentText
# 第二个关键字
print('{}'.format(qs['cds'][1]['cds'][0]['cds'][1]['cds'][0]['val']))
print('{}'.format(qs['cds'][1]['cds'][0]['cds'][1]['cds'][1]['val']))
print('{}'.format(qs['cds'][1]['cds'][0]['cds'][1]['cds'][2]['val']))
print('{}'.format(qs['cds'][1]['cds'][0]['cds'][1]['cds'][3]['val']))
# endregion


def building_qs(word_list1, world_list2):
    combination_list = list(itertools.product(word_list1, world_list2))
    for word in combination_list:
        # 之所以四次循环，是把title,subTitle,introTitle,contentText四个字段都赋值
        for i in range(4):
            qs['cds'][1]['cds'][0]['cds'][0]['cds'][i]['val'] = word[0]
            qs['cds'][1]['cds'][0]['cds'][1]['cds'][i]['val'] = word[1]
        yield word[0], word[1], base_url + urllib.parse.quote(str(qs).replace('\'', '\"'))


count = 0
gen = building_qs(A, B)
while True:
    try:
        key1, key2, url = next(gen)
        print(key1, ' ', key2, ' ', url)
        count += 1
    except StopIteration as e:
        print('Generator is done:', e.value)
        break

print('The count is {}'.format(count))
