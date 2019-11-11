import psycopg2
from tabulate import tabulate

conn = psycopg2.connect(host="localhost", database="hifl", \
                        user="postgres", password="banana")
print("Database opened successfully")

cur = conn.cursor()

# Get match results data.
cur.execute("""
    SELECT home_team, away_team, home_ft, away_ft
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
    home_exp = 1/(1 + 10**((away_elo - home_elo)/500))
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
    elo[result[0]] = elo[result[0]] + 100*(home_sc - home_exp)
    elo[result[1]] = elo[result[1]] + 100*(away_sc - away_exp)

for x,y in elo.items():
    print(x,round(y))