base_url = 'http://data.people.com.cn.proxy.library.georgetown.edu/rmrb/s?qs='

# 两个词的情况
qs_2 = {
    "cds": [{"fld": "dataTime.start", "cdr": "AND", "hlt": "false", "vlr": "AND", "qtp": "DEF", "val": "1993-01-01"},
            {"fld": "dataTime.end", "cdr": "AND", "hlt": "false", "vlr": "AND", "qtp": "DEF", "val": "2020-06-15"},
            {"cdr": "AND", "cds": [{"fld": "title", "cdr": "OR", "hlt": "true", "vlr": "OR", "val": "克林顿"},
                                   {"fld": "subTitle", "cdr": "OR", "hlt": "true", "vlr": "OR", "val": "克林顿"},
                                   {"fld": "introTitle", "cdr": "OR", "hlt": "true", "vlr": "OR", "val": "克林顿"},
                                   {"fld": "contentText", "cdr": "OR", "hlt": "true", "vlr": "OR", "val": "克林顿"}]},
            {"cdr": "AND", "cds": [{"fld": "title", "cdr": "OR", "hlt": "true", "vlr": "OR", "val": "枪支"},
                                   {"fld": "subTitle", "cdr": "OR", "hlt": "true", "vlr": "OR", "val": "枪支"},
                                   {"fld": "introTitle", "cdr": "OR", "hlt": "true", "vlr": "OR", "val": "枪支"},
                                   {"fld": "contentText", "cdr": "OR", "hlt": "true", "vlr": "OR", "val": "枪支"}]}],
    "obs": [{"fld": "dataTime", "drt": "ASC"}]}
# 三个词的查询串
qs_3 = {
    "cds": [{"fld": "dataTime.start", "cdr": "AND", "hlt": "false", "vlr": "AND", "qtp": "DEF", "val": "1993-01-01"},
            {"fld": "dataTime.end", "cdr": "AND", "hlt": "false", "vlr": "AND", "qtp": "DEF", "val": "2020-06-15"},
            {"cdr": "AND", "cds": [{"fld": "title", "cdr": "OR", "hlt": "true", "vlr": "OR", "val": "克林顿"},
                                   {"fld": "subTitle", "cdr": "OR", "hlt": "true", "vlr": "OR", "val": "克林顿"},
                                   {"fld": "introTitle", "cdr": "OR", "hlt": "true", "vlr": "OR", "val": "克林顿"},
                                   {"fld": "contentText", "cdr": "OR", "hlt": "true", "vlr": "OR", "val": "克林顿"}]},
            {"cdr": "AND", "cds": [{"fld": "title", "cdr": "OR", "hlt": "true", "vlr": "OR", "val": "枪支"},
                                   {"fld": "subTitle", "cdr": "OR", "hlt": "true", "vlr": "OR", "val": "枪支"},
                                   {"fld": "introTitle", "cdr": "OR", "hlt": "true", "vlr": "OR", "val": "枪支"},
                                   {"fld": "contentText", "cdr": "OR", "hlt": "true", "vlr": "OR", "val": "枪支"}]},
            {"cdr": "AND", "cds": [{"fld": "title", "cdr": "OR", "hlt": "true", "vlr": "OR", "val": "暴力"},
                                   {"fld": "subTitle", "cdr": "OR", "hlt": "true", "vlr": "OR", "val": "暴力"},
                                   {"fld": "introTitle", "cdr": "OR", "hlt": "true", "vlr": "OR", "val": "暴力"},
                                   {"fld": "contentText", "cdr": "OR", "hlt": "true", "vlr": "OR", "val": "暴力"}]}],
    "obs": [{"fld": "dataTime", "drt": "ASC"}]}

base_url_tail = '&tr=A&ss=1&pageNo=1&pageSize=20'
