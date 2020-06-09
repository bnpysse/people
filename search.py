import urllib.parse

qs = {"cIds": "23,", "cds": [{"cdr": "AND", "cds": [
    {"fld": "dataTime.start", "cdr": "AND", "hlt": "false", "vlr": "OR", "val": "2004-01-01"},
    {"fld": "dataTime.end", "cdr": "AND", "hlt": "false", "vlr": "OR", "val": "2020-05-30"}]}, {"cdr": "AND", "cds": [
    {"cdr": "AND", "cds": [{"fld": "title", "cdr": "OR", "hlt": "true", "vlr": "OR", "val": "克林顿"},
                           {"fld": "subTitle", "cdr": "OR", "hlt": "true", "vlr": "OR", "val": "克林顿"},
                           {"fld": "introTitle", "cdr": "OR", "hlt": "true", "vlr": "OR", "val": "克林顿"},
                           {"fld": "contentText", "cdr": "OR", "hlt": "true", "vlr": "OR", "val": "克林顿"},
                           {"fld": "title", "cdr": "OR", "hlt": "true", "vlr": "OR", "val": "奥巴马"},
                           {"fld": "subTitle", "cdr": "OR", "hlt": "true", "vlr": "OR", "val": "奥巴马"},
                           {"fld": "introTitle", "cdr": "OR", "hlt": "true", "vlr": "OR", "val": "奥巴马"},
                           {"fld": "contentText", "cdr": "OR", "hlt": "true", "vlr": "OR", "val": "奥巴马"}]},
    {"cdr": "AND", "cds": [{"cdr": "AND",
                            "cds": [{"fld": "title", "cdr": "OR", "hlt": "true", "vlr": "AND", "val": "蓬佩奥"},
                                    {"fld": "subTitle", "cdr": "OR", "hlt": "true", "vlr": "AND", "val": "蓬佩奥"},
                                    {"fld": "introTitle", "cdr": "OR", "hlt": "true", "vlr": "AND", "val": "蓬佩奥"},
                                    {"fld": "contentText", "cdr": "OR", "hlt": "true", "vlr": "AND", "val": "蓬佩奥"}]}]},
    {"cdr": "AND", "cds": [{"fld": "title", "cdr": "NOT", "hlt": "true", "vlr": "AND", "val": "希拉里"},
                           {"fld": "subTitle", "cdr": "NOT", "hlt": "false", "vlr": "AND", "val": "希拉里"},
                           {"fld": "introTitle", "cdr": "NOT", "hlt": "false", "vlr": "AND", "val": "希拉里"},
                           {"fld": "contentText", "cdr": "NOT", "hlt": "true", "vlr": "AND", "val": "希拉里"}]}]}],
      "obs": [{"fld": "dataTime", "drt": "DESC"}, {"fld": "orderId", "drt": "DESC"}, {"fld": "seqid", "drt": "DESC"}]}

print(urllib.parse.urlencode(qs))
print(str(qs).replace('\'', '\"'))
print(urllib.parse.quote(str(qs).replace('\'', '\"')))

print('Title is {}'.format(qs['cds'][0]['cds'][0]['fld']))
print('条件 is {}'.format(qs['cds'][0]['cds'][0]['cdr']))
print('hlt is {}'.format(qs['cds'][0]['cds'][0]['hlt']))
print('val is {}'.format(qs['cds'][0]['cds'][0]['val']))
