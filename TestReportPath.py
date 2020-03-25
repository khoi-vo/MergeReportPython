import os
from bs4 import BeautifulSoup
import shutil
from distutils.dir_util import copy_tree
class TestReport:
    def __init__(self,inputPath):
        self.path = inputPath
        self.testSuiteFileArray = []
        self.testSuiteDict = {"RTCFM":[],"RTSales":[],"CFM":[],"Sales":[],"NotExecuted":[]}
        self.crawlingPath()
        self.insertElementToTemplate(self.testSuiteDict["RTCFM"],"./template/CFMRegressionTemplate.html","./reports/logs/CFMRegression.html")
        self.insertElementToTemplate(self.testSuiteDict["RTSales"],"./template/SalesRegressionTemplate.html","./reports/logs/SalesRegression.html")
        self.insertElementToTemplate(self.testSuiteDict["CFM"],"./template/CFMSanityTemplate.html","./reports/logs/CFMSanity.html")
        self.insertElementToTemplate(self.testSuiteDict["Sales"],"./template/SalesSanityTemplate.html","./reports/logs/SalesSanity.html")
        self.copyChildrenFilesTestSuite(self.testSuiteDict["RTCFM"],"./reports/logs/")
        self.copyChildrenFilesTestSuite(self.testSuiteDict["RTSales"],"./reports/logs/")
        self.copyChildrenFilesTestSuite(self.testSuiteDict["CFM"],"./reports/logs/")
        self.copyChildrenFilesTestSuite(self.testSuiteDict["Sales"],"./reports/logs/")
        self.copyScreenshotsFolder("./reports/screenshots/")
        masterSuite = MasterSuite("./template/MasterSuiteTemplate.html",self.testSuiteDict,"./reports/logs/MasterSuite.html")
    def crawlingPath(self):
        for root,dirs,files in  os.walk(self.path,topdown=True):
            for name in files:
                if "Result" in name:
                    self.testSuiteFileArray.append(os.path.join(root,name))
                    tempTestSuite = TestSuite(os.path.join(root,name))
                    self.testSuiteDict["RTCFM"].extend(tempTestSuite.RTCFMList)
                    self.testSuiteDict["CFM"].extend(tempTestSuite.CFMList)
                    self.testSuiteDict["RTSales"].extend(tempTestSuite.RTSalesList)
                    self.testSuiteDict["Sales"].extend(tempTestSuite.SalesList)
                    self.testSuiteDict["NotExecuted"].append(tempTestSuite.NotExecuted) 
        
    def insertElementToTemplate(self, inputList, path,outputFileName):
        soup = BeautifulSoup(open(path),"html.parser")
        templateRowString = "<tr class='' bgcolor='#FFFFFF' style='display: table-row;'> <th><font size='2.5' face='Calibri' color='black' align='center'></font></th> <th><font size='2.5' face='Calibri' color='black' align='left'></font></th> <th><font size='2.5' face='Calibri' color='black' align='center' ><a></font></th> </tr>"
        table = soup.find(id="table")
        scriptChartString = "function drawChart(){var a=google.visualization.arrayToDataTable([['TestCase','Number of Test Case'],['PASS',passNumber],['FAIL',failNumber]]);new google.visualization.PieChart(document.getElementById('piechart')).draw(a,{title:'titleName',width:450,height:300,colors:['#00FA9A','#F08080'],is3D:!0,fontSize:13,backgroundColor:'#DCDCDC'})}google.charts.load('current',{packages:['corechart']}),google.charts.setOnLoadCallback(drawChart);"
        numberOfPass = 0
        for index,data in enumerate(inputList):
            templateRow = BeautifulSoup(templateRowString,'html.parser').tr
            if data[1] == "PASS":
                templateRow["class"].append("hoverRowPass")
                numberOfPass = numberOfPass + 1
            else:
                templateRow["class"].append("hoverRowFail")
            tableHeads = templateRow.findAll("th")
            tableHeads[0].font.string = str(index + 1)
            tableHeads[1].font.string = data[0]
            tableHeads[2].font.a.string = data[1]
            tableHeads[2].font.a['href'] = data[2]
            table.append(templateRow)
        summary = soup.find(id="summary")
        tableHeadsSummary = summary.findAll("th")
        tableHeadsSummary[1].font.string = str(len(inputList))
        tableHeadsSummary[2].font.string = str(numberOfPass)
        tableHeadsSummary[3].font.string = str(len(inputList)-numberOfPass)
        scriptChartString = scriptChartString.replace('passNumber',str(numberOfPass))
        scriptChartString = scriptChartString.replace('failNumber',str(len(inputList)-numberOfPass))
        scriptChartTag = soup.find(id="scriptChart")
        captionTag = soup.find("caption")
        captionText = captionTag.h1.font.text
        scriptChartString = scriptChartString.replace('titleName',captionText)
        scriptChartTag.string=scriptChartString
        with open(outputFileName, "w",encoding="utf-8") as file:
                file.write(str(soup))
    
    def copyChildrenFilesTestSuite(self,inputListOfElements,destination):
        for testCaseElement in inputListOfElements:
            for root,dirs,files in os.walk(self.path,topdown=True):
                for name in files:
                    if testCaseElement[2] in name:
                        shutil.copy2(os.path.join(root,name),destination)
                        self.modifyTestCaseReport(destination+testCaseElement[2])
                    elif "ini.html" in name:
                        shutil.copy2(os.path.join(root,name),destination)
    
    def copyScreenshotsFolder(self,destination):
        for root,dirs,files in os.walk(self.path,topdown=True):
            for name in dirs:
                if "screenshots" in name:
                    copy_tree(os.path.join(root,name),destination)

    def modifyTestCaseReport(self,inputTestCaseFile):
        soup = BeautifulSoup(open(inputTestCaseFile),"html.parser")
        tableTag = soup.find("table")
        tableTag['align'] = "center" 
        tableRows = soup.findAll("tr")
        for row in tableRows:
            column = row.findAll("td")
            if len(column) > 0:
                resultColumn = column[len(column)-4]
                if resultColumn.text == "FAIL":
                    resultColumn['style'] = "background-color:#F08080"
                elif resultColumn.text == "PASS":
                    resultColumn['style'] = "background-color:#00FA9A"
                column[1].extract()
                column[2].extract()
                column[4].extract()
        with open(inputTestCaseFile, "w",encoding="utf-8") as file:
            file.write(str(soup))            

class TestSuite:
    def __init__(self,inputTestSuitePath):
        self.soup = BeautifulSoup(open(inputTestSuitePath),'html.parser')
        self.RTCFMList = []
        self.RTSalesList = []
        self.CFMList = []
        self.SalesList = []
        self.NotExecuted = ""
        self.extractElement()
       

    def extractElement(self):
        tableCells = self.soup.findAll("th")
        NotExecutedCell = self.soup.find(id="summary").findAll("a")
        for cell in tableCells:
            if "[RT]CFM" in cell.text:
                self.RTCFMList.append([cell.text,cell.next_sibling.text,cell.next_sibling.a["href"]])
            elif "[RT]Sales" in cell.text:
                self.RTSalesList.append([cell.text,cell.next_sibling.text,cell.next_sibling.a["href"]])
            elif "CFM" in cell.text:
                self.CFMList.append([cell.text,cell.next_sibling.text,cell.next_sibling.a["href"]])
            elif "Sales" in cell.text:
                self.SalesList.append([cell.text,cell.next_sibling.text,cell.next_sibling.a["href"]])
        self.NotExecuted = NotExecutedCell[0]["href"]
 ###############################################################################################################
 # This Class is responsible for editing MasterSuite file
 # This Class reads the MasterSuiteTemplate and gathers ID corresponding to each test set and the total tag
 # After that, the function updateDataSet is called to update the template with the calculation data
 # Data is gathered from the Dictionary from TestSuite Class
 # Finally, the piechart is inserted
 # #############################################################################################################    
class MasterSuite:
    def __init__(self,inputMasterSuiteTemplate,inputTestSuiteDictionary,outputFileName):
        #Initialize number of total and pass of row TOTAL
        self.total = 0
        self.totalPass = 0
        #Get the Dictionary from TestSuite Class
        self.testSuiteDictionary = inputTestSuiteDictionary
        #Open the MasterSuite Template
        self.soup = BeautifulSoup(open(inputMasterSuiteTemplate),"html.parser")
        #Get the ID from template. These IDs are used for updating data
        self.testSetSalesSanityID = self.soup.find(id="testset1")
        self.testSetCFMSanityID = self.soup.find(id="testset2")
        self.testSetSalesRegressionID = self.soup.find(id="testset3")
        self.testSetCFMRegressionID = self.soup.find(id="testset4")
        self.totalID = self.soup.find(id="total")
        #Update Data of Test Set rows and Total row
        self.updateDataTestSet(self.testSetCFMRegressionID,"RTCFM","scriptChartCFMRegression","CFMRegressionPieChart","CFM Regression")
        self.updateDataTestSet(self.testSetCFMSanityID,"CFM","scriptChartCFMSanity","CFMSanityPieChart","CFM Sanity")
        self.updateDataTestSet(self.testSetSalesRegressionID,"RTSales","scriptChartSalesRegression","SalesRegressionPieChart","Sales Regression")
        self.updateDataTestSet(self.testSetSalesSanityID,"Sales","scriptChartSalesSanity","SalesSanityPieChart","Sales Sanity")
        self.updateDataTestSet(self.totalID,"Total","scriptChartTotal","totalPieChart","Total")
        #Write the modified MasterSuite template to the output file
        with open(outputFileName, "w",encoding="utf-8") as file:
            file.write(str(self.soup))
    #This function gathers the html element: numberOfTestCase,numberOfPassTestCase,numberOfFailTest,percentagePass and percentageFail
    # 
    def updateDataTestSet(self,testSetID,keyDict,scriptChartID,piechartID,titlePieChart):
        numberOfTestCaseHTML = testSetID.findAll("th")[1]
        numberOfPassTestHTML = testSetID.findAll("th")[2]
        numberOfFailTestHTML = testSetID.findAll("th")[3]
        percentagePassHTML = testSetID.findAll("th")[5]
        percentageFailHTML = testSetID.findAll("th")[6]
        if keyDict == "Total":
            Total = self.total
            numberOfPass = self.totalPass
            numberOfFail = self.total - self.totalPass      
        else:    
            Total,numberOfPass, numberOfFail = self.getValueFromDictionary(keyDict)
            self.total = self.total + Total
            self.totalPass = self.totalPass + numberOfPass
        percentagePass = (numberOfPass*100)//Total
        percentageFail = 100 - percentagePass
        numberOfTestCaseHTML.string = str(Total)
        numberOfPassTestHTML.string = str(numberOfPass)
        numberOfFailTestHTML.string = str(numberOfFail)
        percentagePassHTML.string = str(percentagePass)+"%"
        percentageFailHTML.string = str(percentageFail)+"%"
        self.insertPieChart(titlePieChart,numberOfPass,numberOfFail,scriptChartID,piechartID)
    def getValueFromDictionary(self, keyDict):
        numberOfPass = 0
        for data in self.testSuiteDictionary[keyDict]:
            if data[1] == "PASS":
                numberOfPass = numberOfPass + 1
        return len(self.testSuiteDictionary[keyDict]),numberOfPass,  len(self.testSuiteDictionary[keyDict])-numberOfPass
    def insertPieChart(self,inputTitlePieChart,inputNumberOfPass,inputNumberOfFail,scripChartID,piechartID):
        if inputTitlePieChart == "Total":
            scriptChartString = "function drawChart(){var a=google.visualization.arrayToDataTable([['TestCase','Number of Test Case'],['PASS',passNumber],['FAIL',failNumber]]);new google.visualization.PieChart(document.getElementById('piechart')).draw(a,{title:'titleName',titleTextStyle:{fontSize: 18},width:450,height:300,colors:['#00FA9A','#F08080'],is3D:!0,fontSize:15})}google.charts.load('current',{packages:['corechart']}),google.charts.setOnLoadCallback(drawChart);"
        else:
            scriptChartString = "function drawChart(){var a=google.visualization.arrayToDataTable([['TestCase','Number of Test Case'],['PASS',passNumber],['FAIL',failNumber]]);new google.visualization.PieChart(document.getElementById('piechart')).draw(a,{title:'titleName',width:270,height:270,colors:['#00FA9A','#F08080'],is3D:!0,fontSize:13,legend:'none'})}google.charts.load('current',{packages:['corechart']}),google.charts.setOnLoadCallback(drawChart);"
        scriptChartString = scriptChartString.replace('passNumber',str(inputNumberOfPass))
        scriptChartString = scriptChartString.replace('failNumber',str(inputNumberOfFail))
        scriptChartString = scriptChartString.replace('piechart',piechartID)
        scriptChartString = scriptChartString.replace('titleName',inputTitlePieChart)
        scriptChartTag = self.soup.find(id=scripChartID)
        scriptChartTag.string=scriptChartString



        



        

    

