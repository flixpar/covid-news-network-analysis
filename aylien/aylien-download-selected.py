import json
import requests
from bs4 import BeautifulSoup
import pandas as pd
import tqdm

with open("data/aylien_selected_articles_ind.json", "r") as f:
	selected_articles_ind = json.load(f)
selected_articles_ind = set(selected_articles_ind)

articles = []
with open("largedata/aylien_covid_news_data.jsonl", "r") as f:
	for i,line in tqdm.tqdm(enumerate(f)):
		if i not in selected_articles_ind:
			continue

		line = json.loads(line)

		url = line["links"]["permalink"]
		try:
			page = requests.get(url, timeout=5.0)
		except:
			continue

		if not page.ok:
			continue

		soup = BeautifulSoup(page.content, "html.parser")

		links = soup.find_all("a")
		links = [l["href"] for l in links if "href" in l.attrs and l["href"]]
		links = [l for l in links if (l[0] != "#" and l[0] != "/")]

		domain = line["source"]["domain"]
		links = [l for l in links if domain not in l]

		keywords = line["keywords"] if line["keywords"] is not None else []
		hashtags = line["hashtags"] if line["hashtags"] is not None else []

		shares_fb = line["social_shares_count"]["facebook"][0]["count"] if line["social_shares_count"]["facebook"] else 0
		shares_reddit = line["social_shares_count"]["reddit"][0]["count"] if line["social_shares_count"]["reddit"] else 0

		content = line["body"].replace("\n", " ").replace("\r", " ")

		article = {
			"title": line["title"],
			"date": line["published_at"],
			"url": url,
			"domain": domain,
			"links": links,
			"shares_facebook": shares_fb,
			"shares_reddit": shares_reddit,
			"keywords": keywords,
			"hashtags": hashtags,
			"content": content,
		}
		articles.append(article)

		if len(articles) % 500 == 0:
			articles_df = pd.DataFrame(articles)
			articles_df.to_csv("data/aylien_covid_articles_content_selected.csv", index=False)

articles_df = pd.DataFrame(articles)
articles_df.to_csv("data/aylien_covid_articles_content_selected.csv", index=False)
