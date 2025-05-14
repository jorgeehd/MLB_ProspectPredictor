import argparse
import requests
from bs4 import BeautifulSoup
import csv
import re
from pybaseball.datasources.bref import BRefSession

session = BRefSession()


def get_player_url_list(Year : int): 
    '''Go to the baseball reference batting page for a given year and collect the url for the individual players'''
    player_links = [ ]
    batting_url = "https://www.baseball-reference.com/leagues/majors/" + str(Year) + "-standard-batting.shtml" 

    response = session.get(batting_url)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")

    table = soup.find_all("table")[1] #this is the players standard batting table, tried it but didnt work with table id. 
#
    if table: 
        rows = table.find_all("tr")
        for row in rows[1:]: 
            #print(row)
            player_link = row.find("a")
            b_pa_cell = row.find("td", {"data-stat": "b_pa"})
            #print(b_pa_cell) 
            
            if player_link and b_pa_cell:
                b_pa_value = int(b_pa_cell.get_text().strip()) 
                if b_pa_value > 30:  #Filter our players who had less than 15 plate appearances at bat. 
                    player_links.append("https://www.baseball-reference.com" + player_link['href'])
            else:
                print(f"Could not find URL")
        return player_links

    else: print(f"Could not find table")

    return None 


def get_minor_league_url(player_url): 
    
    response = session.get(player_url)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")
    # Findin player's minor league stats

#    search_strings = ["Minor & Fall Lg Stats", "Minor Lg Stats", "Minor & Winter Lg Stats" , "Minor, Winter & Fall Lg Stats" , "Minor, Fall & Winter Lg Stats"]
#    player_link = soup.find('a', string=lambda text: text and any(s in text for s in search_strings))

    player_link = soup.find('a', string = re.compile('Lg Stats'))

    
    #print( player_link) 
    #print("player_link : " , player_link)
    
    
    if player_link:
       return "https://www.baseball-reference.com" + player_link['href']
    else: 
        print("Error: Could not find minor league player link")
    return None


def get_player_statistics(minor_league_url):
    response = session.get(minor_league_url)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")
    name = soup.find("h1").find("span").text
    position = soup.find("p").text.strip() 

    #print(name, position)

    table = soup.find("table", {"id": "standard_batting"})
    
    if table:
        rows = table.find_all("tr")
        headers = [header.text.strip() for header in rows[0].find_all("th")]
        #print(headers)
        data = []
        for row in rows[1:]:
            cells = row.find_all(["th", "td"])
            row_data = {headers[i]: cell.text.strip() for i, cell in enumerate(cells)}
            #print(row_data)
            data.append(row_data)
        return headers, data, name, position
        
    else:
        print("Statistics table not found for:" + player_url)
        return None, None , None , None 
    


def get_data(Year : int):
    #player_names = ["Juan Soto", "Mike Trout", "Francisco Lindor"]  # List of player names
    all_player_data = []

    filename = f"batting_stats_{Year}.csv"
    player_url_list = get_player_url_list(Year = Year)    

    
    if player_url_list:

        for player_url in player_url_list:
                try:
                    print("Processing " + player_url)
                    minor_league_url  = get_minor_league_url(player_url)
                    #print(minor_league_url)
                    headers, data, player_name, position = get_player_statistics(minor_league_url = minor_league_url)
                    if data:
                        all_player_data.append((player_name, position, headers, data))
                        print(f"Data for {player_name} appended.")
                    else:
                        print(f"Error extracting player data ")
                except:
                    print("Error, skipping player")
                    pass
    # Save to CSV
        
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Player Name'] + headers)  # Adjust as needed, can add position here but maybe for later. 
        
        for player_name, position, headers, data in all_player_data:
            for row in data:
                    row_data = [row.get(header, "") for header in headers[:]]  # Use get to handle missing keys
                    writer.writerow([player_name]+ row_data) #Trouble adding position 

    print(f"Data saved to {filename}.")

    
def main():
    parser = argparse.ArgumentParser(description='Process baseball player statistics for a specific year.')
    parser.add_argument('year', type=int, help='The year to fetch data for')
    args = parser.parse_args()
    get_data(args.year)

if __name__ == "__main__":
    main()
