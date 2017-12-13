import requests
import dbscript
from bs4 import BeautifulSoup as bs
import datetime

url = "http://www.espn.com/nba/standings"

def get_soup(url):
    site = requests.get(url)
    return bs(site.content, 'html.parser')

def save_records_to_db(cur, team, wins, losses):
    date = str(datetime.datetime.now())[:10]
    query = "INSERT INTO nba (date, teams, wins, losses) VALUES (%s, %s,%s,%s)"
    cur.execute(query, (date, team, wins, losses),)

def get_team_and_current_record():
    cur = dbscript.cur
    query = """DELETE FROM nba"""
    cur.execute(query)
    soup = get_soup(url=url)
    td_rows = soup.findAll("tr", {"class": "standings-row"})
    for standings in td_rows:
        team = standings.find("span", {"class": "team-names"})
        all_tds = standings.findAll("td")
        wins = all_tds[1].text
        losses = all_tds[2].text
        print(team.text, wins, "-", losses)
        save_records_to_db(cur, team.text, wins, losses)


if __name__ == '__main__':
    get_team_and_current_record()