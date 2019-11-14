def predict_points(kfac, div, dfac):
    import psycopg2
    import assign_elo

    assign_elo.assign_elo(kfac, div)

    conn = psycopg2.connect(host="localhost", database="hifl",
                            user="postgres", password="banana")
    print("Database opened successfully")
    cur = conn.cursor()

    # Collect all fixtures from database with each teams most recent elo score
    cur.execute("""
        WITH elos AS 
        (SELECT elo_date.team, elo
        FROM (
            SELECT team, max(date) AS date
            FROM elo_date
            GROUP BY team) AS t1
        INNER JOIN elo_date
        ON elo_date.team = t1.team
        AND elo_date.date = t1.date),
        t2 AS 
            (SELECT home_team, elos.elo AS home_elo, away_team
            FROM fixtures
            JOIN elos
            ON elos.team = fixtures.home_team)
        SELECT home_team, home_elo, away_team, elos.elo AS away_elo
        FROM t2
        INNER JOIN elos
        ON elos.team = t2.away_team;""")
    fixtures = cur.fetchall()

    # Collect all team names.
    cur.execute("""
        SELECT teamname, points, played
        FROM league_table_1920;""")
    teams = cur.fetchall()

    points = {}
    for i in range(len(teams)):
        points[teams[i][0]] = [teams[i][1], teams[i][2]]

    for fixture in fixtures:
        # Calculate expected result (0 - 1) reflecting expected
        # probability of each team winning.
        home_exp = 1 / (1 + 10 ** ((fixture[3] - fixture[1]) / div))
        away_exp = 1 - home_exp
        draw_exp = 2 * dfac * min(home_exp, away_exp)
        home_exp = home_exp - draw_exp / 2
        away_exp = away_exp - draw_exp / 2
        points[fixture[0]][0] += 3*home_exp + 1*draw_exp
        points[fixture[2]][0] += 3*away_exp + 1*draw_exp
        points[fixture[0]][1] += 1
        points[fixture[2]][1] += 1

    table = []
    for x,y in points.items():
        table.append([x,y[1],round(y[0])])

    table = sorted(table, key=lambda x:x[2], reverse=True)
    conn.close()
    return table

if __name__ == "__main__":
    from tabulate import tabulate
    print(tabulate(predict_points(100, 700, 0.9),headers=['Team', 'Played','Points']))