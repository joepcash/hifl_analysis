def extract_1920_table():
    import psycopg2
    import requests
    from bs4 import BeautifulSoup

    url = 'https://hifl.leaguerepublic.com/l/fg/1_226766634.html'
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
    cur.execute("""
        CREATE TABLE IF NOT EXISTS league_table_1920(
        teamid INT NOT NULL PRIMARY KEY,
        teamname TEXT NOT NULL,
        played INT NOT NULL,
        wins INT NOT NULL,
        draws INT NOT NULL,
        losses INT NOT NULL,
        goals_for INT NOT NULL,
        goals_against INT NOT NULL,
        goal_diff INT NOT NULL,
        points INT NOT NULL);""")
    conn.commit()
    cur.execute("""DELETE FROM league_table_1920;""")
    conn.commit()
    postgres_insert_query = """
        INSERT INTO league_table_1920
        (teamid, teamname, played, wins, draws,
        losses, goals_for, goals_against, goal_diff, points)
        VALUES
        (%s, \'%s\', %s, %s, %s,
        %s, %s, %s, %s, %s)
        ON CONFLICT (teamid) DO NOTHING;"""

    for line in data:
        cur.execute(postgres_insert_query % tuple(line))
        conn.commit()
    conn.close()

if __name__ == "__main__":
    from tabulate import tabulate
    import psycopg2

    extract_1920_table()
    conn = psycopg2.connect(host="localhost", database="hifl", \
                            user="postgres", password="banana")
    print("Database opened successfully")

    cur = conn.cursor()
    cur.execute("""SELECT * FROM league_table_1920""")
    rows = cur.fetchall()
    print(tabulate(rows, headers=['teamid', 'teamname', 'played', 'wins', 'draws',\
                                  'losses', 'goals_for', 'goals_against', 'goal_diff', 'points']))

    print("Success!")
    conn.close()