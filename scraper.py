from bs4 import BeautifulSoup
import requests
import pandas as pd

r = requests.get('https://www.imdb.com/chart/top?ref_=nv_mv_250').content

bsObj = BeautifulSoup(r, 'html.parser')

tabel = bsObj.find('tbody', attrs={'class':'lister-list'})

data = []
for tr in tabel.find_all('tr'):
    regel = {}
    for td in tr.find_all('td'):
        if 'titleColumn' in td['class']:
            
            regel['rank'] = td.contents[0].strip().replace('.', '')
            regel['titel'] = td.a.text
            print(f"Bezig met {regel['titel']}")
            regel['jaartal'] = td.span.text.replace(')', '').replace('(', '')
            regel['href'] = f"https://www.imdb.com/{td.a['href']}"

        if all([klasse in td['class'] for klasse in ['ratingColumn','imdbRating']]):
            regel['rating'] = td.text.strip()
    
    # vanaf hier gaat ik door naar de hoofdpagina van een specifieke film, en haal ik daar extra info vandaan
    r = requests.get(regel['href']).content
    bsObj = BeautifulSoup(r, 'html.parser')

    try:
        div = bsObj.find('div', attrs={'class':'plot_summary'})
    except AttributeError:
        # City lights had een extra class
        div = bsObj.find('div', attrs={'class':['plot_summary', 'minPlotHeightWithPosterAndWatchlistButton']})

    summary = div.find('div', attrs={'class':'summary_text'}).text.strip()
    regel['samenvatting'] = summary
    items = div.find_all('div', attrs={'class': 'credit_summary_item'})
    regel['director'] = items[0].text.replace('Director:','').strip()
    regel['acteurs'] = items[2].text.replace('Stars:','').replace('See full cast & crew','').replace('»','').replace('|','').strip()
    data.append(regel)

df = pd.DataFrame(data)
df.to_csv('films.csv')

