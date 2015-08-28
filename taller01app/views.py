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

			pattern2= ["Ciencias Bio"]

			for link in teachers_links:
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
				elif pattern2[0] in d.name:
					print unique_teachers_url[link];
					br.follow_link(unique_teachers_url[link]);
					print br.response().read();
					root = html.fromstring(br.response().read())
					teachers_e = root.xpath("//tr[@role='presentation']")
					print len(teachers_e)										
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
