from rest_framework import serializers
from taller01app.models import Department, Teacher, New

class DepartmentSerializer(serializers.ModelSerializer):
	def create(self, validated_data):
		return Department(**validated_data)
	
	class Meta:
		model = Department
		fields = ('name', 'url')

class TeacherSerializer(serializers.ModelSerializer):
	class Meta:
		model = Teacher
		fields = ('name', 'email', 'rangekind', 'extension', 'webpage', 'dependency')


class NewSerializer(serializers.ModelSerializer):
	class Meta:
		model = New
		fields = ('title', 'link', 'pubdate')