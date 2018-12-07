# coding=utf-8

import os
import shutil
import xml.etree.ElementTree as ET

def take_jpg(xml_path,jpg_path,take_jpg_path):

	for xml_file_name in os.listdir(xml_path):
		xml_file = xml_path + xml_file_name
		xml_name = xml_file_name.split('.') 
		only_name_xml = xml_name[0]
		for jpg_file_name in os.listdir(jpg_path):
			jpg_xml = jpg_file_name.split('.')
			only_name_jpg = jpg_xml[0]
			if only_name_jpg == only_name_xml:
				old_path = jpg_path
				new_path = take_jpg_path
				file_name = only_name_jpg +'.JPG'
				shutil.copyfile(os.path.join(old_path,file_name),os.path.join(new_path,file_name))
	return 0

	
def take_want_bbox_xml(xml_path,need_xml_path):

	for xml_file_name in os.listdir(xml_path):
		xml_file = xml_path + xml_file_name
		print(xml_file)
		tree = ET.parse(xml_file)
		root = tree.getroot()
		index = False
		for member in root.findall('object'):
			if member[0].text == 'line_insulator':
				index = True
		
		if index == True:
			shutil.copyfile(xml_file,os.path.join(need_xml_path,xml_file_name))
	return 0

	
def del_object(xml_path,new_xml_path):

	for xml_file_name in os.listdir(xml_path):
		xml_file_ = xml_path + xml_file_name
		
		#print(xml_file_)
		tree = ET.parse(xml_file_)
		root = tree.getroot()
		for member in root.findall('object'):
			if member[0].text == 'tower_top':
				root.remove(member)
			if member[0].text == 'tower_line':
				root.remove(member)	
			
		tree.write(new_xml_path + xml_file_name)	
	
	return 0
	
	
def main():
	xml_path = 'F:/1/'		
	#xml_path = 'E:/Image/'		

	#jpg_path = 'D:/wuhandata/dachicun/jpg/'				
	#take_jpg_path = 'C:/Users/admin/Desktop/int/xml/'	
	
	new_xml_path = 'E:/' 
	
	

	#take_jpg(xml_path,jpg_path,take_jpg_path)
	
	
	# need_xml_path = new_xml_path
	 #take_want_bbox_xml(xml_path,need_xml_path)
	
	
	del_object(xml_path,new_xml_path)
	
main()