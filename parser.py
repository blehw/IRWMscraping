from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
import time
import re

# TODO:
# 1. Add link for call back and new pin
# 2. Latitude/longitude issue and email/fax

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

def pageScrape(page, driver, fileName, round_num, step_num):
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

	html_doc = driver.page_source
	page_soup = BeautifulSoup(html_doc, 'html.parser')
	table = page_soup.find(id="ContentPlaceHolder1_PublicProposalSearchGV")

	# grab headers for data
	labels = table.tbody.tr.findAll('th')
	headers = ''
	for th in labels:
		headers += '"' + th.text + '",'

	# grab each row of data for pins' descriptions
	containers = table.findAll('tr')[1:]

	headerBool = True

	for container in containers:

		# PIN DESCRIPTION (first page)
		pin = container.a.text
		description = container.findAll('td')[1:]
		agreement = description[0].text.strip()
		proposal = description[1].text.strip()
		applicant = description[2].text.strip()
		county = description[3].text.strip()
		watershed = description[4].text.strip()
		rwqcb = description[5].text.strip()
		reqfunds = description[6].text.strip()
		status = description[7].text.strip()
		data = pin + ',' + agreement + ',"' + proposal + '","' + applicant + '","' + county + '","' + watershed + '","' + rwqcb + '","' + reqfunds + '","' + status + '"'

		# click through to form
		time.sleep(0.75)
		driver.find_element_by_link_text(pin).click()
		detail_doc = driver.page_source
		detail_soup = BeautifulSoup(detail_doc, 'html.parser')
		#print(detail_soup.prettify())

		
		# APPLICATION OVERVIEW (second page)
		overview = detail_soup.find(id="ContentPlaceHolder1_PropGeneralInfo_ProposalGeneralInfoFV")
		overview_containers = overview.find('tr').findAll('tr') 

		for overview_container in overview_containers:
			oDescription = overview_container.find("td", {"class": "left_column1"})
			if (oDescription != None):
				label = oDescription.text.strip()[:-1]
				if (headerBool):
					headers += label + ','
				#need to fix
				data += ',"' + overview_container.find("td", {"class": "right_column"}).text.strip().replace('\n', '').replace('"',"'") + '"'
			else:
				oDescription = overview_container.find("td", {"class": "left_column"})
				if (oDescription != None):
					label = oDescription.text.strip()[:-1]
					if (headerBool):
						headers += label + ','
					data += ',"' + overview_container.find("td", {"class": "right_column"}).text.strip().replace('\n', '').replace('"',"'") + '"'

		
		# FUNDING
		newHeaders = scrapeHeaders('ContentPlaceHolder1_PropGeneralInfo_FundProgramReadGV', detail_soup, '')
		headers += newHeaders
		data += scrapeData('ContentPlaceHolder1_PropGeneralInfo_FundProgramReadGV', detail_soup, newHeaders.count(','))

		# MANAGEMENT
		newHeaders = scrapeHeaders('ContentPlaceHolder1_PropGeneralInfo_ProjectMgmtDetailsGV', detail_soup, 'Manager')
		headers += newHeaders
		data += scrapeData('ContentPlaceHolder1_PropGeneralInfo_ProjectMgmtDetailsGV', detail_soup, newHeaders.count(','))

		# APPLICANT INFORMATION
		applicant = detail_soup.find(id="ContentPlaceHolder1_PropGeneralInfo_AppOrganizationInfoFV")
		applicant_labels = applicant.tbody.tr.td.findAll('div', {'class' : 'DivTablColumnleft'})
		for th in applicant_labels:
			if (headerBool):
				headers += 'Applicant ' + th.text.strip()[:-1] + ','
		applicant_container = applicant.findAll('div', {'class': 'DivTablColumnright'})
		applicant_name = applicant_container[0].text.strip()
		applicant_division = applicant_container[1].text.strip()
		applicant_address = applicant_container[2].text.strip()
		data += ',"' + applicant_name + '","' + applicant_division + '","' + applicant_address + '"'

		# PERSON SUBMITTING INFORMATION
		person = detail_soup.find(id='ContentPlaceHolder1_PropGeneralInfo_SubmittingUserInfoFV')
		person_labels = person.tbody.tr.td.findAll('div', {'class' : 'DivTablColumnleft'})
		for th in person_labels:
			if (headerBool):
				headers += th.text.strip()[:-1] + ','
		person_container = person.findAll('div', {'class': 'DivTablColumnright'})
		person_name = person_container[0].text.strip()
		#need to fix for fax
		person_phone = person_container[1].text.strip()
		person_address = person_container[2].text.strip()
		data += ',"' + person_name + '","' + person_phone + '","' + person_address + '"'

		# LEGISLATIVE INFORMATION
		newHeaders = scrapeHeaders('ContentPlaceHolder1_PropAddInfo_LegislativeInfoGV', detail_soup, '')
		headers += newHeaders
		data += scrapeData('ContentPlaceHolder1_PropAddInfo_LegislativeInfoGV', detail_soup, newHeaders.count(','))

		# CONTACTS
		# need if statement
		newHeaders = scrapeHeaders('ContentPlaceHolder1_PropAddInfo_AgencyContactListGV', detail_soup, 'Contact')
		headers += newHeaders
		data += scrapeData('ContentPlaceHolder1_PropAddInfo_AgencyContactListGV', detail_soup, newHeaders.count(','))

		# COOPERATING ENTITIES
		newHeaders = scrapeHeaders('ContentPlaceHolder1_PropAddInfo_CoopEntityGV', detail_soup, 'Cooperating Entity')
		headers += newHeaders
		data += scrapeData('ContentPlaceHolder1_PropAddInfo_CoopEntityGV', detail_soup, newHeaders.count(','))

		# Questionnaire
		numQuestions = 0
		questionnaire_data = ''
		questionnaire_headers = detail_soup.findAll(id=re.compile('^ContentPlaceHolder1_PropAnswerSheet_QuestionsPreviewReadOnly_QText_'))
		for th in questionnaire_headers:
			if (headerBool):
				headers += '"' + th.text.strip() + '",'
				numQuestions += 1
		currQuestion = 0
		data += ','
		questionnaire_data = detail_soup.findAll('span', {'id' : re.compile('^ContentPlaceHolder1_PropAnswerSheet_QuestionsPreviewReadOnly_')})
		newData = '"'
		for d in questionnaire_data:
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
		if (newData != '"'):
			data += newData[:-1] + '",'
		else:
			data += ','

		driver.execute_script("window.history.go(-1)")

		if (headerBool):
			fileName.write(headers + 'Round,Step' + '\n')
			headerBool = False

		fileName.write(data + str(round_num) + ',' + str(step_num) + '\n')

driver = webdriver.Firefox()
r1 = open('pin_descriptions_r1.csv', 'w')
r1s1 = open('pin_descriptions_r1s1.csv', 'w')
r1s2 = open('pin_descriptions_r1s2.csv', 'w')
r2s1 = open('pin_descriptions_r2s1.csv', 'w')
r2s2 = open('pin_descriptions_r2s2.csv', 'w')

# Round 1
pageScrape('310', driver, r1, 1, '')

# Round 1, Step 1
pageScrape('330', driver, r1s1, 1, 1)

# Round 1, Step 2
pageScrape('429', driver, r1s2, 1, 2)

# Round 2, Step 1
pageScrape('509', driver, r2s1, 2, 1)

# Round 2, Step 2
pageScrape('629', driver, r2s2, 2, 2)

r1.close()
r1s1.close()
r1s2.close()
r2s1.close()
r2s2.close()