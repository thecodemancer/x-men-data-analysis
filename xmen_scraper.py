import requests
from bs4 import BeautifulSoup
import pandas as pd

# --- Configuration ---
WIKIPEDIA_URL = "https://en.wikipedia.org/wiki/List_of_X-Men_(TV_series)_episodes"
TABLE_CLASS = "wikitable plainrowheaders wikiepisodetable" 
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
        for row in episode_table.find_all("tr", class_="vevent module-episode-list-row"):
            episode_data = {}
            for i, cell in enumerate(row.find_all(["td", "th"])):
                header = headers[i]
                episode_data[header] = cell.text.strip()

            # Get episode summary (Corrected Part)
            summary_div = row.find_next_sibling("tr").find("div", class_="shortSummaryText")
            if summary_div:
                # Extract text from the summary div and remove links
                summary_text = summary_div.text.strip()
                episode_data["Summary"] = summary_text

            all_episodes.append(episode_data)

    return all_episodes

# --- Data Processing --- (Remains the same)
def clean_episode_data(episodes):
    # ... (Your data cleaning and formatting logic here) ... 
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

    return df

# --- Main Script --- (Remains the same)
if __name__ == "__main__":
    try:
        episodes = scrape_episode_data(WIKIPEDIA_URL, TABLE_CLASS)
        df = clean_episode_data(episodes)
        df.to_csv(OUTPUT_CSV, index=False)
        print(f"Successfully scraped and saved episode data to '{OUTPUT_CSV}'")

    except Exception as e:
        print(f"An error occurred: {e}")
