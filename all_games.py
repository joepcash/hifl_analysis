def get_all_games():
    import assign_elo
    import extract_match_results
    import extract_fixtures
    import psycopg2

    games = sorted(extract_match_results.get_results(), key=lambda x:x[0], reverse=False) +\
              sorted(extract_fixtures.get_fixtures(), key=lambda x:x[0], reverse=False)

    assign_elo.assign_elo(100,700)

    conn = psycopg2.connect(host="localhost", database="hifl", \
                            user="postgres", password="banana")
    print("Database opened successfully")

    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS all_games(
        game_id BIGINT NOT NULL PRIMARY KEY,
        date DATE,
        home_team TEXT NOT NULL,
        away_team TEXT NOT NULL,
        home_ft INT,
        away_ft INT,
        home_ht INT,
        away_ht INT,
        home_exp NUMERIC(2,2),
        away_exp NUMERIC(2,2),
        draw_exp NUMERIC(2,2));""")
    conn.commit()

    insert_query = """
            INSERT INTO all_games
            (game_id, date, home_team, away_team,
            home_ft, away_ft, home_ht, away_ht,
            home_exp, away_exp, draw_exp)
            VALUES
            (%s, %s, \'%s\', \'%s\', %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (game_id)
            DO """
    update_query = """UPDATE SET
            game_id = %s,
            date = %s,
            home_team = \'%s\',
            away_team = \'%s\',
            home_ft = %s,
            away_ft = %s,
            home_ht = %s,
            away_ht = %s,
            home_exp = %s,
            away_exp = %s,
            draw_exp = %s;"""

    for game in games:
        team_ids = []
        elos = []
        # Make result_id unique by combining date data with team ids.
        for i in range(1, 3):
            cur.execute("""SELECT team_id
            FROM teams
            WHERE team_name = \'%s\'""" % game[i])
            conn.commit()
            team_ids.append(cur.fetchall()[0][0])
            if game[0] == 'null':
                cur.execute("""SELECT elo
                                        FROM elo_date
                                        WHERE team = \'%s\'
                                        ORDER BY date DESC
                                        LIMIT 1""" % game[i])
            else:
                cur.execute("""SELECT elo
                                FROM elo_date
                                WHERE team = \'%s\'
                                AND date < \'%s\'
                                ORDER BY date DESC
                                LIMIT 1""" % (game[i], game[0]))
            conn.commit()
            temp = cur.fetchall()
            if len(temp) == 0:
                elos.append(500)
            else:
                elos.append(temp[0][0])
        # Calculate expected result (0 - 1) reflecting expected
        # probability of each team winning.
        home_exp = 1 / (1 + 10 ** ((elos[1] - elos[0]) / 700))
        away_exp = 1 - home_exp
        draw_exp = 2 * 0.3 * min(home_exp, away_exp)
        home_exp = home_exp - draw_exp / 2
        away_exp = away_exp - draw_exp / 2
        # If date is TBC, replace date with 0s.
        if game[0] == "null":
            id = '00000000' + str(team_ids[0]) + str(team_ids[1])
            cur.execute(insert_query % tuple([id] + game + [home_exp, away_exp, draw_exp]) + \
                        update_query % tuple([id] + game + [home_exp, away_exp, draw_exp]))
        else:
            id = game[0].replace('-', '') + str(team_ids[0]) + str(team_ids[1])
            cur.execute(insert_query % tuple([id] + ["\'" + game[0] + "\'"] + game[1:] + [home_exp, away_exp, draw_exp]) +\
                            update_query % tuple([id] + ["\'" + game[0] + "\'"] + game[1:] + [home_exp, away_exp, draw_exp]))
        conn.commit()
    conn.close()

if __name__ == "__main__":
    from tabulate import tabulate
    import psycopg2

    conn = psycopg2.connect(host="localhost", database="hifl", \
                            user="postgres", password="banana")
    print("Database opened successfully")

    cur = conn.cursor()
    cur.execute("""SELECT * FROM all_games""")
    rows = cur.fetchall()
    print(tabulate(rows))

    conn.close()