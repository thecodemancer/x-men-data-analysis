import requests
from bs4 import BeautifulSoup
import pandas as pd

# --- Configuration ---
WIKIPEDIA_URL = "https://en.wikipedia.org/wiki/List_of_X-Men_(TV_series)_episodes"
TABLE_CLASS = "wikitable plainrowheaders wikiepisodetable"  # Class of the tables
OUTPUT_CSV = "xmen_episodes.csv"

# --- Web Scraping ---
def scrape_episode_data(url, table_class):
    """Scrapes episode data from multiple Wikipedia tables.

    Args:
        url (str): The URL of the Wikipedia page.
        table_class (str): The class of the tables on the page.

    Returns:
        list: A list of dictionaries containing episode data.
    """

    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")
    episode_tables = soup.find_all("table", {"class": table_class})

    if not episode_tables:
        raise ValueError(f"No tables with class '{table_class}' found on the page.")

    all_episodes = []
    for episode_table in episode_tables:
        # Extract table headers
        headers = [th.text.strip() for th in episode_table.find("tr").find_all("th")]

        # Extract episode data rows
        episodes = []
        for row in episode_table.find_all("tr")[1:]:  # Skip header row
            episode_data = {}
            for i, cell in enumerate(row.find_all(["td", "th"])):
                header = headers[i]
                episode_data[header] = cell.text.strip()

            # Get episode summary from the next row (paragraph)
            summary_row = row.find_next_sibling("tr")
            if summary_row:
                summary_paragraph = summary_row.find("td", {"colspan": "7"}).find("p")
                episode_data["Summary"] = summary_paragraph.text.strip() if summary_paragraph else ""

            episodes.append(episode_data)

        all_episodes.extend(episodes)  # Add episodes from this table to the main list

    return all_episodes

# --- Data Processing --- (You'll add more logic here)
def clean_episode_data(episodes):
    """Cleans and formats the scraped episode data.

    Args:
        episodes (list): List of dictionaries containing episode data.

    Returns:
        pandas.DataFrame: A DataFrame with the cleaned episode data.
    """

    df = pd.DataFrame(episodes)

    # Data cleaning and formatting (example)
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
