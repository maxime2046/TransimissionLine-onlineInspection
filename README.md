# TransimissionLine-onlineInspection
#输电线路在线监测验证比赛代码
#实现功能：
#一、读取参赛单位生成的xml文件，读取出识别出的隐患类型与隐患位置
#二、与标准的xml进行对比，确定隐患识别的准确率、误检率、漏检率。

误检率：不存在隐患但识别出的图像数据/图像总数目
漏检率：存在隐患但未识别出的图像数据/图像总数目
准确率：某一类隐患的识别准确率：存在隐患并识别出的目标的个数/本类型隐患总数目
        准确率：各类型识别准确率求和/隐患类型数目