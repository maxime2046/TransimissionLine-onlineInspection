import xlwt
from xlutils3 import copy

def write(table,pred_result,ground_truth):
    #file = Workbook(encoding = 'utf-8')
    #table = file.add_sheet('pred_result')
    ground_object_name = []
    pred_object_name = []
    if pred_result.has_key('object_name'):
        pred_object_name = pred_result['object_name']
    if ground_truth.has_key('object_name'):
        ground_object_name = ground_truth['object_name']    
    object_name = pred_object_name + ground_object_name
    object_name = list(set(object_name))
    #new_table = copy.copy(table)
    #sheet = new_table.get_sheet('data')
    k = len(table.rows)
    a = pred_result['image_name']
    table.write(k,0,a)
    count = k
    if pred_result.has_key('object_name') or ground_truth.has_key('object_name'):
        for obj_name in object_name:
            table.write(count,1,obj_name)
            if pred_result.has_key(obj_name):
                num = len(pred_result[obj_name])
                table.write(count,2,num)
            else :
                table.write(count,2,0)
            if ground_truth.has_key(obj_name):
                num = len(ground_truth[obj_name])
                table.write(count,3,num)
            else :
                table.write(count,3,0)
            count += 1
    #return table

        



