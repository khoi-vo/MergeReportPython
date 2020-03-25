#!/usr/bin/env python3
from bs4 import BeautifulSoup
#scriptChartString = "function drawChart(){var a=google.visualization.arrayToDataTable([['TestCase','Number of Test Case'],['PASS',passNumber],['FAIL',failNumber]]);new google.visualization.PieChart(document.getElementById('piechart')).draw(a,{title:'titleName',width:450,height:300,colors:['#90ee90','red'],is3D:!0,fontSize:13})}google.charts.load('current',{packages:['corechart']}),google.charts.setOnLoadCallback(drawChart);"
from TestReportPath import TestReport 
from distutils.dir_util import copy_tree
import argparse  
def mergeHandler(args):
    if args.i:
        #C:\\Users\\h.vo\\Downloads\\reports (1)
        testReport = TestReport(args.i)
    if args.o:
        reportFolder = "./reports"
        copy_tree(reportFolder,args.o)
        print("output is set")

parser = argparse.ArgumentParser(description='Sample Arguments Parser')
subparsers = parser.add_subparsers()
mergeParser = subparsers.add_parser("merge")
mergeParser.add_argument("-i",required=True, metavar='INPUT-DIRECTORY', help="specify input directory")
mergeParser.add_argument("-o",required=False, metavar='OUTPUT-DIRECTORY', help="specify output directory")
mergeParser.set_defaults(func=mergeHandler)
arguments= parser.parse_args()
arguments.func(arguments)

print("Successful")