# coding=utf-8

import os
import sys
import requests
from bs4 import BeautifulSoup
from functools import partial

import crypto


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    '(KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36 Edg/93.0.961.47',
    'Accept':
    'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
    'q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,de;q=0.7,pt;q=0.6',
    'Connection': 'keep-alive',
}

HTTP_TIMEOUT = 15  # HTTP连接超时阈值

REPORT_NAME_MAP = {
    'Name': 'txtBGMC', 'Semester': 'ddlXQ',
    'Time': 'txtKssj', 'Location': 'txtBGDD',
    'Speaker': 'txtBGR'
}


def convert_to_form(names):
    return list(REPORT_NAME_MAP[name] for name in names)


class AutoReporter(object):
    def __init__(self, username, password,
                 http_timeout=HTTP_TIMEOUT):
        self._session = requests.Session()
        # initialize customized `get` and `post` methods.
        self._get = partial(self._session.get,
                            headers=HEADERS,
                            timeout=http_timeout)
        self._post = partial(self._session.post,
                             headers=HEADERS,
                             timeout=http_timeout)
        self.username = username
        self.password = password

    def _login(self):
        login_url = 'https://ids.shanghaitech.edu.cn/authserver/login'
        params = {
            "service":
            'https://egate.shanghaitech.edu.cn:443/login?'
            'service=https://egate.shanghaitech.edu.cn/new/index.html'
        }

        # prepare
        response = self._get(login_url, params=params)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.find_all('input', attrs={'type': 'hidden'})

        hidden_data = dict()
        salts = None
        for i in items:
            if i.get('name') is not None:
                hidden_data[i.get('name')] = i.get('value')
            else:
                assert i.get('id') == 'pwdDefaultEncryptSalt'
                salts = i.get('value')

        assert salts != None
        cipher_password = crypto.encrypt(self.password, salts)
        auth_data = dict(username=self.username, password=cipher_password,
                         **hidden_data)

        # login
        response = self._post(login_url, params=params, data=auth_data)

        # make sure that the crawler has logged into the site successfully.
        index_url = 'https://egate.shanghaitech.edu.cn/new/index.html'
        response = self._get(index_url)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        if soup.find('article', attrs={'id': 'ampPersonalArticle'}) is not None:
            print('login succeeded!')
        else:
            print('login failed!!!')
            os._exit(1)

    def redirect(self):
        manage_url = 'http://grad.shanghaitech.edu.cn/'
        auth_url = 'http://ids.shanghaitech.edu.cn/authserver/login?' \
                   'service=http://grad.shanghaitech.edu.cn/sso/'
        show_url = 'https://grad.shanghaitech.edu.cn/GraduateCultivate/WitMis_FBLWManage.aspx'

        params = {
            'PC': 'AA7F0DCDDFB3894C',
            'PCID': '5725B7721D4680F3'
        }

        print('redirect...')
        self._get(manage_url)
        self._get(auth_url)
        response = self._get(show_url, params=params)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        if soup.find('div', attrs={'id': 'RadWindowManager1'}) is not None:
            print('redirected succeeded!')
        else:
            print('redirected failed!!!')
            os._exit(1)

    def submit_reports(self, reports):
        report_url = 'https://grad.shanghaitech.edu.cn/GraduateCultivate/WitMis_Fblw.aspx'

        params = {
            'Action': 'Add',
            'PC': 'AA7F0DCDDFB3894C',
            'PCID': '5725B7721D4680F3'
        }

        response = self._get(report_url, params=params)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.find_all('input', attrs={'type': 'hidden'})
        hidden_data = dict(
            map(lambda i: (i.get('name'), i.get('value')), items))

        for report in reports:
            auth_data = dict(butBC='保存', **hidden_data, **report)

            # submit
            response = self._post(report_url, params=params, data=auth_data,
                                  files={'f': None})
            if response.status_code != 200:
                print('submit failed!!!')
                os._exit(1)

        print('submit succeeded!')

    def run(self, reports):
        # login
        self._login()
        # redirect
        self.redirect()
        # submit
        self.submit_reports(reports)


def make_auto_reporter(cfg):
    return AutoReporter(cfg.username, cfg.password)


if __name__ == '__main__':
    import config as cfg
    auto_reporter = make_auto_reporter(cfg)

    # read excel
    import xlrd
    data = xlrd.open_workbook(sys.argv[1])
    table = data.sheets()[0]

    reports = []
    names = convert_to_form(table.row_values(0))
    for i in range(1, table.nrows):
        reports.append(dict(zip(names, table.row_values(i))))
    if len(reports) > cfg.threshold:
        reports = reports[:cfg.threshold]

    # run
    auto_reporter.run(reports)
