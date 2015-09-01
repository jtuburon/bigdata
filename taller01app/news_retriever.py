import requests
from lxml import html, etree
from models import New
import re
import HTMLParser
import simplexquery as sxq

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
				query_s="""for $i in //item
						where contains(lower-case($i/title), lower-case('"""+ search_text+ """'))
						return <new>{$i/title, $i/pubDate, $i/link }</new>
						"""
				import sys  
				reload(sys)  
				sys.setdefaultencoding('utf8')				
				news_list= sxq.execute_all(query_s, rss);
				for n_i in news_list:
					i = etree.fromstring(n_i)
					title = i.xpath("./title")[0]
					pubDate = i.xpath("./pubDate")[0]
					link = i.xpath("./link")[0]
					n= New(title= title.text, link= link.text, pubdate=pubDate.text)
					news.append(n)
				
				# root = etree.fromstring(rss)
				# items = root.xpath("//item[contains(./title/text(), '" + search_text + "')]")				
				# for i in items:
				# 	title = i.xpath("./title")[0]
				# 	pubDate = i.xpath("./pubDate")[0]
				# 	link = i.xpath("./link")[0]
				# 	n= New(title= title.text, link= link.text, pubdate=pubDate.text)
				# 	news.append(n)
			elif method == 'regexp':
				import sys  
				reload(sys)  
				sys.setdefaultencoding('utf8')		
				h = HTMLParser.HTMLParser()
				rss2= h.unescape(rss)
				
				print rss2						
				#pattern = r'<item>(.*?)<title>((.*)'+  search_text+ '(.*))</title>(.*?)</item>'				
				pattern = ur'<item>(.*?)</item>'				
				regex = re.compile(pattern, re.DOTALL + re.UNICODE + re.IGNORECASE)
				for match in regex.finditer(rss2):													
					item= match.group(1)	
					print """

					--->>>>>>>

					"""
					print item
					pattern = ur'<title>((.*?)'+ search_text+'(.*?))</title>'				
					regex = re.compile(pattern, re.UNICODE + re.UNICODE + re.IGNORECASE)
					matching= regex.search(item)
					if matching:
						title= matching.group(1)
						n= New(title= title)
						news.append(n)
				
		return news

	