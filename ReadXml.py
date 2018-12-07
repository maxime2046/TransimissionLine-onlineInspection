# coding=utf-8
import xml.etree.ElementTree as ET
from lxml import etree
import os
import sys

ENCODE_METHOD = 'utf-8'

def traverseXml(element):
    #print (len(element))
    if len(element)>0:
        for child in element:
            print (child.tag, "----", child.attrib)
            
            traverseXml(child)


#def readShape(self,label,bndbox,difficult):
def readShape(bndbox):
    xmin = int(bndbox.find('xmin').text)
    ymin = int(bndbox.find('ymin').text)
    xmax = int(bndbox.find('xmax').text)
    ymax = int(bndbox.find('ymax').text)
    points = [xmin,ymin,xmax,ymax]
    return points
    #points = [(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)]
    #self.shapes.append((label, points, None, None, difficult))

def getSize(size):
    width = int(size.find('width').text)
    heigt = int(size.find('height').text)
    depth = int(size.find('depth').text)
    points = [width,heigt,depth]
    return points


if __name__ == "__main__":
    #xmlFilePath = os.path.abspath('F:/1.xml')
    xmlFilePath = 'F:\\12.xml'

    #assert self.filepath.endswith(XML_EXT), "Unsupport file format"
    parser = etree.XMLParser(encoding=ENCODE_METHOD)

    xmltree = ET.parse(xmlFilePath,parser = parser).getroot()

    for result_iter in xmltree.findall('result'):
        filename = result_iter.get('filename')
        print ('filename is :',filename)
        flags = result_iter.get('flags')
        print ('flag is :',flags)
        size_iter = result_iter.find('size')
        size = getSize(size_iter)
        print ('image size is',size)

        #label = size.find('name').text
        for object_iter in result_iter.findall('object'):
            label = object_iter.get('name')
            print ('object name is :',label)
            bndbox = object_iter.find("bndbox")            
            object_location = readShape(bndbox)
            print ('object_location is:',object_location)
'''
        # Add chris
        #difficult = False
        #if object_iter.find('difficult') is not None:
            #difficult = bool(int(object_iter.find('difficult').text))
       # self.addShape(label, bndbox, difficult)
    #return True
    #for name in root.findall('result'):
        
    
    #����root����һ��
    for child in root:
        print ("����root����һ��", root.tag, "----", root.attrib)

        #print child.tag
        a= child.attrib
        for info in child:
            print ("����info����һ��", info.tag, "----", info.attrib)
            #b = info.attrib

            #print ("����root����һ��", info.tag, "----", info.attrib)


    #ʹ���±����
    print (root[0].text)
    print (root[1][1][0].text)

    traverseXml(root)
    print (20 * "*")

    #���ݱ�ǩ������root�µ����б�ǩ
    captionList = root.findall("result")  #�ڵ�ǰָ��Ŀ¼�±���
    print (len(captionList))
    for caption in captionList:
        print (caption.tag, "----", caption.attrib, "----", caption.text)

    #�޸�xml�ļ�����passwd�޸�Ϊ999999
    #login = root.find("login")
   # passwdValue = login.get("passwd")
    #print ("not modify passwd:", passwdValue)
    #login.set("passwd", "999999")   #�޸ģ����޸�text���ʾΪlogin.text
    #print ("modify passwd:", login.get("passwd"))
 '''