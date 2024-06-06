import requests
import fake_useragent
from bs4 import BeautifulSoup, SoupStrainer

def get_result(name : str, surname : str, document: int, getuser : bool):
    user = fake_useragent.UserAgent().random
    if getuser == True:
        return user
    else:
        url = 'https://result.rcoi25.ru/'
        headers = {
            'User-Agent': user,
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        session = requests.Session()
        r = session.get(url, headers=headers)
        token = BeautifulSoup(r.content, 'html.parser').findAll('input')[-1]['value']

        datas = {
            "form[name]": name,
            "form[surname]": surname,
            "form[document]": document,

            "form[_token]": token
        }

        r = session.post(url, headers=headers, data=datas)
        soup = BeautifulSoup(r.content, 'html.parser')
        g = list(soup.findAll('tr'))
        res = []
        for i in range(len(g)):
            res.append(str(g[i]).replace('<th>', '').replace('</th>', '').replace('<td>', '').
                       replace('</td>', '').replace('<tr class="table-success">', '').replace('<tr>', '').
                       replace('</tr>', '').replace(
                '[<tr><th>Дата</th><th>Предмет</th><th>Место проведения</th><th>Тестовый балл</th><th>Статус результата</th><th>Подробности</th>',
                '').
                       replace('<tr class="table-warning">', ''))
        return ', '.join(map(str, res[1:len(res)])).replace(',', '')
def result(name : str, surname : str, document: int):
    soup = BeautifulSoup(get_result(name, surname, document), 'html.parser')
    g = list(soup.findAll('tr'))
    res = []
    for i in range(len(g)):
        res.append(str(g[i]).replace('<th>', '').replace('</th>', '').replace('<td>', '').
                   replace('</td>', '').replace('<tr class="table-success">', '').replace('<tr>', '').
                   replace('</tr>', '').replace('[<tr><th>Дата</th><th>Предмет</th><th>Место проведения</th><th>Тестовый балл</th><th>Статус результата</th><th>Подробности</th>', '').
                   replace('<tr class="table-warning">', ''))
    return ', '.join(map(str, res[1:len(res)])).replace(',', '')


