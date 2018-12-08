# coding=utf-8
import os, argparse
import xml.dom.minidom as minidom
import numpy as np
import xml.etree.ElementTree as ET
from lxml import etree
import sys
import metrics
import cv2
import random
from xlwt import *
import xlrd
from writeExcel import write


ENCODE_METHOD = 'utf-8'

def bb_intersection_over_union(boxA, boxB):
# determine the (x, y)-coordinates of the intersection rectangle
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])
    xw = max(xB-xA,0.)
    wh = max(yB-yA,0.)
    # compute the area of intersection rectangle
    #interArea = (xB - xA + 1) * (yB - yA + 1)
    interArea = xw * wh
    boxAArea = (boxA[2] - boxA[0] + 1) * (boxA[3] - boxA[1] + 1)
    boxBArea = (boxB[2] - boxB[0] + 1) * (boxB[3] - boxB[1] + 1)
    iou = interArea / float(boxAArea + boxBArea - interArea)
    if iou < 1e-12:
        iou =0
    return iou

def getSize(size):
    width = int(size.find('width').text)
    heigt = int(size.find('height').text)
    depth = int(size.find('depth').text)
    points = [width,heigt,depth]
    return points

def readShape(bndbox):
    #a = bndbox.find('xmin').text
    #print (a)
    xmin = int(bndbox.find('xmin').text)
    ymin = int(bndbox.find('ymin').text)
    xmax = int(bndbox.find('xmax').text)
    ymax = int(bndbox.find('ymax').text)
    points = [xmin,ymin,xmax,ymax]
    return points

def readResult(resultFile):
    parser = etree.XMLParser(encoding=ENCODE_METHOD)
    xmltree = ET.parse(resultFile,parser = parser).getroot()
    result =[]

    for result_iter in xmltree.findall('result'):
        temp_result = {}
        filename = result_iter.get('filename')  #xiugai filename-->filenanme
        temp_result['image_name'] = filename

        flags = result_iter.get('flag')
        if (flags == 'true' or flags == 'false' or flags == 'True' or flags == 'False'):
            temp_result['fault'] = flags.title()
            for object_iter in result_iter.findall('object'):
                object_name = object_iter.get('name')
            #temp_result['object_name'] = object_name
            #object_name = list(set(pred_result['object_name']))
                bndbox = object_iter.find("bndbox")            
                object_location = readShape(bndbox)
                temp_result.setdefault('object_name',[]).append(object_name)
                temp_result.setdefault(object_name,[]).append(object_location)
            result.append(temp_result)
            
        else:
            print ('the result flag is wrong of %s',flags)
            result = []
            return result
                    
    return result

def readVocXml(xmlfile,image_name):
    parser = etree.XMLParser(encoding=ENCODE_METHOD)
    
    xmltree = ET.parse(xmlfile,parser = parser).getroot()
    result =[]
    image = xmltree.find('filename')  #xiugai filename-->filenanme
    '''
    Detect two xml is equal
    if image != image_name:
        return
    '''
    temp_result = {} 
    temp_result['fault'] = 'False'
    temp_result.setdefault('image_name',[]).append(image)

    for object_iter in xmltree.findall('object'):               
        object_name = object_iter.find('name').text
        #temp_result['object_name'] = object_name
        bndbox = object_iter.find("bndbox")            
        object_location = readShape(bndbox)
        temp_result.setdefault('object_name',[]).append(object_name)
        temp_result.setdefault(object_name,[]).append(object_location)
        temp_result['fault'] = 'True'
   

    return temp_result



def label_save_img(img_file,pred_result,ground_truth_result,img_labeled_save_path,pre_name):
    
    image_name = pred_result['image_name']
    im = image_name.split('.')
    img_name = im[0]

    #img_name = pred_result['image_name']
    img_full_name = os.path.join(img_file,img_name + '.jpg')
    img = cv2.imread(img_full_name)
    color_white = (255,255,255)
    #create the labeled image sava name:'E:\\img_result\\192.3.1.03lsjljl.jpg'
    save_name = os.path.join(img_labeled_save_path,pre_name+image_name + '_result.jpg')
    #pre_labeled_img_save_file = 
    if pred_result.has_key('object_name'):
            object_name = list(set(pred_result['object_name']))
            for  obj_name in object_name:
                color = (random.randint(30,200),random.randint(30,200),random.randint(30,200))
                dets = pred_result[obj_name]
                for det in dets:
                    bbox = det[:4]
                    bbox = map(int,bbox)
                    cv2.rectangle(img,(bbox[0],bbox[1]),(bbox[2],bbox[3]),color = color,thickness = 2)
                    cv2.putText(img,'%s' %( obj_name),(bbox[0],bbox[1]+10),color = color_white,fontFace = cv2.FONT_HERSHEY_COMPLEX,fontScale=0.5)
    if ground_truth_result.has_key('object_name'):
            object_name = list(set(ground_truth_result['object_name']))
            for  obj_name in object_name:
                color = (0,0,255)
                dets = ground_truth_result[obj_name]
                for det in dets:
                    bbox = det[:4]
                    bbox = map(int,bbox)
                    cv2.rectangle(img,(bbox[0],bbox[1]),(bbox[2],bbox[3]),color = color,thickness = 2)                   
    
    cv2.imwrite(save_name,img)




def readGroudTruth(groundTruthFile,image_name):
    image_name = image_name + ".xml"
    ground_image_file = os.path.join(groundTruthFile,image_name)

    result = readVocXml(ground_image_file,image_name)
    return result

def evaluate(groundTruthFile,resultPath,excel_save_path,result_txt_save_path,img_labeled_save_path,threshold):

    '''
    模块功能：
    1、自动获取目录下所有的推理的xml结果文件，并循环读取具体内容
    2、将推理出的缺陷位置，在原图上进行标注，并保存在本地
    3、创建xls文件，保存推理xml结果和手动标记的xml结果，便于对比。
    4、创建txt文件，用于保存识别率、漏报率、准确率
    '''

    #set the initial count for every object as a dict
    class_name = ['DiaoChe','TaDiao','ShiGongJiXie','DaoXianYiWu','ShanHuo','YanWu']
    label_len = len(class_name)

    acc_txt_file = open(result_txt_save_path,'a+')
    total_img_num = len(os.listdir(groundTruthFile))/2
        
    for xmlFile in os.listdir(resultPath):  #根据结果路径，遍历所有的xml文件（文件个数即参加比赛厂家个数）
        try:
            resultFile = resultPath+xmlFile
            xml_name = xmlFile.split('.xml')
            xml_only_name = xml_name[0]
            precdict_true_count = [0,0] #first is true ,second is false
            predict_true,predict_false,groundtruth,accuracy = {},{},{},{}
            no_fault_img_num,fault_no_img_num,acc_mean, = 0.0 , 0.0 , 0.0
            #count = 0
            ground_fault_img_num = 0
            ground_normal_img_num = 0
            '''
            #img_labeled_save_path = os.path.join(img_labeled_save_path,onle_name)
            #img_labeled_save_path = img_labeled_save_path + '\\'
            #if not img_labeled_save_path:
               # os.makedirs(img_labeled_save_path)
            '''
            #get detection result and sava as a list
            pred_result = readResult(resultFile)
            #pred_count,gt_count,hit_count  = {},{},{}
            total_pred_img_num = len(pred_result)
            if(total_pred_img_num != total_img_num):
                print ('the pred image num is %d not equal to the total image num %d'%(total_pred_img_num,total_img_num))


            #初始化识别结果excel表格
            file = Workbook(encoding = 'utf-8')
            file_save_path = os.path.join(excel_save_path,xmlFile+'.xls')
            table= file.add_sheet('data')
            row0 = ['类型','识别数量','标记数量']    #用于写excel表格
    
            for i in range(1,len(row0)+1):
                name = row0[i-1]
                table.write(0,i,name)
            #read ground label based on predict image_name and count the number of object prediction
            for pred_detect_result in pred_result:
            
                #paint the prediction to image and save
                #pre_labeled_img_save_file = os.path.join(img_labeled_save_path,xml_only_name+image_name + '_result.jpg')
                #cv2.imwrite(pre_labeled_img_save_file,pre_labeled_img)

                imag_name = pred_detect_result['image_name']
                img_name = imag_name.split('.')
                image_name = img_name[0]
                #image_name =  pred_result_list['image_name']       
                ground_truth_result = readGroudTruth(groundTruthFile,image_name)
                pre_labeled_img = label_save_img(groundTruthFile,pred_detect_result,ground_truth_result,img_labeled_save_path,xml_only_name)

                '''
                #print (type(pred_result_list['fault']))
                #print (pred_result_list['fault'])
                #if (pred_result_list['fault'] == 'True') and True:
                    #print ('1')
                '''

                #count normal image but predict as fault
                if (ground_truth_result['fault'] == 'False'):
                    no_fault_img_num = no_fault_img_num +1
                    ground_normal_img_num = ground_normal_img_num + 1  #统计测试数据集中正常的图像个数
                    if (pred_detect_result['fault'] == 'False'):
                        no_fault_img_num = no_fault_img_num - 1     #将正常的图像预测为带隐患的图像 数量                  
                #count fault image but predict as normal
                if (ground_truth_result['fault'] == 'True'):
                    fault_no_img_num = fault_no_img_num + 1 
                    ground_fault_img_num = ground_fault_img_num + 1  #统计测试数据集中含有隐患的图像个数
                    if (pred_detect_result['fault'] == 'True'):
                        fault_no_img_num = fault_no_img_num - 1     #将含有隐患的图像预测为不带隐患的图像 数量
                    
                '''         
                #count normal image but predict as fault
                if (pred_result_list['fault'] == 'true') and (ground_truth_result['fault'] == 'False'):
                    no_fault_img_num = no_fault_img_num + 1
                #count fault image but predict as normal
                if (pred_result_list['fault'] == 'false') and (ground_truth_result['fault'] == 'True'):
                    fault_no_img_num = fault_no_img_num + 1 
                '''
                #count the total objects of every fault based on ground_labeled xml
                for key , value in ground_truth_result.items():
                    if key != 'fault':
                        groundtruth[key] = groundtruth.get(key,0) + len(value)
        
                #pred_detect_result = pred_result[count] #extract the count result
                #count += 1
                ##tabel = write(table,pred_detect_result,ground_truth_result)
                write(table,pred_detect_result,ground_truth_result)
       
                if pred_detect_result.has_key('object_name'):
                    #groud_object_list = ground_truth_result
                    #intialize the false prediction of every object class is all the objects' prediction based on prediction result
                    for obj_nam in list(set(pred_detect_result['object_name'])):
                        pre_obj_loc = pred_detect_result[obj_nam]
                        predict_false[obj_nam] = predict_false.get(obj_nam,0) + float(len(pre_obj_loc))
                    #pick the right pred based on grd_label and minus one in predict_false
                    if ground_truth_result.has_key('object_name'):
                        for obj_nam in list(set(ground_truth_result['object_name'])):
                            if pred_detect_result.has_key(obj_nam): # some object is in ground xml 
                                pre_obj_loc = pred_detect_result[obj_nam]            
                                grd_obj_loc = ground_truth_result[obj_nam]
                                #grd_obj_num = len(grd_obj_loc)
                                #groundtruth[obj_nam] = groundtruth.get(obj_nam,0) + grd_obj_num                
            
                                for grd_obj in grd_obj_loc:
                                    iou = []
                                    for pre_obj in pre_obj_loc:                    
                                        iou_tmp = bb_intersection_over_union(pre_obj,grd_obj)
                                        iou.append(iou_tmp)
                                    iou.sort()
                                    if iou[-1] > threshold:
                                        predict_true[obj_nam] = predict_true.get(obj_nam,0) + 1.0 
                                        #predict[obj_nam][0] += 1
                                        predict_false[obj_nam] = predict_false.get(obj_nam,0) -1.0 
                                    #else:
                                        #predict_false[obj_nam] = predict_false.get(obj_nam,0) + 1 
                            #else:# some object is in ground xml 
                                 #predict_false[obj_nam] = predict_false.get(obj_nam,0) + len(pre_obj_loc)

            file.save(file_save_path)
            
            '''**********************caculate the evaluating indicator **************************'''
            miss_detect_acc = float(fault_no_img_num)/ground_fault_img_num
            wrong_detect_acc = float(no_fault_img_num)/total_img_num           

            label_len = 0
            #单独计算每类隐患的识别准确率  统计测试集中缺陷的类型数目
            for key,value in groundtruth.items():
                if key != 'object_name' and key != 'image_name':
                    accuracy[key] = 0.0
                if predict_true.has_key(key):
                    accuracy[key] = predict_true[key] / float(groundtruth[key])
                    acc_mean += accuracy[key]
                if key != 'object_name' and key != 'image_name':
                    #a = predict_true[key]
                   # print (a)
                    label_len += 1
                    print ('the {} object detect accuracy is {:4f} '.format(key ,accuracy[key]) ) 
                    #print ( 'the {} pred object detect num is {:4f} '.format(key ,predict_true[key]) )
                    #print ( 'the {} grd object detect num is {:4f} '.format(key ,groundtruth[key]) )     
                     
            '''
            for key,value in predict_true.items():
                if key != 'object_name' and key !='image_name':
                    acc =  predict_true[key] / float(groundtruth[key])
                    accuracy[key]= acc
                    acc_mean += acc
                    #print (predict_true[key],'   ', groundtruth[key], '   ',accuracy[key])
                    print ('the {} object detect accuracy is {:4f} '.format(key ,acc) )
            '''
            #计算隐患识别的平均准确率
            acc_mean = acc_mean/label_len;
            print('the miss detect acc is:{:4f}'.format(miss_detect_acc))
            print('the wrong detect acc is:{:4f}'.format(wrong_detect_acc))
            print ('the mean accuracy  is {:4f} '.format(acc_mean))

            #acc_result = xmlFile + '#' + wrong_detect_acc + '#' + miss_detect_acc + '#' + acc_mean
            miss_detect_acc = '%f#'%(miss_detect_acc)
            wrong_detect_acc = '%f#'%(wrong_detect_acc)

            acc_mean = '%f\n'%(acc_mean)
            acc_txt_file.write(xml_name[0])
            acc_txt_file.write('#')
            acc_txt_file.write(wrong_detect_acc)
           # acc_txt_file.write('#')
            acc_txt_file.write(miss_detect_acc)
           # acc_txt_file.write('#')
            acc_txt_file.write(acc_mean)
        except :
            acc_txt_file.write(xml_name[0])
            acc_txt_file.write('#')
            acc_txt_file.write('xml error\n')
    acc_txt_file.close()

    
    