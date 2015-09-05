from urllib2 import HTTPError
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from django.http import HttpResponse
from StringIO import StringIO
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser

from rest_framework.parsers import JSONParser
from serializers import DepartmentSerializer, TeacherSerializer, NewSerializer
from models import Department, Teacher

from django.shortcuts import render
from lxml import html, etree
from news_retriever import NewsRetriever

import re, mechanize
import HTMLParser
import requests
import codecs
# Create your views here.

class JSONResponse(HttpResponse):
	"""
	An HttpResponse that renders its content into JSON.
	"""
	def __init__(self, data, **kwargs):
		content = JSONRenderer().render(data)
		kwargs['content_type'] = 'application/json'
		super(JSONResponse, self).__init__(content, **kwargs)


def index(request):
	#departments=get_departments()
	#context = {'departments_list': departments}
	context= {}
	return render(request, 'taller01app/index.html', context)



@csrf_exempt
@api_view(['GET', 'POST'])
def show_teachers_list(request):
	if request.method == 'POST':
		json= request.data['department']
		json= json.encode('utf-8')
		stream = StringIO(json)
		data = JSONParser().parse(stream)
		serializer = DepartmentSerializer(data=data)
		if serializer.is_valid():
			d = serializer.save()
			teachers= get_teachers(d)
			context = {'department': d, 'teachers_list': teachers}
			return render(request, 'taller01app/teachers_list.html', context)
		else: 
			return HttpResponse('Hellllooooo')

def show_teachers_main(request):
	departments=get_departments()
	context = {'departments_list': departments}
	return render(request, 'taller01app/teachers_main.html', context)

def get_departments():
	departaments_url = 'http://www.uniandes.edu.co/institucional/facultades/listado-de-departamentos'
	departments=[]
	try:
		br = mechanize.Browser()
		br.open(departaments_url)
		root = html.fromstring(br.response().read())
		depts = root.xpath('//table[@class="contentpaneopen"][2]//ul/li/a')
		
		for dept in depts:
			d = Department(name=dept.text, url=dept.get("href"))
			departments.append(d)
	except HTTPError:
		print "Site Not Available"
	return departments


"""
List all departments
"""
def list_departments(request):
    
    if request.method == 'GET' or request.method == 'POST':
		departments=get_departments()
		serializer = DepartmentSerializer(departments, many=True)
		return JSONResponse(serializer.data)

@csrf_exempt
@api_view(['GET', 'POST'])
def list_teachers(request):
	if request.method == 'POST':
		json= request.data['department']
		stream = StringIO(json)
		data = JSONParser().parse(stream)
		serializer = DepartmentSerializer(data=data)
		if serializer.is_valid():
			d = serializer.save()
			teachers= get_teachers(d)				
			serializer = TeacherSerializer(teachers, many=True)
			return JSONResponse(serializer.data)

"""
List all departments
"""
def retrieve_departments(request):
    
    if request.method == 'GET' or request.method == 'POST':
		departaments_url = 'http://www.uniandes.edu.co/institucional/facultades/listado-de-departamentos'
		br = mechanize.Browser()
		br.open(departaments_url)
		root = html.fromstring(br.response().read())
		depts = root.xpath('//table[@class="contentpaneopen"][2]//ul/li/a')
		departments=[]
		for dept in depts:
			d = Department(name=dept.text, url=dept.get("href"))
			departments.append(d)
		serializer = DepartmentSerializer(departments, many=True)
		return JSONResponse(serializer.data)


def decodeEmail(node):

	vars_l= node.text.split('var ')
	temp = None
	if(len(vars_l)==4):
		temp= node.text.split('var ')[3].split('document')[0]
	elif(len(vars_l)==5):
		temp= node.text.split('var ')[3]
	elif(len(vars_l)==6):
		temp= node.text.split('var ')[5]
		
	if(temp != None):
		lines= temp.split('\n') 
		line0= lines[0][0:-1]
		line1= lines[1][0:-1]
		line0= line0.split(' = ', 1)[1]
		line1= line1.split(' + ', 1)[1]
		temp = line0 + ' + ' +line1		
		temp= eval(temp)
		
		h = HTMLParser.HTMLParser()
		mail= h.unescape(temp)
		return mail
	else:
		return ""


def get_teachers(department):
	patternG00= ["Civil"]
	patternG01= ["Matem"]
	patternG02= ["Mec"]
	patternG03= ["Ciencias Bio", "Electr", "Industr"]
	patternG04= ["Arte"]
	patternG05= ["Arquitectura", "Dise" ]
	patternG06= ["Ceper"]
	patternG07= ["Musica"]
	patternG08= ["Humanidades"]
	patternG09= ["ingquimica"]
	patternG10= ["quimica"]

	d= department
	
	if patternG05[0	] in d.name:
		d.url= d.url.split('/scripts/')[0]
	
	br = mechanize.Browser()


	br.open(d.url)
	teachers_links = list(br.links(url_regex = "profesores" )) + list(br.links(text_regex = "profesores" ));	
	unique_teachers_url={}
	for link in teachers_links:
		if link.url not in unique_teachers_url and link.url :
			unique_teachers_url[link.url]= link
	teachers_links= unique_teachers_url.keys();

	print teachers_links

	teachers=[]	

	for link in teachers_links:
		if patternG06[0] in d.name:
			print "CEPER"
			br.follow_link(unique_teachers_url[link]);			
			root = html.fromstring(br.response().read())
			teachers_urls = root.xpath("//a[@class='contentpagetitle_galeria']");
			print teachers_urls
			for u in teachers_urls:
				try:
					u.get("href")
					url_be= 'http://ceper.uniandes.edu.co'+ u.get("href")
					r = requests.get(url_be)
					#print r.content;
					root = html.fromstring(r.content)
					name=""
					email=""
					rangekind=""
					extension=""
					webpage= url_be

					name = root.xpath("//a[@class='contentpagetitle_galeria']")[0].text
					mail_e = root.xpath("//span[@class='botonredes']/script")
					
					email= decodeEmail(mail_e[0])

					t= Teacher(name= name, email=email, rangekind= rangekind, extension=extension, webpage= webpage)
					teachers.append(t)
				except Exception:
					print u
					print "SITE NOT AVAILABLE"

		elif patternG08[0] in d.name:
			print "Humanidades"
			br.follow_link(unique_teachers_url[link]);			
			root = html.fromstring(br.response().read())
			teachers_divs = root.xpath("//div[contains(@class, 'item column-')]")	
			for t_div in teachers_divs:
				name=""
				email=""
				rangekind=""
				extension=""
				webpage=""

				name_e = t_div.xpath("./h2/a")[0]
				name = name_e.text
				webpage= d.url[0:-1]+ name_e.get("href")
				rangekind_p = t_div.xpath("./p")
				rangekind = rangekind_p[len(rangekind_p) -1].text


				email_sc= t_div.xpath(".//script")[0]
				email = decodeEmail(email_sc)

				t= Teacher(name= name, email=email, rangekind= rangekind, extension=extension, webpage=webpage)
				teachers.append(t)

		### Pattern URL: (/index.php/profesores)
		elif "/index.php/profesores" in link:
			print "Pattern01"
			br.follow_link(unique_teachers_url[link]);
			root = html.fromstring(br.response().read())
			teachers_e = root.xpath("//div[@class='cover boxcaption']")
			print len(teachers_e)										
			for t_e in teachers_e:		
				name=""
				email=""
				rangekind=""
				extension=""
				webpage=""
				n= t_e.xpath('.//b')
				l= t_e.xpath('.//a')
				


				name= n[0].text
				email=l[len(l)-1].text.replace("\r","").replace("\n","")
				
				webpage = l[0].get("href")
				if(not "http://" in webpage):
					webpage=d.url[0:-1] + webpage
				rangekind=t_e[1][0].text						
				dirty_data = etree.tostring(t_e[1])						
				print dirty_data
				matching =  re.search('(\d{4})',dirty_data)
				if matching is not  None:
					extension= matching.group(0)
				t= Teacher(name= name, email=email, rangekind= rangekind, extension=extension, webpage = webpage)
				teachers.append(t)


		## PATTERN URL 						
		elif "personal/profesores-de-" in link:
			print link
			try:
				br.follow_link(unique_teachers_url[link]);
				root = html.fromstring(br.response().read())
				teacher_e = root.xpath("//h1[@class='title']")
				if len(teacher_e)>0:
					name=""
					email=""
					rangekind=""
					extension=""
					webpage=""

					name = teacher_e[0].text.replace('\t', '').replace('\n', '')
					print name;

					ext_e = root.xpath("//td[contains(text(), ' Ext.')]")
					if(len(ext_e)>0):								
						matching =  re.search('Ext.\s(\d{4})',ext_e[0].text)
						if matching is not  None:
							extension= matching.group(1)

					web_e = root.xpath("//td[contains(text(), 'Web')]/following-sibling::td[1]/a")
					if(len(web_e)):
						webpage= web_e[0].get("href")

					mail_e = root.xpath("//td[contains(text(), 'Correo')]/following-sibling::td[1]//script")
					print "scripts"
					print len(mail_e)
					if len(mail_e)>0:								
						email= decodeEmail(mail_e[0]);
						print email
					t= Teacher(name= name, email=email, rangekind= rangekind, extension=extension, webpage=webpage)
					teachers.append(t)
			except HTTPError:
				print ""
		######## PATTERN ISIS
		elif "es/isis-descripcion/profesores" in link:					
			br.follow_link(unique_teachers_url[link]);
			root = html.fromstring(br.response().read())
			teachers_e = root.xpath("//div[@class='span8']")
			print len(teachers_e)	
			i=0									
			for t_e in teachers_e:		
				name=""
				email=""
				rangekind=""
				extension=""
				webpage=""
				c= t_e.xpath(".//h4[@class='cargo']")
				dirty_data = etree.tostring(c[0])	
				matching =  re.search(re.compile('160;(Profesor(.+))</h4>', re.UNICODE), dirty_data)
				if matching is not  None:
					rangekind= matching.group(1)

				name = t_e[0][0].text
				dirty_data = etree.tostring(t_e[2])						
				matching =  re.search('160;(\d{4})',dirty_data)
				if matching is not  None:
					extension= matching.group(1)


				mail_script_e =t_e.xpath(".//p[@class='mail']/script")
				if len(mail_script_e) >0:
					email= decodeEmail(mail_script_e[0])

				t= Teacher(name= name, email=email, rangekind= rangekind, extension=extension)
				teachers.append(t)

		## PATTERN G00				
		elif patternG00[0] in d.name:
			print "CIVIl"
			print unique_teachers_url[link];
			br.follow_link(unique_teachers_url[link]);					
			root = html.fromstring(br.response().read())
			iframe_e = root.xpath("//iframe[@id='iFrmResBusProf']")
			print iframe_e[0].get("src")
			br.follow_link(url= iframe_e[0].get("src"));
			root = html.fromstring(br.response().read())
			teachers_e = root.xpath("//div[@class='itemProfesor']")
			for t_e in teachers_e:		
				name=""
				email=""
				rangekind=""
				extension=""
				webpage=""

				name= t_e.xpath(".//p[@class='nombreProfesor']")[0].text
				email= t_e.xpath(".//p[@class='correoProfesor']")[0][0].get("href").replace('mailto:','')
				rangekind= t_e.xpath(".//p[@class='infoFacultad']")[0].text.replace('\r','').replace('\n','')
				wp_s =  t_e.xpath(".//p[@class='urlPagina']");
				if len(wp_s)>0:
					wp_s=wp_s[0][0]
					dirty_data= wp_s.get('onclick')
					print dirty_data
					
					matching =  re.search('open\(\'(.+)\'\)', dirty_data)
					if matching is not  None:
						webpage= matching.group(1)
				
				t= Teacher(name= name, email=email, rangekind= rangekind, extension=extension, webpage= webpage)
				teachers.append(t)

		## PATTERN G01				
		elif patternG01[0] in d.name:			
			br.follow_link(unique_teachers_url[link]);
			root = html.fromstring(br.response().read())
			iframe_e = root.xpath("//div[@class='contentpane']/iframe")
			if len(iframe_e)>0:
				br.follow_link(url= iframe_e[0].get("src"));
				root = html.fromstring(br.response().read())
				teachers_e = root.xpath("//div[@class='tile-parent']")

				for t_e in teachers_e:		
					name=""
					email=""
					rangekind=""
					extension=""
					extension=""
					webpage=""
					
					name= t_e[1][0].text
					dirty_data = etree.tostring(t_e[2])
			
					matching =  re.search('<br/><br/>(.+)<br/>',dirty_data)
					if matching is not  None:
						rangekind= matching.group(1)

					matching =  re.search('E-Mail:\s(.+)<br/>',dirty_data)
					if matching is not  None:
						email= matching.group(1)

					matching =  re.search('Ext.:\s(\d{4})',dirty_data)
					if matching is not  None:
						extension= matching.group(1)

					a_e= t_e[2].xpath('./a')
					if(len(a_e)>0):
						webpage= a_e[0].get("href")

					t= Teacher(name= name, email=email, rangekind= rangekind, extension=extension, webpage= webpage)
					teachers.append(t)


		## PATTERN G02				
		elif patternG02[0] in d.name:
			br.follow_link(unique_teachers_url[link]);
			root = html.fromstring(br.response().read())
			teachers_urls = root.xpath("//a[text()='+INFO']")
			for a_e in teachers_urls:	
				url_e = a_e.get('href');	
				if "uniandes" in url_e:
					name=""
					email=""
					rangekind=""
					extension=""

					r = requests.get(url_e)
					root = html.fromstring(r.content)
					name_e = root.xpath("//p[@class='nombreProfesor']")
					if len (name_e)>0:
						name = name_e[0].text		
					mail_e = root.xpath("//a[contains(@href, 'mailto:')]")
					if len (mail_e)>0:
						email = mail_e[0].get('href').replace('mailto:','')
					rk_e = root.xpath("//p[@class='infoFacultad']")
					if len (mail_e)>0:
						rangekind = rk_e[0].text

					p_e= a_e.xpath("../following-sibling::p[1]")
					dirty_data = etree.tostring(p_e[0])
					matching =  re.search('(n: |160;)(\d{4})',dirty_data)
					if matching is not  None:
						extension= matching.group(2)
					
					if not name=='':
						t= Teacher(name= name, email=email, rangekind= rangekind, extension=extension, webpage= url_e)
						teachers.append(t)

		elif patternG03[0] in d.name or patternG03[1] in d.name or patternG03[2] in d.name:
			print unique_teachers_url[link];
			br.follow_link(unique_teachers_url[link]);
			root = html.fromstring(br.response().read())
			iframe_e = root.xpath("//iframe[contains(@src, 'academia.uniandes.edu.co/WebAcademy/showFaculties')]")[0]
			aca_url=iframe_e.get("src");
			print aca_url

			from selenium import webdriver
			from selenium.webdriver.common.by import By
			from selenium.webdriver.support.ui import WebDriverWait
			from selenium.webdriver.support import expected_conditions as EC
			from selenium.common.exceptions import TimeoutException

			#browser = webdriver.Firefox()
			browser = webdriver.PhantomJS()
			#browser = webdriver.Remote(desired_capabilities={'browserName': 'htmlunit', 'javascriptEnabled': True, 'platform': 'ANY', 'version': '', 'setThrowExceptionOnScriptError': True})
			response= browser.get(aca_url)
			delay = 60 # seconds
			try:
				e= WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.ID, "x-auto-6")))
				print "Page is ready!"
				teachers_e= e.find_elements_by_xpath("//div[contains(@class, 'x-grid3-col-idInfoFacultyColumn')]")
				for t_e in teachers_e:
					name=""
					email=""
					rangekind=""
					extension=""
					extension=""
					webpage=""

					inner_html = t_e.get_attribute('innerHTML')
					matches =  list(re.finditer('</b>(.*?)<br>', inner_html))
					name= matches[1].group(1) + ' ' +  matches[0].group(1)
					email= matches[2].group(1)

					matching =  re.search(ur'n: </b>(\d{4}( - \d{4})?)<br>',inner_html)
					if matching is not  None:
						extension= matching.group(1)

					matching =  re.search(ur'<b>(Profesor(.*?))</b>',inner_html)
					if matching is not  None:
						rangekind= matching.group(1)
					if rangekind=="":
						rangekind="Pendiente por asignar"
					
					t= Teacher(name= name, email=email, rangekind= rangekind, extension=extension)
					teachers.append(t)

			except TimeoutException:
				print "Loading took too much time!"
			

		elif patternG04[0] in d.name:
			print "ARTE"
			print unique_teachers_url[link];
			br.follow_link(unique_teachers_url[link]);
			print br.response().read()
			root = html.fromstring(br.response().read())
			teachers_e = root.xpath("//div[@class='info']")
			for t_e in teachers_e:		
				if len(t_e) >0:							
					name=""
					email=""
					rangekind=""
					extension=""
					webpage=""

					name= t_e.xpath(".//a[@class='name']")[0].text
					webpage= t_e.xpath(".//a[@class='name']")[0].get("href")
					rangekind= t_e.xpath(".//p[@class='titulo']")[0].text
					email= t_e.xpath(".//a[@class='mail']")[0].text
					

					t= Teacher(name= name, email=email, rangekind= rangekind, extension=extension, webpage=webpage)
					teachers.append(t)

		elif patternG05[0] in d.name or patternG05[1] in d.name:
			print "ARQUITECTURA O DISE"
			print unique_teachers_url[link];
			br.follow_link(unique_teachers_url[link]);			
			root = html.fromstring(br.response().read())
			teachers_ranges = root.xpath("//article/div")
			for tr_e in teachers_ranges:
				rk_e = tr_e.xpath("./h2")[0]
				rangekind=""
				if len(rk_e.xpath("./a"))>0:
					rangekind=rk_e.xpath("./a")[0].text
				else:
					rangekind=rk_e.text
				teachers_urls = tr_e.xpath(".//a[@class='fancybox-iframe']/@href")
				br2 = mechanize.Browser()
				for u in teachers_urls:
					print u
					print "##########################################"
					try:									
						br2.open(u)							
						root = html.fromstring(br2.response().read())
						div_e = root.xpath("//div[@id='right']")[0];
						name=""
						email=""
						
						extension=""
						webpage=u


						name= div_e.xpath("./h1")[0].text
						email= div_e.xpath("./p/a")[0].text
						if not ('@' in email or 'at' in email):
							email=""

						t= Teacher(name= name, email=email, rangekind= rangekind, extension=extension, webpage=webpage)
						teachers.append(t)
					except HTTPError:
						print "Site Not Available: " + u
					except Exception:
						print "Site Not: " + u

	if len(teachers_links)==0 and patternG07[0] in d.name:
		url_base="http://musica.uniandes.edu.co/index.php?option=content&task=category&sectionid=20&id=129&Itemid=141"
		print "MUSICA"
		r = requests.get(url_base)
		print "MUSICA"
		root = html.fromstring(r.content)
		teachers_urls = root.xpath("//li/p/a/@href");
		for u in  teachers_urls:			
			r2 = requests.get(u)			
			root = html.fromstring(r2.content)
			name=""
			email=""
			rangekind=""
			extension=""
			webpage= u

			name_e= root.xpath("//div[@class='componentheading']")
			if len(name_e)>0:
				name= name_e[0].text
			else:
				name_e= root.xpath("//span[@class='pathway']")
				if len(name_e)>0:
					dirty_data = etree.tostring( name_e[0])	
					data= re.split("<|>", dirty_data)		
					name = data[len(data)-3]
			rks_e = root.xpath("//p[@align='right']/strong")
			if rks_e[0].text == None:
				dirty_data = etree.tostring(rks_e[0])
				matching =  re.search('align="right"/>(.+)<br/>',dirty_data)
				if matching is not  None:
					rangekind= matching.group(1)
			else:
				rangekind=rks_e[0].text

			email_e = root.xpath("//a/strong/font[@color='#3399ff']")
			email=email_e[0].text
			t= Teacher(name= name, email=email, rangekind= rangekind, extension=extension, webpage=webpage)
			teachers.append(t)
	elif len(teachers_links)==0 and patternG10[0] in d.url:
		print "QUIMICA"
		print d.url
		r = requests.get(d.url)		
		root = html.fromstring(r.content)
		sc_e= root.xpath("//script")
		url_b =sc_e[0].text.split('"')[1];
		r = requests.get(url_b)
		root = html.fromstring(r.content)
		a_es= root.xpath("//span[text()='Profesores']/../following-sibling::div[1]//li/a")
		print a_es
		for a_e in a_es:
			n_url = url_b[0:-1] + a_e.get("href")
			print n_url
			r = requests.get(n_url)		
			root = html.fromstring(r.content)
			names_e= root.xpath("//tbody/tr/td[2]//strong[contains(text(), ' ')]"
				+"|//tbody/tr/td[2]//p[contains(text(), ' ')]"
				+"|//div[@class='item-page']//p/strong[contains(text(), ' ')]"				)
			for e_e in names_e:
				name=""
				email=""
				rangekind=""
				extension=""
				webpage= ""
				
				name= e_e.text

				trinfo = e_e.xpath("../../../following-sibling::tr[1]")
				if len(trinfo)>0:					
					trinfo= trinfo[0].xpath(".//td/p")
					if len(trinfo)>0:
						rangekind= trinfo[0].text
						
						email = decodeEmail(trinfo[0].xpath("./following-sibling::p[1]/script")[0])

						dirty_data= trinfo[0].xpath("./following-sibling::p[2]")[0].text
						matching =  re.search('n: (\d{4})',dirty_data)
						if matching is not  None:
							extension= matching.group(1)

						wp_e= trinfo[len(trinfo)-1]
						webpage=  wp_e[0].get("href");
						if not "uniandes" in webpage:
							webpage= url_b+ webpage		

				else:					
					trinfo = e_e.xpath("../../following-sibling::tr[1]")
					if len(trinfo)>0:
						trinfo= trinfo[0].xpath(".//td/p")
						rangekind= trinfo[0].text	

						sc_e =trinfo[0].xpath("./following-sibling::p[1]/script")
						if len(sc_e)>0:
							email = decodeEmail(sc_e[0])
						else:
							sc_e =trinfo[0].xpath("./following-sibling::p[2]/script")
							if len(sc_e)>0:
								email = decodeEmail(sc_e[0])

						wp_e= trinfo[len(trinfo)-1]
						webpage=  wp_e[0].get("href");
						if not "uniandes" in webpage:
							webpage= url_b+ webpage
						
						dirty_data= trinfo[2].text
						matching =  re.search('n: (\d{4})',dirty_data)
						if matching is not  None:
							extension= matching.group(1)
						else:
							dirty_data= trinfo[3].text
							matching =  re.search('n: (\d{4})',dirty_data)
							if matching is not  None:
								extension= matching.group(1)
					else:
						trinfo = e_e.xpath("../following-sibling::p[2]")
						if len(trinfo)>0 :
							rangekind= trinfo[0].text
							email = decodeEmail(trinfo[0].xpath("./following-sibling::p[1]/script")[0])
							dirty_data= trinfo[0].xpath("./following-sibling::p[2]")[0].text
							matching =  re.search('n: (\d{4})',dirty_data)
							if matching is not  None:
								extension= matching.group(1)		


							wp_e= trinfo[0].xpath("./following-sibling::p[3]")							
							if len(wp_e)>0:
								if len(wp_e[0])>0:
									webpage=  wp_e[0][0].get("href")
									if not "uniandes" in webpage:
										webpage= url_b+ webpage				
				t= Teacher(name= name, email=email, rangekind= rangekind, extension=extension, webpage=webpage)
				teachers.append(t)
			

	elif patternG09[0] in d.url:
		print "INQ QUIMICA"
		url_base="https://ingquimica.uniandes.edu.co/home/gente"
		r = requests.get(url_base)
		root = html.fromstring(r.content)
		p_e = root.xpath("//div[@class='dt_detail_block']")[0];
		p_e = p_e.xpath(".//td/p")
		for ttt in p_e:
			name=""
			email=""
			rangekind=""
			extension=""
			webpage= ""

			name_e =ttt[0].xpath(".//a")
			name_e = name_e[len(name_e) -1]
			name= name_e.text

			webpage= name_e.get("href")

			dirty_data = etree.tostring(ttt)
			
			matching =  re.search('(Profesor(.+?))(<br|</strong>|</span>)',dirty_data)
			if matching is not  None:
				rangekind= matching.group(1)

			ssc_e =ttt.xpath(".//script")
			if len(ssc_e)>0:
				email = decodeEmail(ssc_e[0])
			
			t= Teacher(name= name, email=email, rangekind= rangekind, extension=extension, webpage=webpage)
			teachers.append(t)
	return teachers

def show_news_main(request):
	context = {}
	return render(request, 'taller01app/news_main.html', context)

def show_info(request):
	context = {}
	return render(request, 'taller01app/info_main.html', context)


def list_all_news(request):
	news = NewsRetriever().get_all_news()
	serializer = NewSerializer(news, many=True)
	return JSONResponse(serializer.data)

@csrf_exempt
@api_view(['GET', 'POST'])
def find_news(request):
	if request.method == 'POST':
		method= request.data['method']
		search_text= request.data['search_text']
		not_in= request.data['not_in'] == 'true'
		news = NewsRetriever().find_news(method, search_text, not_in)
		serializer = NewSerializer(news, many=True)
		return JSONResponse(serializer.data)

@csrf_exempt
@api_view(['GET', 'POST'])
def show_filtered_news(request):
	if request.method == 'POST':
		method= request.data['method']
		search_text= request.data['search_text']
		not_in= request.data['not_in'] == 'true'
		info = 'all' if method =='xquery' else 'title'
		header =''
		if method=='xquery':
			header="Filtrado con XQuery"
		elif method=='regexp':
			header="Filtrado con RegExp"

		news = NewsRetriever().find_news(method, search_text, not_in)
		context = {'news_list': news, 'info': info, 'header': header}
		return render(request, 'taller01app/news_list.html', context)

def show_all_news(request):
	news = NewsRetriever().get_all_news()
	context = {'news_list': news, 'info': 'title', 'header':'Todas las noticias' }
	return render(request, 'taller01app/news_list.html', context)