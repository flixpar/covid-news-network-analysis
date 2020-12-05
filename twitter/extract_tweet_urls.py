import json
import requests

with open("data/tweet_linkurls_raw.json", "w") as f:
	tweet_links_raw = json.load(f)

tweet_links_expanded = {}
for i,(tweetInd,links_raw) in tqdm.tqdm(tweet_links_raw.items(), total=len(tweet_links_raw)):
	links_expanded = []
	for url_raw in links_raw:
		try:
			resp = requests.get(url, timeout=5.0)
			if resp.ok:
				links_expanded.append(resp.url)
		except:
			continue
	tweet_links_expanded[tweetInd] = links_expanded

	if len(tweet_links_expanded) % 250 == 0:
		with open("data/tweet_linkurls_expanded.json", "w") as f:
			json.dump(tweet_links_expanded, f)

with open("data/tweet_linkurls_expanded.json", "w") as f:
	json.dump(tweet_links_expanded, f)
