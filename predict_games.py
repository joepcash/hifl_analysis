def predict_games(kfac, div, dfac, start_date, end_date):
    import psycopg2

    conn = psycopg2.connect(host="localhost", database="hifl",
                            user="postgres", password="banana")
    print("Database opened successfully")
    cur = conn.cursor()

    # Get all expected values
    cur.execute("""
        SELECT 
            home_team, ROUND(100*home_exp), ROUND(100*draw_exp),
            ROUND(100*away_exp), away_team
        FROM all_games
        WHERE date >= '"""
                + start_date + """'
        AND date <= '"""
                + end_date + """'
        ORDER BY date ASC;""")
    return cur.fetchall()

if __name__ == "__main__":
    from tabulate import tabulate
    print(tabulate(predict_games(100, 700, 0.3, '2019-11-18', '2019-12-30')
                   , headers=['Home Team', 'Home Win', 'Draw', 'Away Win', 'Away Team']))
