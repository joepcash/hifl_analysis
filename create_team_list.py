import psycopg2
import requests
from bs4 import BeautifulSoup
import time
from tabulate import tabulate

# Create list of web address sections that identify each season.
seasons = ['1_226766634','1_181077792','1_571996630']
data = []

for season in seasons:
    url = 'https://hifl.leaguerepublic.com/l/fg/'+ season + '.html'
    response = requests.get(url)

    # Extract html from link.
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table')
    table_body = table.find('tbody')

    # Extract table from HTML.
    rows = table_body.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        data.append([ele for ele in cols if ele])  # Get rid of empty values
    time.sleep(1)

# Strip only team name data.
for i in range(len(data)):
    data[i] = data[i][1]

data = list(set(data))

conn = psycopg2.connect(host="localhost", database="hifl", \
                        user="postgres", password="banana")
print("Database opened successfully")

cur = conn.cursor()
cur.execute("""
    CREATE TABLE IF NOT EXISTS teams(
    team_id INT NOT NULL PRIMARY KEY,
    team_name TEXT NOT NULL UNIQUE);""")
conn.commit()

postgres_insert_query = """
        INSERT INTO teams
        (team_id, team_name)
        VALUES
        (%s, \'%s\')
        ON CONFLICT (team_name) DO NOTHING;"""

for i in range(len(data)):
    cur.execute(postgres_insert_query % (i+100,data[i]))
    conn.commit()


cur.execute("""SELECT * FROM teams""")
conn.commit()
rows = cur.fetchall()
print(tabulate(rows))
conn.close()