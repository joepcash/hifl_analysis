import psycopg2
import requests
#import urllib.request
import time
from bs4 import BeautifulSoup
from tabulate import tabulate

# Web address section to identify each season's results.
seasons = ['212885780/1_226766634','838109370/1_181077792', '316926888/1_571996630']

results = []

for season in seasons:
    for page in range(1,6):
        url = 'https://hifl.leaguerepublic.com/l/results/' + season + '/-1/-1/' + str(page) + '.html'
        response = requests.get(url)

        # Get HTML from url
        soup = BeautifulSoup(response.text, 'html.parser')
        # Find table in HTML
        if soup.find('table'):
            table = soup.find('table')
        else:
            break
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')
        data = []

        # Convert extracted data into a table format
        for row in rows:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            data.append([ele for ele in cols if ele])  # Get rid of empty values

        for i in range(len(data)):
            # Remove walkovers.
            if "W" in data[i][2]:
                pass
            else:
                for j in range(len(data[i])):
                    # Remove formatting characters
                    data[i][j] = data[i][j].replace("\t","").\
                        replace("\r","").replace("\n"," ",1).replace("\n","")
                # Remove time from date/time column and reformat for SQL.
                data[i][0] = data[i][0].split(" ")[0]
                data[i][0] = "20" + data[i][0].split("/")[2] + "-"\
                             + data[i][0].split("/")[1] + "-"\
                            + data[i][0].split("/")[0]
                # Split score into separate columns.
                score = data[i][2]
                data[i][2] = data[i][3]
                data[i][3] = score.split(" ")[0]
                data[i].append(score.split(" ")[2])
                if "HT" in score:
                    data[i].append(score.split(" ")[4].split("-")[0])
                    data[i].append(score.split(" ")[4].split("-")[1].replace(")",""))
                else:
                    # If no half-time score given, leave blank.
                    data[i].append("null")
                    data[i].append("null")
                results.append(data[i])

        # Pause code between web calls so not to have IP blocked.
        time.sleep(1)

conn = psycopg2.connect(host="localhost", database="hifl", \
                        user="postgres", password="banana")
print("Database opened successfully")

cur = conn.cursor()
cur.execute("""
    CREATE TABLE IF NOT EXISTS results(
    result_id BIGINT NOT NULL PRIMARY KEY,
    date DATE NOT NULL,
    home_team TEXT NOT NULL,
    away_team TEXT NOT NULL,
    home_ft INT NOT NULL,
    away_ft INT NOT NULL,
    home_ht INT,
    away_ht INT);""")
conn.commit()

postgres_insert_query = """
        INSERT INTO results
        (result_id, date, home_team, away_team,
        home_ft, away_ft, home_ht, away_ht)
        VALUES
        (%s, \'%s\', \'%s\', \'%s\', %s, %s, %s, %s)
        ON CONFLICT (result_id) DO NOTHING;"""

for line in results:
    team_ids = []
    # Make result_id unique by combining date data with team ids.
    for i in range(1,3):
        cur.execute("""SELECT team_id
        FROM teams
        WHERE team_name = \'%s\'""" % line[i])
        conn.commit()
        team_ids.append(cur.fetchall()[0][0])
    id = line[0].replace('-','') + str(team_ids[0]) + str(team_ids[1])
    cur.execute(postgres_insert_query % tuple([id] + line))
    conn.commit()

cur.execute("""SELECT * FROM results""")
rows = cur.fetchall()
print(tabulate(rows))

conn.close()