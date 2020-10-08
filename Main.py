#!/usr/bin/env python3
import os
from bs4 import BeautifulSoup
#scriptChartString = "function drawChart(){var a=google.visualization.arrayToDataTable([['TestCase','Number of Test Case'],['PASS',passNumber],['FAIL',failNumber]]);new google.visualization.PieChart(document.getElementById('piechart')).draw(a,{title:'titleName',width:450,height:300,colors:['#90ee90','red'],is3D:!0,fontSize:13})}google.charts.load('current',{packages:['corechart']}),google.charts.setOnLoadCallback(drawChart);"
from TestReportPath import TestReport, TestReportUpdate
from distutils.dir_util import copy_tree
import argparse  
def mergeHandler(args):
    if args.i:
        #C:\\Users\\h.vo\\Downloads\\reports (1)
        cwd = os.path.dirname(os.path.abspath(__file__))
        print(cwd)
        for root,dirs,files in os.walk(cwd+"/reports/logs/",topdown=True):
            for name in files:
                if "html" in name:
                    os.remove(os.path.join(root,name))
        testReport = TestReport(args.i,args.k)
    if args.o:
        reportFolder = "./reports"
        copy_tree(reportFolder,args.o)
def updateHandler(args):
    #beforeUpdate = []
    #afterUpdate = []
    if args.s and args.m:
        #file1 = open("file1.txt","w+")
        #file2 = open("file2.txt","w+")
        #for root,dirs,files in os.walk("./reports/logs/",topdown=True):
            #for name in files:
                #if "1-" in name:
                    #beforeUpdate.append(name)
                    #file1.write(name+"\n")
        testReportUpdate = TestReportUpdate(args.m,args.s)
        #for root,dirs,files in os.walk("./reports/logs/",topdown=True):
            #for name in files:
                #if "1-" in name:
                    #afterUpdate.append(name)
                    #file2.write(name+"\n")
        #filedelete = [file for file in beforeUpdate if file not in afterUpdate]
        #fileadd = [file for file in afterUpdate if file not in beforeUpdate]
        #print(len(filedelete),len(testReportUpdate.beforeUpdate))
        #print(len(fileadd),len(testReportUpdate.afterUpdate))
        #print([file for file in testReportUpdate.afterUpdate if testReportUpdate.afterUpdate.count(file) > 1])
parser = argparse.ArgumentParser(description='Sample Arguments Parser')
subparsers = parser.add_subparsers()
mergeParser = subparsers.add_parser("merge")
mergeParser.add_argument("-i",required=True, metavar='INPUT-DIRECTORY', help="specify input directory")
mergeParser.add_argument("-o",required=False, metavar='OUTPUT-DIRECTORY', help="specify output directory")
mergeParser.add_argument("-k",required=False, metavar='KEY-NUMBER', help="specify key number")
mergeParser.set_defaults(func=mergeHandler)

mergeParser = subparsers.add_parser("update")
mergeParser.add_argument("-m",required=True, metavar='MAIN-FOLDER', help="specify folder contains files to be updated")
mergeParser.add_argument("-s",required=True, metavar='SUB-FILE', help="specify directory and file used for updating")
mergeParser.set_defaults(func=updateHandler)
arguments= parser.parse_args()
arguments.func(arguments)

print("Successful")