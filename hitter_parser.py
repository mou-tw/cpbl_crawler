from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import os
import time
import re

options = Options()
options.add_argument("--disable-notifications")


def soup_extract(soup, rd):
    name = soup.select('div[class="name"]')[0].text.strip().split('\n')[0]
    bd = soup.select('div[class="desc"]')[3].text.strip()
    bd_y = soup.select('div[class="desc"]')[3].text.strip()[:4]
    fav_p = soup.select('div[class="desc"]')[1].text.strip()[:2]
    fav_h = soup.select('div[class="desc"]')[1].text.strip()[2:]
    country = soup.select('div[class="desc"]')[6].text.strip()
    years = [i.text.strip() for i in soup.select('td div[class="year"]')[:rd]]
    team = [i.text.strip() for i in soup.select('td div[class="team"]')[:rd]]
    ages = [int(i) - int(bd_y) for i in years]

    return name, fav_p, fav_h, country, years, team, ages, bd_y

def soup_agg_df(soup, column_d):
    agg_df = []
    for i in range(int(len(soup.find_all('tbody')[1].select('td[class="num"]')) / (len(column_d) - 1))):
        t_lst = []

        tmp = soup.find_all('tbody')[1].find_all("td", class_="num")
        for ii in tmp[i * (len(column_d) - 1):(i + 1) * (len(column_d) - 1)]:
            t_lst.append([ii.text.strip().split(' ')[0].strip()] + [i.text for i in ii.find_all("span")])

        t_year = soup.find_all('tbody')[1].select('td[class="sticky"]')[i].select('div[class="year"]')[0].text.strip()
        t_team = soup.find_all('tbody')[1].select('td[class="sticky"]')[i].select('div[class="team"]')[0].text.strip()
        t_df = pd.DataFrame(t_lst).T
        t_df.insert(0, 'year', t_year)
        t_df.insert(0, 'team', t_team)
        agg_df.append(t_df)
    df_d = pd.concat(agg_df)
    return  df_d

def soup_agg_df_dual(soup, column_d):
    agg_df = []
    for i in range(int(len(soup.find_all('tbody')[0].select('td[class="num"]')) / (len(column_d) - 1))):
        t_lst = []

        tmp = soup.find_all('tbody')[0].find_all("td", class_="num")
        for ii in tmp[i * (len(column_d) - 1):(i + 1) * (len(column_d) - 1)]:
            t_lst.append([ii.text.strip().split(' ')[0].strip()] + [i.text for i in ii.find_all("span")])

        t_year = soup.find_all('tbody')[0].select('td[class="sticky"]')[i].select('div[class="year"]')[0].text.strip()
        t_team = soup.find_all('tbody')[0].select('td[class="sticky"]')[i].select('div[class="team"]')[0].text.strip()
        t_df = pd.DataFrame(t_lst).T
        t_df.insert(0, 'year', t_year)
        t_df.insert(0, 'team', t_team)
        agg_df.append(t_df)
    df_d = pd.concat(agg_df)
    return  df_d


def parse_dual_type_player(soup):
    atk_soup = soup.select('table')[0]
    dfs_soup = soup.select('div[class="RecordTableOuter"]')[2]

    # get hitter's attack abilities data
    column = [i.string.strip() for i in atk_soup.find('tr').select('th[class="num"] ')]
    rd = int(len(soup.find('tbody').select('td[class="num"]')) / len(column) - 1)
    agg_list = []
    for i in range(rd):
        agg_list.append([i.text.strip() for i in soup.find('tbody').select('td[class="num"]')][
                        (i) * len(column):(i + 1) * len(column)])
    df = pd.DataFrame(agg_list, columns=column)
    name, fav_p, fav_h, country, years, team, ages, bd_y = soup_extract(soup, rd)
    df.insert(0, 'name', name)
    df.insert(1, '投', fav_p)
    df.insert(1, '打', fav_h)
    df.insert(1, 'country', country)
    df.insert(1, 'play_year', years)
    df.insert(1, 'team', team)
    df.insert(1, 'ages', ages)

    # get hitter's defense abilities data

    # print(dfs_soup.find_all('tbody')[0].select('th'))
    column_d = [i.text.strip() for i in dfs_soup.find_all('tbody')[0].select('th')][1:]

    tmp_filed_lst = [i.text for i in dfs_soup.find_all('tbody')[0].find_all("td", class_="pos")]
    tmp_filed_lst = [i.replace('手', '手 ') for i in tmp_filed_lst]
    tmp_filed_lst = [i.split(' ') for i in tmp_filed_lst]
    tmp_filed_lst = [i.strip() for inner in tmp_filed_lst for i in inner]
    tmp_filed_lst = [i for i in tmp_filed_lst if i != '']
    tmp_filed_lst.append('tmp')

    df_d = soup_agg_df_dual(dfs_soup, column_d)
    df_d.insert(2, 'field', tmp_filed_lst)
    df_d = df_d.loc[df_d.field != '合計']
    df_d = df_d.loc[df_d.field != 'tmp']
    df_d.columns = ['team', 'play_year'] + column_d
    df_d.insert(0, 'name', name)
    df_d.insert(1, '投', fav_p)
    df_d.insert(1, '打', fav_h)
    df_d.insert(1, 'country', country)
    df_d.insert(1, 'bd_y', int(bd_y))
    df_d.play_year = df_d.play_year.astype('int')
    df_d['age'] = df_d.play_year - df_d.bd_y
    df_d.drop(['bd_y'], axis=1, inplace=True)

    df_d = df_d[['name', 'age', 'team', 'play_year', 'country', '打', '投', '守備位置', '出賽數', '守備機會',
                 '刺殺', '助殺', '失誤', '雙殺', '三殺', '守備率']]

    return df, df_d

def parse_single_type_player(soup):
    # get hitter's attack abilities data
    column = [i.string.strip() for i in soup.find('tr').select('th[class="num"] ')]
    rd = int(len(soup.find('tbody').select('td[class="num"]')) / len(column) - 1)
    agg_list = []
    for i in range(rd):
        agg_list.append([i.text.strip() for i in soup.find('tbody').select('td[class="num"]')][
                        (i) * len(column):(i + 1) * len(column)])
    df = pd.DataFrame(agg_list, columns=column)
    name, fav_p, fav_h, country, years, team, ages, bd_y = soup_extract(soup, rd)
    df.insert(0, 'name', name)
    df.insert(1, '投', fav_p)
    df.insert(1, '打', fav_h)
    df.insert(1, 'country', country)
    df.insert(1, 'play_year', years)
    df.insert(1, 'team', team)
    df.insert(1, 'ages', ages)


    # get hitter's defense abilities data
    column_d = [i.text.strip() for i in soup.find_all('tbody')[1].select('th')][1:]

    tmp_filed_lst = [i.text for i in soup.find_all('tbody')[1].find_all("td", class_="pos")]
    tmp_filed_lst = [i.replace('手', '手 ') for i in tmp_filed_lst]
    tmp_filed_lst = [i.split(' ') for i in tmp_filed_lst]
    tmp_filed_lst = [i.strip() for inner in tmp_filed_lst for i in inner]
    tmp_filed_lst = [i for i in tmp_filed_lst if i != '']
    tmp_filed_lst.append('tmp')

    df_d = soup_agg_df(soup, column_d)
    df_d.insert(2, 'field', tmp_filed_lst)
    df_d = df_d.loc[df_d.field != '合計']
    df_d = df_d.loc[df_d.field != 'tmp']
    df_d.columns = ['team', 'play_year'] + column_d
    df_d.insert(0, 'name', name)
    df_d.insert(1, '投', fav_p)
    df_d.insert(1, '打', fav_h)
    df_d.insert(1, 'country', country)
    df_d.insert(1, 'bd_y', int(bd_y))
    df_d.play_year = df_d.play_year.astype('int')
    df_d['age'] = df_d.play_year - df_d.bd_y
    df_d.drop(['bd_y'], axis=1, inplace=True)

    df_d = df_d[['name', 'age', 'team', 'play_year', 'country', '打', '投', '守備位置', '出賽數', '守備機會',
                 '刺殺', '助殺', '失誤', '雙殺', '三殺', '守備率']]
    return df, df_d

def hitter_parse_todf(url):
    chrome = webdriver.Chrome('./chromedriver', options=options)
    assert type(url) == type('str') , 'url should be string'
    chrome.get(url)
    soup = BeautifulSoup(chrome.page_source, 'html.parser')

    #get hitter's attack abilities data
    column = [i.string.strip() for i in soup.find('tr').select('th[class="num"] ')]
    rd = int(len(soup.find('tbody').select('td[class="num"]')) / len(column) - 1)
    agg_list = []
    for i in range(rd):
        agg_list.append([i.text.strip() for i in soup.find('tbody').select('td[class="num"]')][(i) * len(column):(i + 1) * len(column)])
    df = pd.DataFrame(agg_list, columns=column)
    name, fav_p, fav_h, country, years, team, ages, bd_y = soup_extract(soup,rd)
    df.insert(0, 'name', name)
    df.insert(1, '投', fav_p)
    df.insert(1, '打', fav_h)
    df.insert(1, 'country', country)
    df.insert(1, 'play_year', years)
    df.insert(1, 'team', team)
    df.insert(1, 'ages', ages)

    chrome.close()
    # get hitter's attack abilities data
    column_d = [i.text.strip() for i in soup.find_all('tbody')[1].select('th')][1:]


    tmp_filed_lst = [i.text for i in soup.find_all('tbody')[1].find_all("td", class_="pos")]
    tmp_filed_lst = [i.replace('手','手 ') for i in tmp_filed_lst]
    tmp_filed_lst = [i.split(' ') for i in tmp_filed_lst]
    tmp_filed_lst = [i.strip() for inner in tmp_filed_lst for i in inner]
    tmp_filed_lst = [i for i in tmp_filed_lst if i != '']
    tmp_filed_lst.append('tmp')



    df_d = soup_agg_df(soup, column_d)
    df_d.insert(2, 'field', tmp_filed_lst)
    df_d = df_d.loc[df_d.field != '合計']
    df_d = df_d.loc[df_d.field != 'tmp']
    df_d.columns = ['team', 'play_year'] + column_d
    df_d.insert(0, 'name', name)
    df_d.insert(1, '投', fav_p)
    df_d.insert(1, '打', fav_h)
    df_d.insert(1, 'country', country)
    df_d.insert(1, 'bd_y', int(bd_y))
    df_d.play_year = df_d.play_year.astype('int')
    df_d['age'] = df_d.play_year - df_d.bd_y
    df_d.drop(['bd_y'], axis=1, inplace=True)

    df_d = df_d[['name', 'age', 'team', 'play_year', 'country', '打', '投', '守備位置', '出賽數', '守備機會',
       '刺殺', '助殺', '失誤', '雙殺', '三殺', '守備率']]
    # print(df_d.columns)

    return df , df_d

def hitter_parse_tocsv(url):
    assert type(url) == type('str'), 'url should be string'
    chrome = webdriver.Chrome('./chromedriver', options=options)
    chrome.get(url)
    time.sleep(0.7)
    soup = BeautifulSoup(chrome.page_source, 'html.parser')
    chrome.close()

    try:
        if len(soup.select('div[class="RecordTableWrap"]')) == 3:
            df, df_d = parse_single_type_player(soup)

        elif len(soup.select('div[class="RecordTableWrap"]')) == 4:
            df, df_d = parse_dual_type_player(soup)

        os.makedirs('../tmp_csv/', exist_ok=True)
        df.to_csv(f'./tmp_csv/{df.name.unique()[0]}_atk.csv', index=False)
        df_d.to_csv(f'./tmp_csv/{df.name.unique()[0]}_dfs.csv', index=False)

    except:
        print('parse error!', url)
        with open('../undone_url.txt', 'a') as f:
            f.write(url)




def hitter_parse_hotfix(url):
    chrome = webdriver.Chrome('./chromedriver', options=options)
    assert type(url) == type('str') , 'url should be string'
    chrome.get(url)

    soup = BeautifulSoup(chrome.page_source, 'html.parser')
    chrome.close()
    print(len(soup.select('table')))

    if len(soup.select('div[class="RecordTableWrap"]')) == 3:
        df, df_d = parse_single_type_player(soup)
        print(df_d.columns)
        print(df)
        print(df_d)

    elif len(soup.select('div[class="RecordTableWrap"]')) == 4:
        df, df_d = parse_dual_type_player(soup)
        # print(df_d.columns)
        # print(df)
        # print(df_d)

    n = df.name.unique()[0].replace('*','')
    os.makedirs('../tmp_csv/', exist_ok=True)
    df.to_csv(f'./tmp_csv/{n}_atk.csv',index=False)
    df_d.to_csv(f'./tmp_csv/{n}_dfs.csv',index=False)




if __name__ == '__main__':
    url = "https://www.cpbl.com.tw/team/person?acnt=0000001136"
    # df , df_d = hitter_parse_todf(url)
    # df.to_csv('bt_atk.csv',index=False)
    # df_d.to_csv('bt_dfs.csv', index=False)
    hitter_parse_hotfix(url)