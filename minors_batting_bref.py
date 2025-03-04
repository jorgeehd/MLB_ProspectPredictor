import requests
from bs4 import BeautifulSoup
import csv
from pybaseball.datasources.bref import BRefSession

session = BRefSession()


def get_player_url(player_name):

    #player_url for Jose Altuve =   "https://www.baseball-reference.com/players/a/altuvjo01.shtml" Example url
    names = player_name.split()

    firstName = names[0].lower() 
    secondName = names[1].lower()

    if len(names) == 2: 
        player_url ="https://www.baseball-reference.com/players/" + secondName[0] + "/" + secondName[:5] + firstName[0:2]  + "01" + ".shtml"
    else: 
        #Edge case if player is a Jr.
        player_url ="https://www.baseball-reference.com/players/" + secondName[0] + "/" + secondName[:5] + firstName[0:2]  + "02" + ".shtml"
    
     
     
#    search_url = "https://www.baseball-reference.com/search/search.cgi?search=" + player_name.replace(" ", "+")

    response = session.get(player_url)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")
    # Findin player's minor league stats

    search_strings = ["Minor & Fall Lg Stats", "Minor Lg Stats"]
    
    player_link = soup.find('a', string=lambda text: text and any(s in text for s in search_strings))
    #print( player_link) 
    #print("player_link : " , player_link)
    
    
    if player_link:
       return "https://www.baseball-reference.com" + player_link['href']
       
    return None

def get_player_statistics(player_url):
    response = session.get(player_url)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find("table", {"id": "standard_batting"})
    
    if table:
        rows = table.find_all("tr")
        headers = [header.text.strip() for header in rows[0].find_all("th")]
        print(headers)
        data = []
        for row in rows[1:]:
            cells = row.find_all(["th", "td"])
            row_data = {headers[i]: cell.text.strip() for i, cell in enumerate(cells)}
            #print(row_data)
            data.append(row_data)
        return headers, data
    else:
        print("Statistics table not found for:", player_url)
        return None, None

def get_data(player_names : list):
    #player_names = ["Juan Soto", "Mike Trout", "Francisco Lindor"]  # List of player names
    all_player_data = []

    for player_name in player_names:
        print(f"Processing {player_name}...")
        player_url = get_player_url(player_name)
#        print(player_url)
        
        if player_url:
            headers, data = get_player_statistics(player_url)
            if data:
                all_player_data.append((player_name, headers, data))
        else:
            print(f"Could not find URL for {player_name}")

    # Save to CSV
    with open('players_data.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Player Name'] + ['Year'] + headers)  # Adjust as needed
        
        for player_name, headers, data in all_player_data:
            for row in data:
                    row_data = [row.get(header, "") for header in headers[1:]]  # Use get to handle missing keys
                    writer.writerow([player_name] + [row.get("Year", "")] + row_data)

    print("Data saved to players_data.csv.")

#if __name__ == "__main__":
#    get()