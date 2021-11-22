import numpy as np
import pandas as pd
import sqlite3 as sql

#######function Pandas##################

def getTable(urlFiles, all = False):
    formatFile = urlFiles[urlFiles.rfind('.') + 1:]
    if formatFile == 'csv':
        try:
            data = pd.read_csv(urlFiles, delimiter=';', encoding='cp1251')
        except UnicodeDecodeError:
            data = pd.read_csv(urlFiles, delimiter=';')
        if all:
            return data
        else:
            return data.head(8)
    elif formatFile == 'xlsx' or formatFile == 'xls':
        data = pd.read_excel(urlFiles)
        if all:
            return data
        else:
            return data.head(8)

def getNameFile(urlFile):
    nameFile = urlFile[urlFile.rfind('/')+1:]
    nameFile2 = nameFile[:nameFile.find('.')]
    return nameFile2

def get_param_for_files(list_url):
    listFiles = []
    listError = []
    listDataFrame = []
    if any(list_url) == False:
        listError.append('Пустой список')
        return listError
    for url in list_url:
        column = getNameColumn(list_url[url])
        if column == None:
            listError.append('param')
            listError.append('Не заполнены параметры файла '+url)
            return listError
        param = {}
        param['url'] = column[1]
        param['Артикул'] = column[2].upper()
        param['Производитель'] = column[3].upper()
        param['Наименование'] = column[4]
        param['Цена'] = column[5]
        if column[2] == '' or column[2] == None:
            listError.append('param')
            listError.append('Не заполнен параметр "Артикул" в файле: \n' + column[0])
            return listError
        elif column[3] == '' or column[3] == None:
            listError.append('param')
            listError.append('Не заполнен параметр "Производитель" в файле: \n' + column[0])
            return listError
        elif column[5] == '' or column[5] == None:
            listError.append('param')
            listError.append('Не заполнен параметр "Цена" в файле: \n' + column[0])
            return listError
        listFiles.append(param)

    for val in listFiles:
        dataFrames = getTable(val['url'], True)
        nameColumn = dataFrames.columns

        if val['Наименование'] == '' or val['Наименование'] == None:
            dataFrames = dataFrames.rename(columns={nameColumn[int(val['Артикул'])]: 'Article', nameColumn[int(val['Производитель'])]: 'Brand', nameColumn[int(val['Цена'])]: 'Price'})
        else:
            dataFrames = dataFrames.rename(columns={nameColumn[int(val['Артикул'])]: 'Article', nameColumn[int(val['Производитель'])]: 'Brand', nameColumn[int(val['Наименование'])]: 'Name', nameColumn[int(val['Цена'])]: 'Price'})

        dataFrames['Brand'] = dataFrames['Brand'].astype('str').str.upper()
        dataFrames['Article'] = dataFrames['Article'].astype('str').str.upper()
        dataFrames.loc[dataFrames['Brand'] == 'LEMFORDER', 'Article'] = dataFrames['Article'].replace(to_replace=r'LMI', value='', regex=True).str.slice(start=0, stop=5)
        dataFrames.loc[dataFrames['Brand'] == 'KYB', 'Brand'] = dataFrames['Brand'].replace(to_replace=r'KYB', value='KAYABA', regex=True)
        dataFrames['ArticleBrand'] = dataFrames['Article'].astype('str').replace(to_replace=r'[/\s+\-*/|=_)(}{[\]\':.,><;\"]', value='', regex=True) + dataFrames['Brand'].astype('str').replace(to_replace=r'[/\s+\-*/|=_)(}{[\]\':.,><;\"]', value='', regex=True)
        listDataFrame.append(dataFrames)
    listDataFrame.append(list_url)
    return listDataFrame

def returnData(listData):
    f = pd.DataFrame({'ArticleBrand': listData['ArticleBrand'], 'Price': listData['Price'].astype('str').replace(to_replace=r'\.', value=',',regex=True)})
    return f

def returnNewDate(ListData, f, nameFile1, nameFile2, val, join):

    if val == 0:
        ListData['Price'] = ListData['Price'].astype('str').replace(to_replace=r'\.', value=',', regex=True)

    newData = pd.merge(ListData, f, on='ArticleBrand', how=join, suffixes=('_' + nameFile1, '_' + nameFile2))
    return newData

def renameColumns(ListData, newName):
    ListData = ListData.rename(columns={'Price': 'Price_' + newName})
    return ListData

def saveToCsv(ListDate, url, nameFiles):
    del ListDate['ArticleBrand']
    dfNew = pd.DataFrame()
    for n, e in enumerate(ListDate.columns):
        if e[0:5] == 'Price':
            while True:
                try:
                    dfNew[e] = ListDate[ListDate.columns[n]].replace(to_replace=r'\,', value='.', regex=True).astype(float)
                    break
                except ValueError as arr:
                    arrString = str(arr)
                    valueErr = arrString[arrString.find('\'')+1: arrString.rfind('\'')]
                    indexFrame = ListDate.loc[ListDate[ListDate.columns[n]] == valueErr].index[0]
                    ListDate = ListDate.drop(indexFrame)
                    ListDate = ListDate.reset_index(drop=True)
                    continue

    dfNew['minProvider'] = dfNew.idxmin(axis="columns")
    ListDate['minProvider'] = dfNew['minProvider']
    countMinProvider = ListDate.groupby(['minProvider'], as_index=False)['Article'].count()
    minBrandProviser = ListDate.groupby(['minProvider', 'Brand'], as_index=False)['Article'].count()
    ListDate[''] = ''
    ListDate[' '] = ''
    ListDate['  '] = ''
    ListDate['files'] = countMinProvider['minProvider']
    ListDate['count-min'] = countMinProvider['Article']
    ListDate['    '] = ''
    ListDate['file'] = minBrandProviser['minProvider']
    ListDate['brand'] = minBrandProviser['Brand']
    ListDate['count_min'] = minBrandProviser['Article']
    ListDate.to_csv(url + nameFiles + '.csv', sep=';', index=False, encoding='utf-8-sig')


########function for db###################

def insertSeting(name, url, list_value, column_value):
    array_value = {}
    conn = sql.connect("setingFiles.db")
    curs = conn.cursor()
    curs.execute("SELECT count(url_file) from seting where url_file = '%s'" % url)
    countUrl = list(curs.fetchone())
    if countUrl[0] == 0:
        curs.execute("INSERT INTO seting (name_file,url_file,%s) VALUES ('%s','%s',%s)" % (list_value, name, url, column_value))
    else:
        curs.execute("SELECT * from seting where url_file = '%s'" % url)
        listRow = list(curs.fetchone())
        listNameColumn = list(curs.description)
        for i, e in enumerate(listRow):
            if e == str(column_value):
                array_value[listNameColumn[i][0]] = ''
                curs.execute("Update seting set '%s' = '%s' where url_file = '%s'" % (listNameColumn[i][0], '', url))

            else:
                array_value[listNameColumn[i][0]] = e
        if list_value != 'False':
            curs.execute("Update seting set '%s' = '%s' where url_file = '%s'" % (list_value, column_value, url))
    conn.commit()
    curs.close()
    conn.close()

def getNameColumn(url):
    conn = sql.connect("setingFiles.db")
    curs = conn.cursor()
    curs.execute("SELECT * from seting where url_file = '%s'" % url)
    listRow = curs.fetchone()
    conn.commit()
    curs.close()
    conn.close()
    return listRow









