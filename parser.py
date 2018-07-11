from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
import time
import re

# TODO:
# 1. Scrape questionnaire (insert into end of pageScrape function)
# 2. Distinguish phone/email etc...
# 3. Latitude/longitude issue?

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
		applicant_title = description[2].text.strip()
		county = description[3].text.strip()
		watershed = description[4].text.strip()
		rwqcb = description[5].text.strip()
		reqfunds = description[6].text.strip()
		status = description[7].text.strip()
		data = pin + ',' + agreement + ',"' + proposal + '","' + applicant_title + '","' + county + '","' + watershed + '","' + rwqcb + '","' + reqfunds + '","' + status + '"'

		# click through to form
		time.sleep(0.5)
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
<<<<<<< HEAD
				if 'Latitude' in label:
					if (headerBool):
						headers += 'Longitude,'
					coordinates = overview_container.find("td", {"class": "right_column"}).text.strip().replace('\n', '').replace('"',"'").split('Longitude:')
					data += ',"' + coordinates[0].strip() + '","' + coordinates[1].strip() + '"'
				else:
					data += ',"' + overview_container.find("td", {"class": "right_column"}).text.strip().replace('\n', '').replace('"',"'") + '"'
=======
				#need to fix
				data += ',"' + overview_container.find("td", {"class": "right_column"}).text.strip().replace('\n', '').replace(',','|') + '"'
			else:
				oDescription = overview_container.find("td", {"class": "left_column"})
				if (oDescription != None):
					label = oDescription.text.strip()[:-1]
					if (headerBool):
						headers += label + ','
					data += ',"' + overview_container.find("td", {"class": "right_column"}).text.strip().replace('\n', '').replace(',','|') + '"'

>>>>>>> 8fc296204330735d7b9a5bb63bf1baf64d56d94c
		
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
				if 'Submitter Phone' in th.text.strip()[:-1]:
					headers += 'Submitter Fax,'
		person_container = person.findAll('div', {'class': 'DivTablColumnright'})
		person_name = person_container[0].text.strip()
		person_phone_fax =  person_container[1].text.strip().split('Fax:')
		person_address = person_container[2].text.strip()
		data += ',"' + person_name + '","' + person_phone_fax[0] + '","' + person_phone_fax[1] + '","' + person_address + '"'

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
		questionnaire_data = ''
		questionnaire_headers = detail_soup.findAll(id=re.compile('^ContentPlaceHolder1_PropAnswerSheet_QuestionsPreviewReadOnly_QText_'))
		for th in questionnaire_headers:
			if (headerBool):
				headers += '"' + th.text.strip() + '",'
		questionnaire_data = detail_soup.findAll('span', {'id' : re.compile('^ContentPlaceHolder1_PropAnswerSheet_QuestionsPreviewReadOnly_')})
		for d in questionnaire_data:
			newD = str(d).replace('ContentPlaceHolder1_PropAnswerSheet_QuestionsPreviewReadOnly_', '')
			if 'Ans' in str(newD):
				if (d.text.strip() != ''):
					data += ',"' + d.text.strip() + '"'

		driver.execute_script("window.history.go(-1)")

<<<<<<< HEAD
		if (round_num == 1 and step_num == 1) or (round_num == 2 and step_num == 1):
			driver.get(url)
			link = driver.find_element_by_id("GotoSearch")
			link.click()
			mySelect = Select(driver.find_element_by_id("ContentPlaceHolder1_RfpDDL"))
			if round_num == 1 and step_num == 1:
				my = mySelect.select_by_value('429')
			else:
				my = mySelect.select_by_value('629')
			wait = WebDriverWait(driver, 300)
			search = driver.find_element_by_id("ContentPlaceHolder1_PublicSearchBtn")
			search.click()

			new_html_doc = driver.page_source
			new_page_soup = BeautifulSoup(new_html_doc, 'html.parser')
			new_table = new_page_soup.find(id="ContentPlaceHolder1_PublicProposalSearchGV")

			# grab each row of data for pins' descriptions
			new_containers = new_table.findAll('tr')[1:]

			calledBack = False
			for new_container in new_containers:
				new_description = new_container.findAll('td')[1:]
				new_applicant = new_description[2].text.strip()
				if new_applicant == applicant_title:
					print(proposal)
					new_pin = new_container.a.text
					if (headerBool):
						fileName.write(headers + 'Round,Step,Called Back?,Step 2 Pin #' + '\n')
						headerBool = False
					fileName.write(data + str(round_num) + ',' + str(step_num) + ',Yes,' + new_pin + '\n')
					calledBack = True
			if (calledBack != True):
				if (headerBool):
					fileName.write(headers + 'Round,Step,Called Back?,Step 2 Pin #' + '\n')
					headerBool = False
				fileName.write(data + str(round_num) + ',' + str(step_num) + ',No,' + '\n')

			driver.get(url)
			link = driver.find_element_by_id("GotoSearch")
			link.click()
			mySelect = Select(driver.find_element_by_id("ContentPlaceHolder1_RfpDDL"))
			my = mySelect.select_by_value(page)
			wait = WebDriverWait(driver, 300)
			search = driver.find_element_by_id("ContentPlaceHolder1_PublicSearchBtn")
			search.click()
		else:
			if (headerBool):
				fileName.write(headers + 'Round,Step' + '\n')
				headerBool = False

			fileName.write(data + str(round_num) + ',' + str(step_num) + '\n')
=======
		if (headerBool):
			f.write(headers[:-1] + ',Round,Step' + '\n')
			headerBool = False

		f.write(data + ',' + str(round_num) + ',' + str(step_num) + '\n')
>>>>>>> 8fc296204330735d7b9a5bb63bf1baf64d56d94c

driver = webdriver.Firefox()
fname = 'pin_descriptions.csv'
f = open(fname, 'w')

# Round 1
<<<<<<< HEAD
# pageScrape('310', driver, r1, 1, '')

# Round 1, Step 1
# pageScrape('330', driver, r1s1, 1, 1)

# Round 1, Step 2
# pageScrape('429', driver, r1s2, 1, 2)
=======
pageScrape('310', driver, f, 1, '')

# Round 1, Step 1
pageScrape('330', driver, f, 1, 1)

# Round 1, Step 2
pageScrape('429', driver, f, 1, 2)
>>>>>>> 8fc296204330735d7b9a5bb63bf1baf64d56d94c

# Round 2, Step 1
pageScrape('509', driver, f, 2, 1)

# Round 2, Step 2
<<<<<<< HEAD
# pageScrape('629', driver, r2s2, 2, 2)
=======
pageScrape('629', driver, f, 2, 2)

>>>>>>> 8fc296204330735d7b9a5bb63bf1baf64d56d94c

f.close()