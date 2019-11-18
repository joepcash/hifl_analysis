import psycopg2
from tabulate import tabulate

def get_fixtures():
    import time
    import requests
    from bs4 import BeautifulSoup

    fixtures = []

    for page in range(1,10):
        url = 'https://hifl.leaguerepublic.com/l/matches/212885780/1_226766634/-1/-1/-1/' + str(page) + '.html'
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
            for j in range(len(data[i])):
                # Remove formatting characters
                data[i][j] = data[i][j].replace("\t", ""). \
                    replace("\r", "").replace("\n", " ", 1).replace("\n", "")
            # Remove time from date/time column and reformat for SQL.
            if "TBC" in data[i][0]:
                data[i][0] = "null"
            else:
                data[i][0] = data[i][0].split(" ")[0]
                data[i][0] = "20" + data[i][0].split("/")[2] + "-" \
                             + data[i][0].split("/")[1] + "-" \
                             + data[i][0].split("/")[0]
            data[i][2] = data[i][3]
            data[i][3] = data[i][4] = "null"
            data[i].append("null")
            data[i].append("null")
            fixtures.append(data[i])
        # Pause code between web calls so not to have IP blocked.
        time.sleep(1)
    return fixtures

if __name__ == "__main__":
    fixtures = get_fixtures()

    conn = psycopg2.connect(host="localhost", database="hifl", \
                            user="postgres", password="banana")
    print("Database opened successfully")

    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS fixtures(
        id BIGINT NOT NULL PRIMARY KEY,
        date DATE,
        home_team TEXT NOT NULL,
        away_team TEXT NOT NULL);""")
    conn.commit()

    postgres_insert_query = """
            INSERT INTO fixtures
            (id, date, home_team, away_team)
            VALUES
            (%s, %s, \'%s\', \'%s\')
            ON CONFLICT (id) DO NOTHING;"""

    for line in fixtures:
        team_ids = []
        # Make result_id unique by combining date data with team ids.
        for k in [1,2]:
            cur.execute("""SELECT team_id
                FROM teams
                WHERE team_name = \'%s\'""" % line[k])
            conn.commit()
            team_ids.append(cur.fetchall()[0][0])
        # If date is TBC, replace date with 0s.
        if line[0] == "null":
            id = '00000000' + str(team_ids[0]) + str(team_ids[1])
            cur.execute(postgres_insert_query % (id, line[0], line[1], line[2]))
        else:
            id = line[0].replace('-', '') + str(team_ids[0]) + str(team_ids[1])
            cur.execute(postgres_insert_query % (id, "\'" + str(line[0]) + "\'", line[1], line[2]))
        conn.commit()

    cur.execute("""SELECT * FROM fixtures""")
    rows = cur.fetchall()
    print(tabulate(rows))

    conn.close()