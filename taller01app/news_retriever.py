import requests
from lxml import html, etree
from models import New
import re
import HTMLParser

class NewsRetriever():
	rss_urls= {
		"espectador": "http://feeds.elespectador.com/c/33813/f/607844/index.rss",
		"tiempo01": "http://www.eltiempo.com/contenido/mundo/rss.xml",
		"tiempo02": "http://www.eltiempo.com/contenido/deportes/rss.xml",
		"tiempo03": "http://www.eltiempo.com/contenido/tecnosfera/rss.xml"
	}

	def get_all_news(self):
		news = []
		for source in self.rss_urls.keys():
			r = requests.get(self.rss_urls[source])
			root = etree.fromstring(r.content)
			items = root.xpath("//item")			
			for i in items:
				title = i.xpath("./title")[0]
				pubDate = i.xpath("./pubDate")[0]
				link = i.xpath("./link")[0]
				n= New(title= title.text, link= link.text, pubdate=pubDate.text)
				news.append(n)
		return news

	def find_news(self, method='xquery', search_text=''):
		news=[]
		if method=='':
			method = 'xquery'

		for source in self.rss_urls.keys():
			r = requests.get(self.rss_urls[source])
			rss = r.content
			if method == 'xquery':
				root = etree.fromstring(rss)
				items = root.xpath("//item[contains(./title/text(), '" + search_text + "')]")				
				for i in items:
					title = i.xpath("./title")[0]
					pubDate = i.xpath("./pubDate")[0]
					link = i.xpath("./link")[0]
					n= New(title= title.text, link= link.text, pubdate=pubDate.text)
					news.append(n)
			elif method == 'regexp':
				rss= rss.replace('><', '>\n<')
				pattern = '<title>((.*)'+  search_text+ '(.*))</title>'
				for match in re.finditer(pattern, rss):
					h = HTMLParser.HTMLParser()
					title= h.unescape(match.group(1))
					n= New(title= title)
					news.append(n)
		return news

	