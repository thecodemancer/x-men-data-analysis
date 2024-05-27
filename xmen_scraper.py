import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# --- Configuration ---
WIKIPEDIA_URL = "https://en.wikipedia.org/wiki/List_of_X-Men_(TV_series)_episodes"
TABLE_CLASS = "wikitable plainrowheaders wikiepisodetable" 
OUTPUT_CSV = "datasets/xmen_episodes.csv"

# --- Web Scraping ---
def scrape_episode_data(url, table_class):
    """Scrapes episode data from multiple Wikipedia tables, 
       handling rows with rowspan, missing cells, inconsistent headers,
       and multi-part episodes using next_sibling and previous_sibling.

    Args:
        url (str): The URL of the Wikipedia page.
        table_class (str): The class of the tables on the page.

    Returns:
        list: A list of dictionaries containing episode data.
    """

    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")
    episode_tables = soup.find_all("table", {"class": table_class}, limit=5)

    if not episode_tables:
        raise ValueError(f"No tables with class '{table_class}' found on the page.")

    all_episodes = []
    for season, episode_table in enumerate(episode_tables):    
        # Extract table headers from the first row
        headers = [th.text.strip() for th in episode_table.find_all("tr")[0].find_all("th")]

        # Find the index of the "Original air date" header
        air_date_index = headers.index("Original air date")
        
        # Find the index of the "Title" header
        title_index = headers.index("Title")
        directedby_index = headers.index("Directed by")
        writtenby_index = headers.index("Written by")
        # Extract episode data rows
        for row in episode_table.find_all("tr", class_="vevent module-episode-list-row"):
            current_episode_data = {}
            cells = row.find_all(["td", "th"])
            # Check for rowspan in the Title column
            title_rowspan = int(cells[title_index].attrs['rowspan']) if 'rowspan' in cells[title_index].attrs else 1
            # Check for rowspan in the "Directed by" column
            directedby_rowspan = int(cells[directedby_index].attrs['rowspan']) if 'rowspan' in cells[directedby_index].attrs else 1
            # Check for rowspan in the "Written by" column
            writtenby_rowspan = int(cells[writtenby_index].attrs['rowspan']) if 'rowspan' in cells[writtenby_index].attrs else 1

            current_episode_data["season"] = season+1
            # Extract data from cells
            for j, cell in enumerate(cells):
                header = headers[j]
                current_episode_data[header] = cell.text.strip()
            
            # Get episode summary
            current_episode_data["Summary"]=""
            summary_row = row.find_next_siblings("tr", {"class":'expand-child'}, limit=1)
            for summary in summary_row:
                summary_div = summary.find("div", class_="shortSummaryText")
                if summary_div:
                    current_episode_data["Summary"] = summary_div.text.strip()

            all_episodes.append(current_episode_data)

            # Handle multi-part episodes
            #for title
            if title_rowspan > 1:
                next_row = row.next_sibling
                part_cells = next_row.find_all(["td", "th"])
                
                #You cannot copy a list simply by typing list2 = list1, 
                #because: list2 will only be a reference to list1, 
                #and changes made in list1 will automatically also be made in list2.
                current_episode_data_part_2 = current_episode_data.copy()
                if len(part_cells) == 3:
                    current_episode_data_part_2["No.overall"] = part_cells[0].text.strip()
                    current_episode_data_part_2["No. inseason"] = part_cells[1].text.strip()
                    current_episode_data_part_2["Original air date"] = part_cells[2].text.strip()                    
                    all_episodes.append(current_episode_data_part_2)
                if len(part_cells) == 4:
                    current_episode_data_part_2["No.overall"] = part_cells[0].text.strip()
                    current_episode_data_part_2["No. inseason"] = part_cells[1].text.strip()
                    current_episode_data_part_2["Written by"] = part_cells[2].text.strip()                    
                    current_episode_data_part_2["Original air date"] = part_cells[3].text.strip()                    
                    all_episodes.append(current_episode_data_part_2)

            #for director
            if directedby_rowspan >= 4 and title_rowspan == 1:
                next_row = row.next_sibling
                while next_row and next_row.name == 'tr' and 'expand-child' not in next_row.get('class', []) and next_row.find_all(["td", "th"]):
                    part_cells = next_row.find_all(["td", "th"])
                    print(len(part_cells))
                    #You cannot copy a list simply by typing list2 = list1, 
                    #because: list2 will only be a reference to list1, 
                    #and changes made in list1 will automatically also be made in list2.
                    current_episode_data_part_2 = current_episode_data.copy()
                    if len(part_cells) >= 4:
                        current_episode_data_part_2["No.overall"] = part_cells[0].text.strip()
                        current_episode_data_part_2["No. inseason"] = part_cells[1].text.strip()
                        current_episode_data_part_2["Title"] = part_cells[2].text.strip()                    
                        current_episode_data_part_2["Written by"] = part_cells[3].text.strip()                    
                        current_episode_data_part_2["Original air date"] = part_cells[4].text.strip()                    
                        all_episodes.append(current_episode_data_part_2)
                    next_row = next_row.next_sibling

            if writtenby_rowspan > 1:
                next_row = row.next_sibling
                part_cells = next_row.find_all(["td", "th"])
                
                #You cannot copy a list simply by typing list2 = list1, 
                #because: list2 will only be a reference to list1, 
                #and changes made in list1 will automatically also be made in list2.
                current_episode_data_part_2 = current_episode_data.copy()
                if len(part_cells) == 2:
                    current_episode_data_part_2["No.overall"] = part_cells[0].text.strip()
                    current_episode_data_part_2["No. inseason"] = part_cells[1].text.strip()
                    all_episodes.append(current_episode_data_part_2)

    return all_episodes

# --- Data Processing ---
def clean_episode_data(episodes):
    """Cleans and formats the scraped episode data.

    Args:
        episodes (list): List of dictionaries containing episode data.

    Returns:
        pandas.DataFrame: A DataFrame with the cleaned episode data.
    """

    df = pd.DataFrame(episodes)

    # Extract date from parentheses in "Original air date" column
    df["Original air date"] = df["Original air date"].str.extract(r'\((.*?)\)')

    # Convert "Original air date" to datetime objects
    df["Original air date"] = pd.to_datetime(df["Original air date"])

    # ... (Add more cleaning and formatting as needed) ...

    return df

# --- Main Script ---
if __name__ == "__main__":
    try:
        episodes = scrape_episode_data(WIKIPEDIA_URL, TABLE_CLASS)
        df = clean_episode_data(episodes)
        df.to_csv(OUTPUT_CSV, index=False)
        print(f"Successfully scraped and saved episode data to '{OUTPUT_CSV}'")

    except Exception as e:
        print(f"An error occurred: {e}")

#Credits by @thecodemancer