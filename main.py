import requests
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
import datetime
import dbscript


def get_soup(url):
    site = requests.get(url)
    return bs(site.content, 'html.parser')


def get_game(url):
    list_of_links = []
    soup = get_soup(url=url)
    td = soup.findAll("td", {"class": "h-text-left"})
    for tds in td:
        links = tds.findAll(href=True)
        for link in links:
            list_of_links.append(link['href'])
    return list_of_links


def chrome():
    chrome_options = Options()
    chrome_options.add_experimental_option('prefs', {'credentials_enable_service': False,
                                                     'profile.default_content_settings.images': 2})
    chrome_options.add_argument("window-size=1440,1400")
    chrome_options.add_argument("window-position=1900,0")
    chrome_options.add_argument("disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--always-authorize-plugin")
    chrome_options.add_argument("--enable-automatic-password-saving")
    chrome_options.add_argument("--disable-captive-portal-bypass-proxy")

    driver = webdriver.Chrome('C:\\Users\jeck\\Downloads\\chromedriver_win32\\chromedriver.exe',
                              chrome_options=chrome_options)
    return driver


def get_game_odds():
    cur = dbscript.cur
    query = """DELETE FROM bet"""
    cur.execute(query)
    url_list = ['http://www.betexplorer.com/handball/sweden/allsvenskan/',
                'http://www.betexplorer.com/handball/sweden/allsvenskan-2016-2017/results/',
                'http://www.betexplorer.com/handball/sweden/allsvenskan-2015-2016/results/',
                'http://www.betexplorer.com/handball/sweden/elitserien-2015-2016/results/?stage=bwsO16No',
                'http://www.betexplorer.com/handball/sweden/handbollsligan-2016-2017/results/?stage=YBwji1fj',
                'http://www.betexplorer.com/handball/sweden/handbollsligan/results/',
                'http://www.betexplorer.com/handball/sweden/elitserien-women-2015-2016/?stage=6DT0aOMA',
                'http://www.betexplorer.com/handball/sweden/she-women-2016-2017/?stage=rLgzCt1S',
                'http://www.betexplorer.com/handball/sweden/she-women/']
    for url in url_list:
        links = get_game(url=url)
        type_list = ["#ou", "#ah"]
        driver = chrome()
        for line_type in type_list:
            for link in links:
                link_ = str('http://www.betexplorer.com') + str(link) + str(line_type)
                driver.get(link_)
                soup = bs(driver.page_source, "html.parser")
                even_line = get_lines(soup=soup)
                teams = get_teams(soup=soup)
                date = get_date(soup=soup)
                if even_line is None:
                    print(link_)
                if str(line_type) == "#ah":
                    insert_into_db(date, teams, even_line, cur=cur, line_type="#ah")
                else:
                    insert_into_db(date, teams, even_line, cur=cur)


def get_date(soup):
    full_date = soup.find("p", {'id': 'match-date'})
    full_date = full_date.text
    date, time_ = full_date.split(' - ')
    return datetime.datetime.strptime(date, '%d.%m.%Y').strftime('%Y-%m-%d')


def get_teams(soup):
    teams = soup.find("span", {'class': 'list-breadcrumb__item__in'})
    return teams.text


def calc_even_line(odds_diff: list, lines: list) -> float:
    min_diff = min(odds_diff, key=abs)
    max_diff = max(odds_diff, key=abs)
    cor_line = [i for i, x in enumerate(odds_diff) if x == min_diff]
    wrong_line = [i for i, x in enumerate(odds_diff) if x == max_diff]
    line_diff = lines[wrong_line[0]] - lines[cor_line[0]]
    even_line = round(lines[cor_line[0]] + line_diff * abs(min_diff) / (abs(min_diff) + abs(max_diff)), 2)
    return even_line


def insert_into_db(date_, teams_, line_, cur, line_type=None):
    if line_type == "#ah":
        query = "UPDATE bet SET spread=%s WHERE Date=%s and teams=%s"
        cur.execute(query, (line_, date_, teams_))
    else:
        query = "INSERT INTO bet (Date, teams, total) VALUES (%s,%s,%s)"
        cur.execute(query, (date_, teams_, line_))


def get_lines(soup):
    bookies = []
    line_list = []
    odds_list = []
    odds_diff = []
    bookie_lines = []
    links = soup.findAll("a")

    for link in links:
        span_links = link.findAll("span")
        for x in span_links:
            if x.get('title'):
                bookies.append(x.get('title'))
    lines = soup.findAll("td", {'table-main__doubleparameter'})
    odds = soup.findAll("td", {'table-main__odds'})
    [line_list.append(float(x.text)) for x in lines]
    try:
        [odds_list.append(float(' '.join(re.findall(r'\d.\d+', x.text)))) for x in odds]
    except ValueError:
        return max(line_list, key=line_list.count)
    k = 0
    for i in range(len(line_list)):
        if i > 0 and line_list[i] != line_list[i - 1]:
            k += 1
        if bookies[i] == "Pinnacle" and 1.79 < odds_list[2 * (i + k)] < 2.07:
            # print(bookies[i], line_list[i], odds_list[2 * (i + k)], odds_list[2 * (i + k) + 1])
            odds_diff.append(odds_list[2 * (i + k)] - odds_list[2 * (i + k) + 1])
            bookie_lines.append(line_list[i])
            # print(line_list[i], "diff",  diff)

    if len(bookie_lines) > 1:
        # print("correct line", get_even_line(odds_diff, bookie_lines))
        return calc_even_line(odds_diff, bookie_lines)
    elif len(bookie_lines) == 1:
        # print("correct line", bookie_lines)
        return bookie_lines[0]
    else:
        try:
            return max(line_list, key=line_list.count)
        except ValueError:
            return None


if __name__ == '__main__':
    get_game_odds()
