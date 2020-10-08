import os
from bs4 import BeautifulSoup
import shutil
from distutils.dir_util import copy_tree
###############################################################################################################
 # This Class is responsible for handling multiple of steps of merging the report:
 # Step 1: Getting the directory of input folder, the crawlingPath function is called to crawl each folder
 #         and check for files which has the "Result" in file name.
 # Step 2: For each file searched, the testsuite object is initiated and representated for each test suite file.
 #         Then after the catorization of test case, lists of each categorized test cases in appended to the dictionary.
 # Step 3: For each Key represented for each test suite name, the insertElementToTemplate is called to insert data read
 #         from the dictionary into the testSuiteTemplate and generate the result test suite into the input directory
 # Step 4: After 4 test suite of 4 categories are generated. Test cases file corresponding to the href of test case in each test suite
 #         is copy from origin folder to the destination folder which is the same folder of the test suite. After that,
 #         the test case file is modified by function modifyTestCaseReport
 # Step 5: Copy the screenshot folder of the origin directory to the destination folder.
 # Step 6: Modify the MasterSuite report by instantiate the masterSuite object
 # ############################################################################################################# 
class TestReport:
    def __init__(self,inputPath):
        self.cwd = os.path.dirname(os.path.abspath(__file__))
        print(self.cwd)
        self.path = inputPath
        self.testSuiteFileArray = []
        self.testSuiteDict = {"RTCFM":[],"RTSales":[],"CFM":[],"Sales":[],"NotExecuted":[]}
        self.crawlingPath(self.path,self.testSuiteDict)
        if len(self.testSuiteDict["RTCFM"]) > 0:
            self.insertElementToTemplate(self.testSuiteDict["RTCFM"],self.cwd+"/template/CFMRegressionTemplate.html",self.cwd+"/reports/logs/CFMRegression.html")
            self.copyChildrenFilesTestSuite(self.testSuiteDict["RTCFM"],self.cwd+"/reports/logs/")
        if len(self.testSuiteDict["RTSales"]) > 0:
            self.insertElementToTemplate(self.testSuiteDict["RTSales"],self.cwd+"/template/SalesRegressionTemplate.html",self.cwd+"/reports/logs/SalesRegression.html")
            self.copyChildrenFilesTestSuite(self.testSuiteDict["RTSales"],self.cwd+"/reports/logs/")
        if len(self.testSuiteDict["CFM"]) > 0:
            self.insertElementToTemplate(self.testSuiteDict["CFM"],self.cwd+"/template/CFMSanityTemplate.html",self.cwd+"/reports/logs/CFMSanity.html")
            self.copyChildrenFilesTestSuite(self.testSuiteDict["CFM"],self.cwd+"/reports/logs/")
        if len(self.testSuiteDict["Sales"]) > 0:
            self.insertElementToTemplate(self.testSuiteDict["Sales"],self.cwd+"/template/SalesSanityTemplate.html",self.cwd+"/reports/logs/SalesSanity.html")
            self.copyChildrenFilesTestSuite(self.testSuiteDict["Sales"],self.cwd+"/reports/logs/")
        self.copyScreenshotsFolder(self.cwd+"/reports/screenshots/")
        masterSuite = MasterSuite(self.cwd+"/template/MasterSuiteTemplate.html",self.testSuiteDict,self.cwd+"/reports/logs/MasterSuite.html")
    #This function crawling the directory of input folder and searching for the file name contains the "Result" in name
    def crawlingPath(self,inputPath,inputTestSuiteDict):
        for root,dirs,files in  os.walk(inputPath,topdown=True):
            for name in files:
                if "Result" in name:
                    print(name)
                    #self.testSuiteFileArray.append(os.path.join(root,name))
                    #Instantiate the test suite object represented for the test suite file
                    tempTestSuite = TestSuite(os.path.join(root,name))
                    #Append the lists of categorized test case to the dictionary
                    inputTestSuiteDict["RTCFM"].extend(tempTestSuite.RTCFMList)
                    inputTestSuiteDict["CFM"].extend(tempTestSuite.CFMList)
                    inputTestSuiteDict["RTSales"].extend(tempTestSuite.RTSalesList)
                    inputTestSuiteDict["Sales"].extend(tempTestSuite.SalesList)
                    #inputTestSuiteDict["NotExecuted"].append(tempTestSuite.NotExecuted) 
    
    #This function is used for inserting the element to the template.
    #This function takes the list element in the dictionary which corresponds to the determined category and retrieves data
    #The function reads the template and modify it and write the output file
    #Params: inputList: list element in the dictionary
    #        path: the template of test suite
    #        outputFileName: The desired output file name
    def insertElementToTemplate(self, inputList, path,outputFileName):
        #Instantiate the soup object
        soup = BeautifulSoup(open(path),"html.parser")
        #This string is the template for row inserted into the table of test suite template
        templateRowString = "<tr class='' bgcolor='#FFFFFF' style='display: table-row;'> <th><font size='2.5' face='Calibri' color='black' align='center'></font></th> <th><font size='2.5' face='Calibri' color='black' align='left'></font></th> <th><font size='2.5' face='Calibri' color='black' align='center' ><a></font></th> </tr>"
        #Retrieve table tag of the test suite template
        table = soup.find(id="table")
        #The pie chart teamplate string to be added under the table of test suite
        scriptChartString = "function drawChart(){var a=google.visualization.arrayToDataTable([['TestCase','Number of Test Case'],['PASS',passNumber],['FAIL',failNumber]]);new google.visualization.PieChart(document.getElementById('piechart')).draw(a,{title:'titleName',width:450,height:300,colors:['#00FA9A','#F08080'],is3D:!0,fontSize:13,backgroundColor:'#DCDCDC'})}google.charts.load('current',{packages:['corechart']}),google.charts.setOnLoadCallback(drawChart);"
        numberOfPass = 0
        #Iterate the input list of test cases
        #inputList: [[testcase1name,testcase1result,testcase1href],[testcase2name,testcase2result,testcase2href]...]
        #             _____data[0]_____data[1]_________data[2]___   ____data[0]_______data[1]_______data[2]____
        #                              index: 1                                       index: 2                
        for index,data in enumerate(inputList):
            #Transform the string row into the html row
            templateRow = BeautifulSoup(templateRowString,'html.parser').tr
            if data[1] == "PASS":
                #add class style to the template row
                templateRow["class"].append("hoverRowPass")
                #count the number of pass test case
                numberOfPass = numberOfPass + 1
            else:
                templateRow["class"].append("hoverRowFail")
            tableHeads = templateRow.findAll("th")
            #set the index number of test case in table row, because index starts at 0, then need to add 1
            tableHeads[0].font.string = str(index + 1)
            #set name of testcase in row of table
            tableHeads[1].font.string = data[0]
            #set result of testcase in row of table
            tableHeads[2].font.a.string = data[1]
            #set the href of test case in row of table
            tableHeads[2].font.a['href'] = data[2]
            #append row into the table of test suite
            table.append(templateRow)
        #Get the id of Summary table of test suite
        summary = soup.find(id="summary")
        tableHeadsSummary = summary.findAll("th")
        #Set value of Summary Table
        tableHeadsSummary[1].font.string = str(len(inputList))
        tableHeadsSummary[2].font.string = str(numberOfPass)
        tableHeadsSummary[3].font.string = str(len(inputList)-numberOfPass)
        #Insert Pie Chart under the table of test suite
        scriptChartString = scriptChartString.replace('passNumber',str(numberOfPass))
        scriptChartString = scriptChartString.replace('failNumber',str(len(inputList)-numberOfPass))
        scriptChartTag = soup.find(id="scriptChart")
        captionTag = soup.find("caption")
        captionText = captionTag.h1.font.text
        scriptChartString = scriptChartString.replace('titleName',captionText)
        scriptChartTag.string=scriptChartString
        #Write to the output testsuite file
        with open(outputFileName, "w",encoding="utf-8") as file:
                file.write(str(soup))
    #this function copies test cases and ini.html file from origin folder to destination folder
    #After copying, modifying the test case in the destination folder by invoking the modifyTestCaseReport function
    #Params: inputListOfElement: the list of categorized test case in the dictionary
    #        destination: destination folder
    def copyChildrenFilesTestSuite(self,inputListOfElements,destination):
        #Iterate the list element
        for testCaseElement in inputListOfElements:
            for root,dirs,files in os.walk(self.path,topdown=True):
                for name in files:
                    #Check the href name in the current file name and copy that file to the destination
                    if testCaseElement[2] in name:
                        shutil.copy2(os.path.join(root,name),destination)
                        self.modifyTestCaseReport(destination+testCaseElement[2])
                    elif "ini.html" in name:
                        shutil.copy2(os.path.join(root,name),destination)
    #This function is responsible for copying the screenshot folder from the origin folder to destination folder
    def copyScreenshotsFolder(self,destination):
        for root,dirs,files in os.walk(self.path,topdown=True):
            for name in dirs:
                if "screenshots" in name:
                    #Copy folder
                    copy_tree(os.path.join(root,name),destination)
    #This function is responsible for modifying the test case report
    #Params: inputTestCaseFile: the test case file need to be modified
    def modifyTestCaseReport(self,inputTestCaseFile):
        #Instantiate the soup object reprenseted for test case file
        soup = BeautifulSoup(open(inputTestCaseFile),"html.parser")
        tableTag = soup.find("table")
        tableTag['align'] = "center" 
        tableRows = soup.findAll("tr")
        #Iterate through table rows
        for row in tableRows:
            #For each row, get the columns
            column = row.findAll("td")
            if len(column) > 0:
                #the column contains the result of each step at the position 4 to the last
                resultColumn = column[len(column)-4]
                #if the result is fail,set background
                if resultColumn.text == "FAIL":
                    resultColumn['style'] = "background-color:#F08080"
                elif resultColumn.text == "PASS":
                    resultColumn['style'] = "background-color:#00FA9A"
                #delete unnecessary column in the test case report
                column[1].extract()
                column[2].extract()
                column[4].extract()
        with open(inputTestCaseFile, "w",encoding="utf-8") as file:
            file.write(str(soup))            
###############################################################################################################
 # This Class is responsible for getting data of TestSuite file
 # This Class reads the input Test Suite file and gathers the information of each row in table
 # Then, name of test case in row is checked and distinguished into 4 categories:"[RT]CFM","Sales","[RT]Sales","CFM"
 # In addition, the result of test case and href correspondings to that test case are also collected
 # After checked, row is appended to the corresponding category list
 # Params of contrsuctor: the input test suite file
 # ############################################################################################################# 
class TestSuite:
    def __init__(self,inputTestSuitePath):
        #open the input test suite file as a soup object
        self.soup = BeautifulSoup(open(inputTestSuitePath),'html.parser')
        #Initialize List of 4 categories
        self.RTCFMList = []
        self.RTSalesList = []
        self.CFMList = []
        self.SalesList = []
        self.NotExecuted = ""
        #extract Row in table and save it to list of each category
        self.extractElement()
       
    #This function is used for extract information of each row in table and save it to list of each category
    def extractElement(self):
        #find all table cell
        tableCells = self.soup.findAll("th")
        NotExecutedCell = self.soup.find(id="summary").findAll("a")
        #Categorize rows, the first element of the list appended is name of the test case, the second is the result
        #and the last is the href links to that test case
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
 # Params: inputMasterSuiteTemplate: the master suite template need to be modified
 #         inputTestSuiteDictionary: the Dictionary contains categorized test case of each test suite
 #         outputFileName: name of the desired output file
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
        if len(self.testSuiteDictionary["RTCFM"]) > 0:
            self.updateDataTestSet(self.testSetCFMRegressionID,"RTCFM","scriptChartCFMRegression","CFMRegressionPieChart","CFM Regression")
        if len(self.testSuiteDictionary["CFM"]) > 0:
            self.updateDataTestSet(self.testSetCFMSanityID,"CFM","scriptChartCFMSanity","CFMSanityPieChart","CFM Sanity")
        if len(self.testSuiteDictionary["RTSales"]) > 0:
            self.updateDataTestSet(self.testSetSalesRegressionID,"RTSales","scriptChartSalesRegression","SalesRegressionPieChart","Sales Regression")
        if len(self.testSuiteDictionary["Sales"]) > 0:
            self.updateDataTestSet(self.testSetSalesSanityID,"Sales","scriptChartSalesSanity","SalesSanityPieChart","Sales Sanity")
        self.updateDataTestSet(self.totalID,"Total","scriptChartTotal","totalPieChart","Total")
        #Write the modified MasterSuite template to the output file
        with open(outputFileName, "w",encoding="utf-8") as file:
            file.write(str(self.soup))

    #This function gathers the html element: numberOfTestCase,numberOfPassTestCase,numberOfFailTest,percentagePass and percentageFail
    # of MasterSuite template. The input keyDict need to be provided in order to distinguish the calculation of row
    # Total and Test Set Row.
    # Params: testSetID: the id of test set html element in the mastersuite template
    #         keyDict: the key in dictionary contains categorized test case
    #         scripChartID: the id of script html element in the mastersuite template, used for searching by soup
    #                       and insert the pie chart
    #         piechartID: the id of pie chart html element in the mastersuite template, used for replacing the 
    #                     piechart String in the scriptChartString
    #         titlePieChart: the title of piechart used for replacing the title string in the scriptChartString
    def updateDataTestSet(self,testSetID,keyDict,scriptChartID,piechartID,titlePieChart):
        #Get the HTML tableHead tag of each element from row
        numberOfTestCaseHTML = testSetID.findAll("th")[1]
        numberOfPassTestHTML = testSetID.findAll("th")[2]
        numberOfFailTestHTML = testSetID.findAll("th")[3]
        percentagePassHTML = testSetID.findAll("th")[5]
        percentageFailHTML = testSetID.findAll("th")[6]
        #Check if keyDict is Total then calculate number for row ToTal
        if keyDict == "Total":
            Total = self.total
            numberOfPass = self.totalPass
            numberOfFail = self.total - self.totalPass      
        else:
            #Get Value from Dictionary    
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
        #insert pie chart
        self.insertPieChart(titlePieChart,numberOfPass,numberOfFail,scriptChartID,piechartID)
    #This function will iterate through the value of each keyDict, with each value which is a list contains name of
    #test case, result of test case and href of test case, the number of pass test case is counted if there is a 
    #result of pass. The calculate total number of test case of one test set by calculate length of the value of each
    #keyDict.
    def getValueFromDictionary(self, keyDict):
        numberOfPass = 0
        for data in self.testSuiteDictionary[keyDict]:
            if data[1] == "PASS":
                numberOfPass = numberOfPass + 1
        return len(self.testSuiteDictionary[keyDict]),numberOfPass,  len(self.testSuiteDictionary[keyDict])-numberOfPass
    #This Class is used for insert Pie Chart to the template.    
    def insertPieChart(self,inputTitlePieChart,inputNumberOfPass,inputNumberOfFail,scriptChartID,piechartID):
        #If the input title pie chart is Total then use a pie chart with different size with legend 
        if inputTitlePieChart == "Total":
            scriptChartString = "function drawChart(){var a=google.visualization.arrayToDataTable([['TestCase','Number of Test Case'],['PASS',passNumber],['FAIL',failNumber]]);new google.visualization.PieChart(document.getElementById('piechart')).draw(a,{title:'titleName',titleTextStyle:{fontSize: 18},width:450,height:300,colors:['#00FA9A','#F08080'],is3D:!0,fontSize:15})}google.charts.load('current',{packages:['corechart']}),google.charts.setOnLoadCallback(drawChart);"
        else:
            #If the input title pie chart is other then use a pie chart with different size without legend
            scriptChartString = "function drawChart(){var a=google.visualization.arrayToDataTable([['TestCase','Number of Test Case'],['PASS',passNumber],['FAIL',failNumber]]);new google.visualization.PieChart(document.getElementById('piechart')).draw(a,{title:'titleName',width:270,height:270,colors:['#00FA9A','#F08080'],is3D:!0,fontSize:13,legend:'none'})}google.charts.load('current',{packages:['corechart']}),google.charts.setOnLoadCallback(drawChart);"
        #Replace the string with calculation data
        scriptChartString = scriptChartString.replace('passNumber',str(inputNumberOfPass))
        scriptChartString = scriptChartString.replace('failNumber',str(inputNumberOfFail))
        scriptChartString = scriptChartString.replace('piechart',piechartID)
        scriptChartString = scriptChartString.replace('titleName',inputTitlePieChart)
        #Find script chart ID and insert
        scriptChartTag = self.soup.find(id=scriptChartID)
        scriptChartTag.string=scriptChartString
    
    ##########################################################################################################
class TestReportUpdate(TestReport):
    def __init__(self,inputPathMainFolder,inputPathSubFile):
        #self.copy = 0
        #self.remove = 0
        #self.beforeUpdate = []
        #self.afterUpdate = []
        self.subTestSuiteDictionary = {"RTCFM":[],"RTSales":[],"CFM":[],"Sales":[]}
        self.testSuiteSummaryTables = {"RTCFM":[],"RTSales":[],"CFM":[],"Sales":[]}
        self.crawlingPath(inputPathSubFile,self.subTestSuiteDictionary)
        self.updateMainTestSuite("RTCFM","CFMRegression",inputPathMainFolder,self.subTestSuiteDictionary["RTCFM"],inputPathSubFile)
        self.updateMainTestSuite("CFM","CFMSanity",inputPathMainFolder,self.subTestSuiteDictionary["CFM"],inputPathSubFile)
        self.updateMainTestSuite("Sales","SalesSanity",inputPathMainFolder,self.subTestSuiteDictionary["Sales"],inputPathSubFile)
        self.updateMainTestSuite("RTSales","SalesRegression",inputPathMainFolder,self.subTestSuiteDictionary["RTSales"],inputPathSubFile)
        self.updateMasterSuite(inputPathMainFolder,self.testSuiteSummaryTables)
    #########################################################################################################
    def updateMainTestSuite(self,keyDict,mainTestSuiteName,inputPathMainFolder,inputTestCaseList,inputPathSubFile):
        #oldTestCases = []
        for root,dirs,files in os.walk(inputPathMainFolder,topdown=True):
            for name in files:
                if mainTestSuiteName in name:
                    soup = BeautifulSoup(open(os.path.join(root,name)),'html.parser')
                    tableCells = soup.findAll('th')
                    summaryTable = soup.find(id="summary")
                    summaryTableHeadList = summaryTable.findAll("th")
                    totalTestCase = int(summaryTableHeadList[1].text)
                    passTestCase = int(summaryTableHeadList[2].text)
                    failTestCase = int(summaryTableHeadList[3].text)
                    #count = 0
                    for cell in tableCells:
                        for data in inputTestCaseList:
                            if data[0] == cell.text:
                                #print("Sub: " + data[0] + " " + data[2] + " " + data[1])
                                #print("MainBefore: " +cell.text + " " + str(cell.find_next_sibling("th").a))
                                if data[1] == "PASS" and cell.find_next_sibling("th").a.text == "FAIL":
                                    cell.find_next_sibling("th").a.string = data[1]
                                    self.copyTestCasesSub2MainFolder(inputPathSubFile,inputPathMainFolder,mainTestSuiteName,data[2])
                                    self.removeOldTestCase(cell.find_next_sibling("th").a["href"],inputPathMainFolder)
                                    #self.beforeUpdate.append(cell.find_next_sibling("th").a["href"])
                                    #self.afterUpdate.append([data[0],data[2]])
                                    cell.find_next_sibling("th").a["href"] = data[2]
                                    cell.parent["class"] = "hoverRowPass"
                                    #print("MainAfter: " +cell.text + " " + str(cell.find_next_sibling("th").a))
                                    #print("_______________________________________________________")
                                    passTestCase = passTestCase + 1
                    #print(self.copy, self.remove)
                    failTestCase = totalTestCase - passTestCase
                    self.testSuiteSummaryTables[keyDict] = [passTestCase,failTestCase]
                    summaryTableHeadList[2].font.string = str(passTestCase)
                    summaryTableHeadList[3].font.string = str(failTestCase)
                    self.insertUpdatedPieChartTestSuite(soup,passTestCase,failTestCase)
                    with open(os.path.join(root,name), "w",encoding="utf-8") as file:
                        file.write(str(soup))
    #############################################################################################
    def copyTestCasesSub2MainFolder(self,locationSubFile,destinationMainFolder,mainTestSuiteName,testCaseName):
        destinationMainDir = ""
        for root, dirs, files in os.walk(destinationMainFolder,topdown=True):
            for name in files:
                if mainTestSuiteName in name:
                    destinationMainDir = root
        for root,dirs,files in os.walk(locationSubFile,topdown=True):
            for name in files:
                if testCaseName == name:
                    shutil.copy2(os.path.join(root,name),destinationMainDir)
                    #self.copy = self.copy + 1
                    self.modifyTestCaseReport(os.path.join(destinationMainDir,name))

    def removeOldTestCase(self,oldTestCaseName,destinationMainFolder):
        for root,dirs,files in os.walk(destinationMainFolder,topdown=True):
            for name in files:
                if oldTestCaseName == name:
                    #self.remove = self.remove + 1
                    os.remove(os.path.join(root,name))

    def insertUpdatedPieChartTestSuite(self,soupObject,numberOfPass,numberOfFail):
        scriptChartString = "function drawChart(){var a=google.visualization.arrayToDataTable([['TestCase','Number of Test Case'],['PASS',passNumber],['FAIL',failNumber]]);new google.visualization.PieChart(document.getElementById('piechart')).draw(a,{title:'titleName',width:450,height:300,colors:['#00FA9A','#F08080'],is3D:!0,fontSize:13,backgroundColor:'#DCDCDC'})}google.charts.load('current',{packages:['corechart']}),google.charts.setOnLoadCallback(drawChart);"
        scriptChartString = scriptChartString.replace('passNumber',str(numberOfPass))
        scriptChartString = scriptChartString.replace('failNumber',str(numberOfFail))
        scriptChartTag = soupObject.find(id="scriptChart")
        captionTag = soupObject.find("caption")
        captionText = captionTag.h1.font.text
        scriptChartString = scriptChartString.replace('titleName',captionText)
        scriptChartTag.string=scriptChartString
    
    def updateMasterSuite(self,inputPathMainFolder,inputDict):
        self.dataSet = inputDict
        for root,dirs,files in os.walk(inputPathMainFolder,topdown=True):
            for name in files:
                if "MasterSuite" in name:
                    masterSuiteFile = os.path.join(root,name)
        self.soup = BeautifulSoup(open(masterSuiteFile),"html.parser")
        testSetSalesSanityID = self.soup.find(id="testset1")
        testSetCFMSanityID = self.soup.find(id="testset2")
        testSetSalesRegressionID = self.soup.find(id="testset3")
        testSetCFMRegressionID = self.soup.find(id="testset4")
        totalID = self.soup.find(id="total")
        self.totalNumberOfPass = 0
        self.totalNumberOfFail = 0
        for key,value in inputDict.items():
            self.totalNumberOfPass = self.totalNumberOfPass + value[0]
            self.totalNumberOfFail = self.totalNumberOfFail + value[1]

        self.updateDataSet(testSetCFMRegressionID,"RTCFM","scriptChartCFMRegression","CFMRegressionPieChart","CFM Regression")
        self.updateDataSet(testSetCFMSanityID,"CFM","scriptChartCFMSanity","CFMSanityPieChart","CFM Sanity")
        self.updateDataSet(testSetSalesRegressionID,"RTSales","scriptChartSalesRegression","SalesRegressionPieChart","Sales Regression")
        self.updateDataSet(testSetSalesSanityID,"Sales","scriptChartSalesSanity","SalesSanityPieChart","Sales Sanity")
        self.updateDataSet(totalID,"Total","scriptChartTotal","totalPieChart","Total")
        with open(masterSuiteFile, "w",encoding="utf-8") as file:
            file.write(str(self.soup))
    def updateDataSet(self,testSetID,keyDict,scriptChartID,piechartID,titlePieChart):
        numberOfPassTestHTML = testSetID.findAll("th")[2]
        numberOfFailTestHTML = testSetID.findAll("th")[3]
        percentagePassHTML = testSetID.findAll("th")[5]
        percentageFailHTML = testSetID.findAll("th")[6]
        if keyDict == "Total":
            percentagePass = (self.totalNumberOfPass*100) // (self.totalNumberOfPass + self.totalNumberOfFail)
            percentageFail = 100 - percentagePass
            numberOfPassTestHTML.string = str(self.totalNumberOfPass)
            numberOfFailTestHTML.string = str(self.totalNumberOfFail)
            percentagePassHTML.string = str(percentagePass)+"%"
            percentageFailHTML.string = str(percentageFail)+"%"
            self.updatePieChart(titlePieChart,self.totalNumberOfPass,self.totalNumberOfFail,scriptChartID,piechartID)
        else:    
            numberOfPass = self.dataSet[keyDict][0]
            numberOfFail = self.dataSet[keyDict][1]
            percentagePass = (numberOfPass*100) // (numberOfPass + numberOfFail)
            percentageFail = 100 - percentagePass
            numberOfPassTestHTML.string = str(numberOfPass)
            numberOfFailTestHTML.string = str(numberOfFail)
            percentagePassHTML.string = str(percentagePass)+"%"
            percentageFailHTML.string = str(percentageFail)+"%"
            self.updatePieChart(titlePieChart,numberOfPass,numberOfFail,scriptChartID,piechartID)
    def updatePieChart(self,inputTitlePieChart,inputNumberOfPass,inputNumberOfFail,scriptChartID,piechartID):
            #If the input title pie chart is Total then use a pie chart with different size with legend 
        if inputTitlePieChart == "Total":
            scriptChartString = "function drawChart(){var a=google.visualization.arrayToDataTable([['TestCase','Number of Test Case'],['PASS',passNumber],['FAIL',failNumber]]);new google.visualization.PieChart(document.getElementById('piechart')).draw(a,{title:'titleName',titleTextStyle:{fontSize: 18},width:450,height:300,colors:['#00FA9A','#F08080'],is3D:!0,fontSize:15})}google.charts.load('current',{packages:['corechart']}),google.charts.setOnLoadCallback(drawChart);"
        else:
            #If the input title pie chart is other then use a pie chart with different size without legend
            scriptChartString = "function drawChart(){var a=google.visualization.arrayToDataTable([['TestCase','Number of Test Case'],['PASS',passNumber],['FAIL',failNumber]]);new google.visualization.PieChart(document.getElementById('piechart')).draw(a,{title:'titleName',width:270,height:270,colors:['#00FA9A','#F08080'],is3D:!0,fontSize:13,legend:'none'})}google.charts.load('current',{packages:['corechart']}),google.charts.setOnLoadCallback(drawChart);"
        #Replace the string with calculation data
        scriptChartString = scriptChartString.replace('passNumber',str(inputNumberOfPass))
        scriptChartString = scriptChartString.replace('failNumber',str(inputNumberOfFail))
        scriptChartString = scriptChartString.replace('piechart',piechartID)
        scriptChartString = scriptChartString.replace('titleName',inputTitlePieChart)
        #Find script chart ID and insert
        scriptChartTag = self.soup.find(id=scriptChartID)
        scriptChartTag.string=scriptChartString
        


        
                                



        



        

    

