import psycopg2
from tabulate import tabulate

conn = psycopg2.connect(host="localhost", database="hifl",
                        user="postgres", password="banana")
print("Database opened successfully")
cur = conn.cursor()

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

cur.execute("""
    SELECT teamname, points
    FROM league_table_1920;""")
teams = cur.fetchall()

points = {}
for i in range(len(teams)):
    points[teams[i][0]] = teams[i][1]

for fixture in fixtures:
    # Calculate expected result (0 - 1) reflecting expected
    # probability of each team winning.
    home_exp = 1 / (1 + 10 ** ((fixture[3] - fixture[1]) / 500))
    away_exp = 1 - home_exp
    points[fixture[0]] += 3*home_exp
    points[fixture[2]] += 3*away_exp

table = []
for x,y in points.items():
    table.append([x,round(y)])

table = sorted(table, key=lambda x:x[1], reverse=True)
print(tabulate(table))