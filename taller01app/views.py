from urllib2 import HTTPError
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from django.http import HttpResponse
from StringIO import StringIO
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser

from rest_framework.parsers import JSONParser
from serializers import DepartmentSerializer, TeacherSerializer
from models import Department, Teacher


from lxml import html, etree
import re, mechanize
import HTMLParser

# Create your views here.

class JSONResponse(HttpResponse):
	"""
	An HttpResponse that renders its content into JSON.
	"""
	def __init__(self, data, **kwargs):
		content = JSONRenderer().render(data)
		kwargs['content_type'] = 'application/json'
		super(JSONResponse, self).__init__(content, **kwargs)


"""
List all departments
"""
def list_departments(request):
    
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
			br = mechanize.Browser()
			br.open(d.url)
			teachers_links = list(br.links(url_regex = "profesores" )) + list(br.links(text_regex = "profesores" ));	
			unique_teachers_url={}
			for link in teachers_links:
				if link.url not in unique_teachers_url and link.url :
					unique_teachers_url[link.url]= link
			teachers_links= unique_teachers_url.keys();
			teachers=[]
			patternG00= ["Civil"]
			patternG01= ["Matem"]
			patternG02= ["Mec"]
			patternG03= ["Ciencias Bio"]
			patternG04= ["Arte"]

			for link in teachers_links:
				### Pattern URL: (/index.php/profesores)
				if "/index.php/profesores" in link:
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
						
						n= t_e.xpath('.//b')
						l= t_e.xpath('.//a')

						name= n[0].text
						email=l[len(l)-1].text.replace("\r","").replace("\n","")
						
						rangekind=t_e[1][0].text						
						dirty_data = etree.tostring(t_e[1])						
						print dirty_data
						matching =  re.search('(\d{4})',dirty_data)
						if matching is not  None:
							extension= matching.group(0)
						t= Teacher(name= name, email=email, rangekind= rangekind, extension=extension)
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
					print unique_teachers_url[link];
					br.follow_link(unique_teachers_url[link]);
					print link
					#print br.response().read()
					root = html.fromstring(br.response().read())
					iframe_e = root.xpath("//div[@class='contentpane']/iframe")
					if len(iframe_e)>0:
						print iframe_e[0].get("src")
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
							print "%%%%%%%%%%%%%%%%%%%%%%%%%%%"
							dirty_data = etree.tostring(t_e[2])
							print dirty_data

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
					print unique_teachers_url[link];
					br.follow_link(unique_teachers_url[link]);
					root = html.fromstring(br.response().read())

					
					teachers_e = root.xpath("//article/section/p//*[@style='color: #0073a3;']")
					for t_e in teachers_e:		
						name=""
						email=""
						rangekind="PROFESOR DE PLANTA"
						extension=""

						if t_e.text != None:
							name= t_e.text
	 						print name
							t= Teacher(name= name, email=email, rangekind= rangekind, extension=extension)
							teachers.append(t)

				elif patternG03[0] in d.name:
					print unique_teachers_url[link];
					br.follow_link(unique_teachers_url[link]);
					root = html.fromstring(br.response().read())
					iframe_e = root.xpath("//iframe[contains(@src, 'academia.uniandes.edu.co/WebAcademy/showFaculties')]")[0]
					br.follow_link(url=iframe_e.get("src"));
					print br.response().read()
					root = html.fromstring(br.response().read())
					teachers_e= root.xpath("//tr")
					for t_e in teachers_e:		
						name=""
						email=""
						rangekind=""
						extension=""
						#n= t_e.xpath('.//b')
						#l= t_e.xpath('.//a')
						#name= n[0].text
						#email=l[len(l)-1].text.replace("\r","").replace("\n","")						
						#rangekind=t_e[1][0].text						
						#dirty_data = etree.tostring(t_e[1])						
						#print dirty_data
						#matching =  re.search('(\d{4})',dirty_data)
						#if matching is not  None:
						#	extension= matching.group(0)
						t= Teacher(name= name, email=email, rangekind= rangekind, extension=extension)
						teachers.append(t)
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
		
	if(temp != None):
		lines= temp.split('\n') 
		line0= lines[0][0:-1]
		line1= lines[1][0:-1]
		line0= line0.split(' = ', 1)[1]
		line1= line1.split(' + ', 1)[1]
		temp = line0 + ' + ' +line1		
		temp= eval(temp)

		print "LINDAAA"
		h = HTMLParser.HTMLParser()
		mail= h.unescape(temp)
		print "LINDA: " + mail
		return mail
	else:
		return "LLLLLL"
