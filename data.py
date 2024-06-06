import pandas as pd


def build():
    empty = {}
    df_orders = pd.read_excel('Sem.xlsx', sheet_name='Лист1', usecols=[1, 2, 3, 4]).to_dict('list')
    for i in range(len(df_orders['id'])):
        empty[df_orders['id'][i]] = {'name': df_orders['name'][i],
                                     'surname': df_orders['surname'][i],
                                     'document': df_orders['document'][i]}
    return empty

def create(id, name, surname, document):
    df_orders = pd.read_excel('Sem.xlsx', sheet_name='Лист1', usecols=[1, 2, 3, 4]).to_dict('list')
    if id in df_orders['id']:
        print('пошёл ты')
    else:
        df_orders['id'].append(id)
        df_orders['name'].append(name)
        df_orders['surname'].append(surname)
        df_orders['document'].append(document)
        print(df_orders)
        pd.DataFrame(df_orders).to_excel('Sem.xlsx', sheet_name='Лист1')