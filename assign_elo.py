def assign_elo(kfac, div):
    import psycopg2
    from datetime import datetime

    conn = psycopg2.connect(host="localhost", database="hifl",
                            user="postgres", password="banana")
    #print("Database opened successfully")

    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS elo_date(
        id BIGINT NOT NULL PRIMARY KEY,
        date DATE NOT NULL,
        team TEXT NOT NULL,
        elo INT NOT NULL);""")
    conn.commit()
    cur.execute("""DELETE FROM elo_date;""")
    conn.commit()
    postgres_insert_query = """
            INSERT INTO elo_date
            (id, date, team, elo)
            VALUES
            (%s, \'%s\', \'%s\', %s)
            ON CONFLICT (id) DO NOTHING;"""

    # Get match results data.
    cur.execute("""
        SELECT home_team, away_team, home_ft, away_ft, date
        FROM results
        ORDER BY DATE ASC""")
    results = cur.fetchall()


    # Get team names.
    cur.execute("""
        SELECT team_name
        FROM teams
        """)
    teams = cur.fetchall()

    # Set base elo score to 500.
    elo = {}
    for i in range(len(teams)):
        elo[teams[i][0]] = 500

    # For each match, assign teams new elo score based on result.
    for result in results:
        home_elo = elo[result[0]]
        away_elo = elo[result[1]]
        # Calculate expected result (0 - 1) reflecting expected
        # probability of each team winning.
        home_exp = 1/(1 + 10**((away_elo - home_elo)/div))
        away_exp = 1 - home_exp
        # Assign actual result, 1 = win, 0.5 = draw, 0 = loss.
        if result[2] > result[3]:
            home_sc = 1
            away_sc = 0
        elif result[3] > result[2]:
            home_sc = 0
            away_sc = 1
        else:
            home_sc = away_sc = 0.5
        # New elo score based on difference
        # between expected and actual result.
        elo[result[0]] = elo[result[0]] + kfac*(home_sc - home_exp)
        elo[result[1]] = elo[result[1]] + kfac*(away_sc - away_exp)

        team_ids = []
        # Make id unique by combining date data with team id.
        for i in range(2):
            cur.execute("""SELECT team_id
                FROM teams
                WHERE team_name = \'%s\'""" % result[i])
            conn.commit()
            team_ids.append(cur.fetchall()[0][0])
        home_id = str(result[4]).replace('-','') + str(team_ids[0])
        away_id = str(result[4]).replace('-', '') + str(team_ids[1])
        cur.execute(postgres_insert_query %\
                    (home_id, result[4], result[0], round(elo[result[0]])))
        conn.commit()
        cur.execute(postgres_insert_query % \
                    (away_id, result[4], result[1], round(elo[result[1]])))
        conn.commit()
    conn.close()

if __name__ == "__main__":
    from tabulate import tabulate
    import psycopg2
    assign_elo(100,500)

    conn = psycopg2.connect(host="localhost", database="hifl",
                                user="postgres", password="banana")
    print("Database opened successfully")
    cur = conn.cursor()
    cur.execute("""SELECT * FROM elo_date""")
    rows = cur.fetchall()
    print(tabulate(rows))

    conn.close()