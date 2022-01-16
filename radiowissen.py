import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
import os

def get_infos(url):
    """Returns all infos from one podcast site."""
    if url[:18] != "https://www.br.de/":
        url = "https://www.br.de" + url
    web = requests.get(url)
    soup = BeautifulSoup(web.text, 'html.parser')
    #title
    title = soup.find("div", {"class": "episode-description"}).h2.text.strip()
    # desc
    desc = soup.find("div", {"class": "episode-description"}).p.text.strip()
    # info: author, date
    info = soup.find("div", {"class": "episode-info"})
    author = info.find_all("p")[0].text.strip().replace("VON: ", "")
    date = info.find_all("p")[1].text.strip().replace("Ausstrahlung am ", "")
    # tags
    res = soup.find("div", {"class": "list"}).text.strip().replace("\n", " ")
    tags = ','.join(res.split())
    # duration
    res = soup.find("div", {"class": "info-holder"})
    duration_min = res.text.strip().split("|")[0].strip().replace(" Min.", "")
    # title, desc, author, date, tags, duration_min
    return {"url": url, "title": title, "desc": desc, "author": author, "date": date, "tags": tags, "duration_min": duration_min} 


def get_all_urls():
    """Get all podcast urls."""
    results = []
    for page_number in tqdm(range(110), desc="Get urls"):
        url = f"https://www.br.de/mediathek/podcast/radiowissen/alle/488?page={page_number}&order=relevance"
        web = requests.get(url)
        soup = BeautifulSoup(web.text, 'html.parser')
        res_list = soup.find_all("div", {"class": "description"})
        url_title_list = [(x.find('a', href=True)['href'], x.find('h3').text.strip()) for x in res_list]
        results.extend(url_title_list)
    return results


def get_all_data():
    """Get all infos from all podcasts."""
    # Get urls
    res = get_all_urls()
    df = pd.DataFrame(res)    
        
    results = []
    for index, row in tqdm(df.iterrows(), total=df.shape[0], desc="Get data"):
        try:
            res = get_infos(row[0])
            results.append(res)
        except:
            print(index, row[0])
    return results


if __name__ == "__main__":
    res = get_all_data()
    df = pd.DataFrame(res)
    os.makedirs("data", exists_ok=True)
    df.to_csv("data/podcasts.csv", index=False)    
    print("Save to 'data/podcasts.csv'")
