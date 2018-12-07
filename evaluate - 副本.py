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
    # compute the area of intersection rectangle
    interArea = (xB - xA + 1) * (yB - yA + 1)
    boxAArea = (boxA[2] - boxA[0] + 1) * (boxA[3] - boxA[1] + 1)
    boxBArea = (boxB[2] - boxB[0] + 1) * (boxB[3] - boxB[1] + 1)
    iou = interArea / float(boxAArea + boxBArea - interArea)
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
        temp_result['fault'] = flags

        #size_iter = result_iter.find('size')
        #size = getSize(size_iter)
       # temp_result['size'] = size


        for object_iter in result_iter.findall('object'):
            object_name = object_iter.get('name')
            #temp_result['object_name'] = object_name
            #object_name = list(set(pred_result['label_name']))
            bndbox = object_iter.find("bndbox")            
            object_location = readShape(bndbox)
            temp_result.setdefault('label_name',[]).append(object_name)
            temp_result.setdefault(object_name,[]).append(object_location)
        result.append(temp_result)
    return result

def label_img(img_file,pred_result):
    img_name = pred_result['image_name']
    img_full_name = os.path.join(img_file,img_name+'.jpg')
    img = cv2.imread(img_full_name)
    color_white = (255,255,255)
    if pred_result.has_key('label_name'):
            object_name = list(set(pred_result['label_name']))
            for  obj_name in object_name:
                color = (random.randint(0,256),random.randint(0,256),random.randint(0,256))
                dets = pred_result[obj_name]
                for det in dets:
                    bbox = det[:4]
                    bbox = map(int,bbox)
                    cv2.rectangle(img,(bbox[0],bbox[1]),(bbox[2],bbox[3]),color = color,thickness = 2)
                    cv2.putText(img,'%s' %( obj_name),(bbox[0],bbox[1]+10),color = color_white,fontFace = cv2.FONT_HERSHEY_COMPLEX,fontScale=0.5)
    return img

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
        temp_result.setdefault('label_name',[]).append(object_name)
        temp_result.setdefault(object_name,[]).append(object_location)
        temp_result['fault'] = 'True'
   

    return temp_result


def readGroudTruth(groundTruthFile,image_name):
    image_name = image_name + ".xml"
    ground_image_file = os.path.join(groundTruthFile,image_name)

    result = readVocXml(ground_image_file,image_name)
    return result



if __name__ == "__main__":
    
    resultPath = 'E:\\CodeTest\\ReadXml\\resultxml\\'   #各个厂家存储识别结果xml的路径
    groundTruthFile = 'E:\\CodeTest\\ReadXml\\test51\\'    #手动标记标准样本的路径
    img_path = 'E:\\CodeTest\\ReadXml\\test51\\'           #带标价框的图像存储位置 这个要每个厂家一个目录。
    excel_save_path = 'E:\\CodeTest\\ReadXml\\'
    result_txt_save_file = 'E:\\CodeTest\\ReadXml\\acc.txt'
    img_labeled_save_path = 'E:\\CodeTest\\ReadXml\\img_labeled'

    threshold = 0.5 #usd for detect prediction is right or wrong.

    #table = xlrd.open_workbook('F:\\result.xls')
    #set the initial count for every object as a dict
    label_list = ['DiaoChe','TaDiao','ShiGongJiXie','DaoXianYiWu','ShanHuo','YanWu']
    label_len = len(label_list)

    acc_txt_file = file(result_txt_save_file,'a+')
        
    for xmlFile in os.listdir(resultPath):
        resultFile = resultPath+xmlFile
        xml_name = xmlFile.split('.xml')
        onle_name = xml_name[0]
        precdict_true_count = [0,0] #first is true ,second is false
        predict_true,predict_false,groundtruth,accuracy = {},{},{},{}
        no_fault_img_num,fault_no_img_num,acc_mean, = 0.0 , 0.0 , 0.0
        count = 0

        #get detection result and sava as a list
        pred_result = readResult(resultFile)
        #pred_count,gt_count,hit_count  = {},{},{}
        total_img_num = len(pred_result)


        #初始化识别结果excel表格
        file = Workbook(encoding = 'utf-8')
        file_save_path = os.path.join(excel_save_path,xmlFile+'.xls')
        table= file.add_sheet('data')
        row0 = ['类型','标记数量','识别数量']    #用于写excel表格
    
        for i in range(1,len(row0)+1):
            name = row0[i-1]
            table.write(0,i,name)
        #read ground label based on predict image_name and count the number of object prediction
        for pred_result_list in pred_result:

            image_name = pred_result_list['image_name']
            #imread image and label rectangle and save to locoal storage
            pre_labeled_img = label_img(img_path,pred_result_list)
            pre_labeled_img_save_file = os.path.join(img_labeled_save_path,image_name + '_result.jpg')
            cv2.imwrite(pre_labeled_img_save_file,pre_labeled_img)

        
            ground_truth_result = readGroudTruth(groundTruthFile,image_name)
            #print (type(pred_result_list['fault']))
            #print (pred_result_list['fault'])
            #if (pred_result_list['fault'] == 'True') and True:
                #print ('1')

            #count normal image but predict as fault
            if (pred_result_list['fault'] == 'True') and (ground_truth_result['fault']== 'False'):
                no_fault_img_num = no_fault_img_num + 1
            #count fault image but predict as normal
            if (pred_result_list['fault'] == 'False') and (ground_truth_result['fault'] == 'True'):
                fault_no_img_num = fault_no_img_num + 1       

            #count the total objects of ground label xml
            for key , value in ground_truth_result.items():
                if key != 'fault':
                    groundtruth[key] = groundtruth.get(key,0) + len(value)
        
            pred_detect_result = pred_result[count] #extract the count result
            count += 1
            #tabel = write(table,pred_detect_result,ground_truth_result)
            write(table,pred_detect_result,ground_truth_result)
       
            if pred_detect_result.has_key('label_name'):
                #groud_object_list = ground_truth_result
                for obj_nam in list(set(pred_detect_result['label_name'])):
                    if ground_truth_result.has_key(obj_nam): # some object is in ground xml 
                        pre_obj_loc = pred_detect_result[obj_nam]            
                        grd_obj_loc = ground_truth_result[obj_nam]
                        grd_obj_num = len(grd_obj_loc)
                        #groundtruth[obj_nam] = groundtruth.get(obj_nam,0) + grd_obj_num                
            
                        for pre_obj in pre_obj_loc:
                            iou = []
                            for grd_obj in grd_obj_loc:                    
                                iou_tmp = bb_intersection_over_union(pre_obj,grd_obj)
                                iou.append(iou_tmp)
                            iou.sort()
                            if iou[-1] > threshold:
                                predict_true[obj_nam] = predict_true.get(obj_nam,0) + 1 
                                #predict[obj_nam][0] += 1
                            else:
                                predict_false[obj_nam] = predict_false.get(obj_nam,0) + 1 
                    else:# some object is in ground xml 
                         predict_false[obj_nam] = predict_false.get(obj_nam,0) + len(pre_obj_loc)

        miss_detect_acc = float(fault_no_img_num)/total_img_num

        wrong_detect_acc = float(no_fault_img_num)/total_img_num

        file.save(file_save_path)


        for key,value in groundtruth.items():
            if key != 'label_name' and key !='image_name':
                accuracy[key] = 0.0

        for key,value in predict_true.items():
            if key != 'label_name' and key !='image_name':
                acc =  predict_true[key] / float(groundtruth[key])
                accuracy[key]= acc
                acc_mean += acc
                #print (predict_true[key],'   ', groundtruth[key], '   ',accuracy[key])
                print ('the {} object detect accuracy is {:4f} '.format(key ,acc) )

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
    acc_txt_file.close()



        #print ('the mean acc is: {:4f};'.format(acc_mean))

        #print('the miss detect acc is:{:4f}'.format(miss_detect_acc))
        ##print('the wrong detect acc is:{:4f}'.format(wrong_detect_acc))

        #acc_txt_file.close()
        
    
    