import psycopg2
import requests
import urllib.request
import time
from bs4 import BeautifulSoup
from tabulate import tabulate

url = 'https://hifl.leaguerepublic.com/l/fg/1_181077792.html'
response = requests.get(url)

soup = BeautifulSoup(response.text, 'html.parser')
table = soup.find('table')
table_body = table.find('tbody')
data = []

rows = table_body.find_all('tr')
for row in rows:
    cols = row.find_all('td')
    cols = [ele.text.strip() for ele in cols]
    data.append([ele for ele in cols if ele])  # Get rid of empty values

conn = psycopg2.connect(host="localhost", database="hifl", \
                        user="postgres", password="banana")
print("Database opened successfully")

cur = conn.cursor()

postgres_insert_query = """
    INSERT INTO league_table_1819
    (teamid, teamname, played, wins, draws,
    losses, goals_for, goals_against, goal_diff, points)
    VALUES
    (%s, \'%s\', %s, %s, %s,
    %s, %s, %s, %s, %s)
    ON CONFLICT (teamid) DO NOTHING;"""

for line in data:
    cur.execute(postgres_insert_query % tuple(line))
    conn.commit()

cur.execute("""SELECT * FROM league_table_1819""")
rows = cur.fetchall()
print(tabulate(rows, headers=['teamid', 'teamname', 'played', 'wins', 'draws',\
                              'losses', 'goals_for', 'goals_against', 'goal_diff', 'points']))

print("Success!")
conn.close()