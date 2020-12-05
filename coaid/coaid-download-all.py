import json
import requests
from bs4 import BeautifulSoup
import pandas as pd
import math
import tqdm
import glob
import tldextract

ignore_domains = ["twitter.com", "facebook.com", "youtube.com", ""]

def url_to_domain(url):
	domain = tldextract.extract(url)
	domain = domain.domain + "." + domain.suffix
	return domain

fns = glob.glob("largedata/CoAID/*/NewsRealCOVID-19.csv")
dfs = [pd.read_csv(fn) for fn in fns]
data = pd.concat(dfs)

articles = []
for i,line in tqdm.tqdm(data.iterrows(), total=len(data)):
	url = line.news_url
	if not isinstance(url, str):
		continue
	domain = url_to_domain(url)
	if domain in ignore_domains:
		continue

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
	links = [l for l in links if domain not in l]

	text_elems = soup.findAll("p")
	text_list = [e.text for e in text_elems]
	content = " ".join(text_list)
	content = content.replace("\n", " ").replace("\r", " ")

	date = line.publish_date
	date = date if not (isinstance(date,float) and math.isnan(date)) else ""

	article = {
		"title": line.title,
		"date": date,
		"url": url,
		"domain": domain,
		"links": links,
		"shares_facebook": -1,
		"shares_reddit": -1,
		"keywords": line.meta_keywords,
		"hashtags": [],
		"content": content,
	}
	articles.append(article)

	if len(articles) % 500 == 0:
		articles_df = pd.DataFrame(articles)
		articles_df.to_csv("data/coaid_covid_articles_content.csv", index=False)

articles_df = pd.DataFrame(articles)
articles_df.to_csv("data/coaid_covid_articles_content.csv", index=False)
