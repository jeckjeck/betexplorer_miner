import requests
from bs4 import BeautifulSoup as bs
import datetime
from pymongo import MongoClient

# insert hostname, username, password for mongodb
# and uncoment db, and insert_into_db call


def con_to_mongo_db(db_, drop=True):
    dbconn = MongoClient(host = 'hostname', port=27017)
    _db = dbconn[db_]
    _db.authenticate("username", "password")
    if drop:
        _db.dat.drop()
    return _db


def insert_into_db(db, team, wins, losses):
    date = str(datetime.datetime.now())[:10]
    db.dat.insert_one(
        {
            date: {
                "team": team,
                "wins": int(wins),
                "losses": int(losses),
            }
        }
    )


url = "http://www.espn.com/nba/standings"

def get_soup(url):
    site = requests.get(url)
    return bs(site.content, 'html.parser')

def save_records_to_db(cur, team, wins, losses):
    date = str(datetime.datetime.now())[:10]
    query = "INSERT INTO nba (date, teams, wins, losses) VALUES (%s, %s,%s,%s)"
    cur.execute(query, (date, team, wins, losses),)

def get_team_and_current_record():
    soup = get_soup(url=url)
    td_rows = soup.findAll("tr", {"class": "standings-row"})
    # db = con_to_mongo_db(db_='nba_standings')
    for standings in td_rows:
        team = standings.find("span", {"class": "team-names"})
        all_tds = standings.findAll("td")
        wins = all_tds[1].text
        losses = all_tds[2].text
        print(team.text, wins, "-", losses)
        # insert_into_db(db=db, team= team.text, wins = wins, losses = losses)


if __name__ == '__main__':
    get_team_and_current_record()