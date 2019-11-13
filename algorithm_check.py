import assign_elo
from tabulate import tabulate
import psycopg2
import statistics

kfac = 100 # Range from 0, 500, 10
div = 500 # Range from 10, 1000, 10
dfac = 0.5 # Range: 0.1, 1, 0.1
diff = 0
results = []

for kfac in [100]:
    #print(round(100*(kfac-50)/(150-50)))
    for x in [90]:
        dfac = x/100
        for div in [700]:
            diff = 0
            assign_elo.assign_elo(kfac,div)

            conn = psycopg2.connect(host="localhost", database="hifl",
                                        user="postgres", password="banana")
            #print("Database opened successfully")
            cur = conn.cursor()

            cur.execute("""
                WITH elos AS
                    (SELECT elo_date.team, elo
                    FROM (
                        SELECT team, max(date) AS date
                        FROM (SELECT team, date
                        FROM elo_date
                        WHERE date < '2018-07-07') AS pre_2019
                        GROUP BY team) AS t1
                    INNER JOIN elo_date
                    ON elo_date.team = t1.team
                    AND elo_date.date = t1.date),
                    t2 AS
                        (SELECT home_team, home_ft, elos.elo AS home_elo, away_team, away_ft
                        FROM (
                            SELECT home_team, away_team, home_ft, away_ft
                            FROM results
                            WHERE date > '2018-07-07'
                            AND date < '2019-07-07') AS games
                        JOIN elos
                        ON elos.team = games.home_team)
                    SELECT home_team, home_ft, home_elo, away_team, away_ft, elos.elo AS away_elo
                    FROM t2
                    INNER JOIN elos
                    ON elos.team = t2.away_team;""")

            fixtures = cur.fetchall()
            teams = []

            for i in range(len(fixtures)):
                teams.append(fixtures[i][0])

            teams = list(set(teams))

            points = {}
            for team in teams:
                points[team] = [0, 0, 0]

            for fixture in fixtures:
                # Calculate expected result (0 - 1) reflecting expected
                # probability of each team winning.
                home_exp = 1 / (1 + 10 ** ((fixture[5] - fixture[2]) / div))
                away_exp = 1 - home_exp
                draw_exp = 2*dfac*min(home_exp,away_exp)
                home_exp = home_exp - draw_exp/2
                away_exp = away_exp - draw_exp/2
                hp_exp = 3*home_exp + 1*draw_exp
                ap_exp = 3*away_exp + 1*draw_exp
                if fixture[1] > fixture[4]:
                    hp_rl = 3
                    ap_rl = 0
                elif fixture[1] < fixture[4]:
                    hp_rl = 0
                    ap_rl = 3
                else:
                    hp_rl = 1
                    ap_rl = 1
                points[fixture[0]][0] += hp_exp
                points[fixture[0]][1] += hp_rl
                points[fixture[3]][0] += ap_exp
                points[fixture[3]][1] += ap_rl
            diff = []
            for i in range(len(teams)):
                diff.append(abs(points[teams[i]][0]-points[teams[i]][1]))
            results.append([kfac, div, dfac, round(statistics.mean(diff),2)])

results = sorted(results, key=lambda x:x[3], reverse=False)
print(tabulate(results))