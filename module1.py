#!/usr/bin/python
# -*- coding: UTF-8 -*-
import unittest
import os
import time

from xml.dom.minidom import parse
import xml.dom.minidom

#??ȡxml?ļ???ַ
#path = os.path.abspath('.') 
#data_path = os.path.join(path,'features/data/data.xml') #??ȡxml?ļ???ַ

#DOMTree = xml.dom.minidom.parse(data_path) 
#data = DOMTree.documentElement

def get_attrvalue(node, attrname):
     return node.getAttribute(attrname)

# style = xml?еĴ??? ; typename = ϸ??????; typevalue = ϸ?????Ե?ֵ; valuename = xml?ļ?????Ҫ??ȡ??ֵ??tag;
def get_data_vaule(style, typename, typevalue, valuename):
    nodelist = data.getElementsByTagName(style)

    for node in nodelist: 
        if typevalue == node.getAttribute(typename):
            node_name = node.getElementsByTagName(valuename)
            value = node_name[0].childNodes[0].nodeValue
            print value
            return value
    return 



if __name__ == "__main__":
    #xmlFilePath = os.path.abspath('F:/1.xml')
    data_path = 'F:\\12.xml'
    DOMTree = xml.dom.minidom.parse(data_path) 
    data = DOMTree.documentElement
    nodelist = data.getElementsByTagName('result')

    for node in nodelist: 
        filename = node.getElementsByTagName('filename')[0]
        filename 
        print filename
       # object = node.getElementsByTagName('object')

        #if typevalue == node.getAttribute(typename):
           # node_name = node.getElementsByTagName(valuename)
            #value = node_name[0].childNodes[0].nodeValue

    #assert self.filepath.endswith(XML_EXT), "Unsupport file format"
'''
    parser = etree.XMLParser(encoding=ENCODE_METHOD)

    xmltree = ET.parse(xmlFilePath,parser = parser).getroot()

    for result_iter in xmltree.findall('result'):
        filename = result_iter.get('filename').text
        print ('filename is :',filename)
        flags = result_iter.get('flags')
        print ('flag is :',flags)
        size_iter = result_iter.find('size')
        size = getSize(size_iter)
        print ('image size is',size)

        #label = size.find('name').text
        for object_iter in result_iter.findall('object'):
            bndbox = object_iter.find("bndbox")
            label = object_iter.find('name')[0].text
            print ('object name is :',label)
            object_location = readShape(bndbox)
            print ('object_location is:',object_location)
'''