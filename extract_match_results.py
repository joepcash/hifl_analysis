import psycopg2
import requests
import urllib.request
import time
from bs4 import BeautifulSoup
from tabulate import tabulate

# Web address section to identify each season's results.
seasons = ['212885780/1_226766634','838109370/1_181077792']

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
            if "W" in data[i][2]:
                pass
            else:
                for j in range(len(data[i])):
                    # Remove formatting characters
                    data[i][j] = data[i][j].replace("\t","").\
                        replace("\r","").replace("\n"," ",1).replace("\n","")
                # Remove time from date/time column
                data[i][0] = data[i][0].split(" ")[0]
                # Split score into separate columns
                score = data[i][2]
                data[i][2] = data[i][3]
                data[i][3] = score.split(" ")[0]
                data[i].append(score.split(" ")[2])
                if "HT" in score:
                    data[i].append(score.split(" ")[4].split("-")[0])
                    data[i].append(score.split(" ")[4].split("-")[1].replace(")",""))
                else:
                    # If no half-time score given, leave blank.
                    data[i].append("")
                    data[i].append("")
                results.append(data[i])

        time.sleep(1)

print(tabulate(results))

# conn = psycopg2.connect(host="localhost", database="hifl", \
#                         user="postgres", password="banana")
# print("Database opened successfully")
#
# cur = conn.cursor()

#conn.close()