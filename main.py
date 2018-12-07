import argparse
from evaluate import *

def parse_args():
    parser  = argparse.ArgumentParser(description = 'Calculate the prediction accuarcy')
    parser.add_argument('--label-image-path', dest = 'label_image_path',default ='E:\\CodeTest\\ReadXml\\Image\\test52\\',
                        help = 'the path of standard image and label')
    parser.add_argument('--pred-result-path' , dest = 'pred_result_path',default = 'E:\\CodeTest\\ReadXml\\resultxml\\',
                        help = 'the path of prediction result ')
    parser.add_argument('--excel-save-path' , dest = 'excel_save_path',default = 'E:\\CodeTest\\ReadXml\\',
                        help = 'the path of prediction result and standard date to sava as an excel')
    parser.add_argument('--result-txt-save-path' , dest = 'result_txt_save_path',default = 'E:\\CodeTest\\ReadXml\\acc.txt',
                        help = 'the path of accuarcy to save every prediction')
    parser.add_argument('--image-labeled-save-path' , dest = 'image_labeled_save_path',default = 'E:\\CodeTest\\ReadXml\\img_labeled',
                        help = 'the path of labeled image with prediction result')
    parser.add_argument('--threshold' ,dest = 'threshold',default = 0.5,
                        help = 'the threshold of IoU')
    #parser.add_argument('--class-name' ,dest = 'class-name',dafault = 'DiaoChe','TaDiao',\
     #                   'ShiGongJiXie','DaoXianYiWu','ShanHuo','YanWu'
     #                   help = 'the threshold of IoU')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = parse_args()
    evaluate(args.label_image_path,args.pred_result_path,args.excel_save_path,
             args.result_txt_save_path,args.image_labeled_save_path,args.threshold)
