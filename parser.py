from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
import time
import re

'''
To use, the most recent version of Firefox and the following need to be installed:

$pip install selenium
$pip install beautifulsoup4
$brew install geckodriver
$brew tap homebrew/cask

Then, run:
$python parser.py
'''

def scrapeHeaders(tableName, soup, title):
	table = soup.find(id=tableName)
	labels = table.tbody.tr.findAll('th')
	headers = ""
	for th in labels:
		if title != None:
			headers += title + ' '
		headers += th.text + ','
	return headers

def scrapeData(tableName, soup, numFields):
	table = soup.find(id=tableName)
	containers = table.findAll('tr')[1:]
	data = []
	initialize = True
	for i in range(0, len(containers)):
		description = containers[i].findAll('td')
		if (initialize):
			for j in range(0, len(description)):
				data.append('')
			initialize = False
		for j in range(0, len(description)):
			data[j] += description[j].text.strip() + "/"
	dataStr = ''
	for i in range(0, numFields):
		if (i < len(data)):
			dataStr += ',"' + data[i][:-1] + '"'
		else:
			dataStr += ','
	return dataStr

def pageScrape(page, driver, fileName, roundNum, stepNum):
	url = 'http://faast.waterboards.ca.gov/Public_Interface/PublicPropSearchMain.aspx'

	# get to appropriate page
	driver.get(url)
	link = driver.find_element_by_id("GotoSearch")
	link.click()
	mySelect = Select(driver.find_element_by_id("ContentPlaceHolder1_RfpDDL"))
	my = mySelect.select_by_value(page)
	wait = WebDriverWait(driver, 300)
	search = driver.find_element_by_id("ContentPlaceHolder1_PublicSearchBtn")
	search.click()

	htmlDoc = driver.page_source
	pageSoup = BeautifulSoup(htmlDoc, 'html.parser')
	table = pageSoup.find(id="ContentPlaceHolder1_PublicProposalSearchGV")

	# grab headers for data
	labels = table.tbody.tr.findAll('th')
	headers = ''
	for th in labels:
		headers += '"' + th.text + '",'

	# grab each row of data for pins' descriptions
	containers = table.findAll('tr')[1:]

	headerBool = True

	for container in containers:

		# pin description (first page)
		pin = container.a.text
		description = container.findAll('td')[1:]
		agreement = description[0].text.strip()
		proposal = description[1].text.strip()
		applicantTitle = description[2].text.strip()
		county = description[3].text.strip()
		watershed = description[4].text.strip()
		rwqcb = description[5].text.strip()
		reqfunds = description[6].text.strip()
		status = description[7].text.strip()
		data = pin + ',' + agreement + ',"' + proposal + '","' + applicantTitle + '","' + county + '","' + watershed + '","' + rwqcb + '","' + reqfunds + '","' + status + '"'

		# click through to form
		time.sleep(0.75)
		driver.find_element_by_link_text(pin).click()
		detailDoc = driver.page_source
		detailSoup = BeautifulSoup(detailDoc, 'html.parser')
		
		# application overview (second page)
		overview = detailSoup.find(id="ContentPlaceHolder1_PropGeneralInfo_ProposalGeneralInfoFV")
		overviewContainers = overview.find('tr').findAll('tr') 

		for overviewContainer in overviewContainers:
			oDescription = overviewContainer.find("td", {"class": "left_column1"})
			if (oDescription != None):
				label = oDescription.text.strip()[:-1]
				if (headerBool):
					headers += label + ','
				if 'Latitude' in label:
					if (headerBool):
						headers += 'Longitude,'
					coordinates = overviewContainer.find("td", {"class": "right_column"}).text.strip().replace('\n', '').replace('"',"'").split('Longitude:')
					data += ',"' + coordinates[0].strip() + '","' + coordinates[1].strip() + '"'
				else:
					data += ',"' + overviewContainer.find("td", {"class": "right_column"}).text.strip().replace('\n', '').replace('"',"'") + '"'
		
		# funding
		newHeaders = scrapeHeaders('ContentPlaceHolder1_PropGeneralInfo_FundProgramReadGV', detailSoup, '')
		headers += newHeaders
		data += scrapeData('ContentPlaceHolder1_PropGeneralInfo_FundProgramReadGV', detailSoup, newHeaders.count(','))

		# management
		newHeaders = scrapeHeaders('ContentPlaceHolder1_PropGeneralInfo_ProjectMgmtDetailsGV', detailSoup, 'Manager')
		headers += newHeaders
		data += scrapeData('ContentPlaceHolder1_PropGeneralInfo_ProjectMgmtDetailsGV', detailSoup, newHeaders.count(','))

		# applicant information
		applicant = detailSoup.find(id="ContentPlaceHolder1_PropGeneralInfo_AppOrganizationInfoFV")
		applicantLabels = applicant.tbody.tr.td.findAll('div', {'class' : 'DivTablColumnleft'})
		for th in applicantLabels:
			if (headerBool):
				headers += 'Applicant ' + th.text.strip()[:-1] + ','
		applicantContainer = applicant.findAll('div', {'class': 'DivTablColumnright'})
		applicantName = applicantContainer[0].text.strip()
		applicantDivision = applicantContainer[1].text.strip()
		applicantAddress = applicantContainer[2].text.strip()
		data += ',"' + applicantName + '","' + applicantDivision + '","' + applicantAddress + '"'

		# person submitting information
		person = detailSoup.find(id='ContentPlaceHolder1_PropGeneralInfo_SubmittingUserInfoFV')
		personLabels = person.tbody.tr.td.findAll('div', {'class' : 'DivTablColumnleft'})
		for th in personLabels:
			if (headerBool):
				headers += th.text.strip()[:-1] + ','
				if 'Submitter Phone' in th.text.strip()[:-1]:
					headers += 'Submitter Fax,'
		personContainer = person.findAll('div', {'class': 'DivTablColumnright'})
		personName = personContainer[0].text.strip()
		personPhoneFax =  personContainer[1].text.strip().split('Fax:')
		personAddress = personContainer[2].text.strip()
		data += ',"' + personName + '","' + personPhoneFax[0] + '","' + personPhoneFax[1] + '","' + personAddress + '"'

		# legislative information
		newHeaders = scrapeHeaders('ContentPlaceHolder1_PropAddInfo_LegislativeInfoGV', detailSoup, '')
		headers += newHeaders
		data += scrapeData('ContentPlaceHolder1_PropAddInfo_LegislativeInfoGV', detailSoup, newHeaders.count(','))

		# contacts
		newHeaders = scrapeHeaders('ContentPlaceHolder1_PropAddInfo_AgencyContactListGV', detailSoup, 'Contact')
		headers += newHeaders
		data += scrapeData('ContentPlaceHolder1_PropAddInfo_AgencyContactListGV', detailSoup, newHeaders.count(','))

		# cooperating entities
		newHeaders = scrapeHeaders('ContentPlaceHolder1_PropAddInfo_CoopEntityGV', detailSoup, 'Cooperating Entity')
		headers += newHeaders
		data += scrapeData('ContentPlaceHolder1_PropAddInfo_CoopEntityGV', detailSoup, newHeaders.count(','))

		# questionnaire
		numQuestions = 0
		questionnaireData = ''
		questionnaireHeaders = detailSoup.findAll(id=re.compile('^ContentPlaceHolder1_PropAnswerSheet_QuestionsPreviewReadOnly_QText_'))
		for th in questionnaireHeaders:
			if (headerBool):
				headers += '"' + th.text.strip() + '",'
				numQuestions += 1
		currQuestion = 0
		data += ','
		questionnaireData = detailSoup.findAll('span', {'id' : re.compile('^ContentPlaceHolder1_PropAnswerSheet_QuestionsPreviewReadOnly_')})
		newData = '"'
		for d in questionnaireData:
			newD = str(d.get('id')).replace('ContentPlaceHolder1_PropAnswerSheet_QuestionsPreviewReadOnly_', '')
			if 'Ans' in str(newD) and str(newD).endswith(str(currQuestion + 1)):
				currQuestion += 1
				if (newData != '"'):
					data += newData[:-1] + '",'
				else:
					data += ','
				newData = '"'
			if 'Ans' in str(newD) and str(newD).endswith(str(currQuestion)):
				if (d.text.strip() != ''):
					newData += d.text.strip().replace('"',"'") + '/'
					if (roundNum == 1 and stepNum == 2) or (roundNum == 2 and stepNum == 2):
						prevPins = 0
						if (roundNum == 1 and stepNum == 2):
							prevPins = 3
						else:
							prevPins = 4
						if (currQuestion == prevPins) and ('Descriptive' in str(newD)):
							step1Pins = re.findall(r'\d+', d.text.strip())
							for s in step1Pins:
								if (len(s) >= 4):
									if (roundNum == 1 and stepNum == 2):
										r1callback[s] = pin
									else:
										r2callback[s] = pin
		if (newData != '"'):
			data += newData[:-1] + '",'
		else:
			data += ','

		if (roundNum == 1 and stepNum == 1) or (roundNum == 2 and stepNum == 1):
			callbackPins = {}
			if (roundNum == 1 and stepNum == 1):
				callbackPins = r1callback
			else:
				callbackPins = r2callback
			if pin in callbackPins:
				if (headerBool):
					fileName.write(headers + 'Round,Step,Called Back?,Step 2 Pin #' + '\n')
					headerBool = False
				fileName.write(data + str(roundNum) + ',' + str(stepNum) + ',Yes,' + callbackPins.get(pin) + '\n')
			else:
				if (headerBool):
					fileName.write(headers + 'Round,Step,Called Back?,Step 2 Pin #' + '\n')
					headerBool = False
				fileName.write(data + str(roundNum) + ',' + str(stepNum) + ',No,' + '\n')
		else:
			if (headerBool):
				fileName.write(headers + 'Round,Step' + '\n')
				headerBool = False
			fileName.write(data + str(roundNum) + ',' + str(stepNum) + '\n')

		driver.execute_script("window.history.go(-1)")

driver = webdriver.Firefox()
r1 = open('pin_descriptions_r1.csv', 'w')
r1s1 = open('pin_descriptions_r1s1.csv', 'w')
r1s2 = open('pin_descriptions_r1s2.csv', 'w')
r2s1 = open('pin_descriptions_r2s1.csv', 'w')
r2s2 = open('pin_descriptions_r2s2.csv', 'w')

r1callback = {}
r2callback = {}

# Round 1
pageScrape('310', driver, r1, 1, '')

# Round 1, Step 2
pageScrape('429', driver, r1s2, 1, 2)

# Round 1, Step 1
pageScrape('330', driver, r1s1, 1, 1)

# Round 2, Step 2
pageScrape('629', driver, r2s2, 2, 2)

# Round 2, Step 1
pageScrape('509', driver, r2s1, 2, 1)

r1.close()
r1s1.close()
r1s2.close()
r2s1.close()
r2s2.close()