from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
import time

url = 'http://faast.waterboards.ca.gov/Public_Interface/PublicPropSearchMain.aspx'
# headers = {
#     'HTTP_USER_AGENT': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.13) Gecko/2009073022 Firefox/3.0.13',
#     'HTTP_ACCEPT': 'text/html,application/xhtml+xml,application/xml; q=0.9,*/*; q=0.8',
#     'Content-Type': 'application/x-www-form-urlencoded'
# }

# get to appropriate page
driver = webdriver.Firefox()
driver.get(url)
link = driver.find_element_by_id("GotoSearch")
link.click()
mySelect = Select(driver.find_element_by_id("ContentPlaceHolder1_RfpDDL"))
my = mySelect.select_by_value('310')
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
	headers += th.text + ', '

# grab each row of data for pins' descriptions
containers = table.findAll('tr')[1:]

# write each row of data to csv file
filename = 'pin_descriptions.csv'
f = open(filename, 'w')

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
			#need to fix
			data += ',"' + overview_container.find("td", {"class": "right_column"}).text.strip().replace('\n', '').replace(',','|') + '"'
		else:
			oDescription = overview_container.find("td", {"class": "left_column"})
			if (oDescription != None):
				label = oDescription.text.strip()[:-1]
				if (headerBool):
					headers += label + ','
				data += ',"' + overview_container.find("td", {"class": "right_column"}).text.strip().replace('\n', '').replace(',','|') + '"'

	
	# FUNDING
	funding = detail_soup.find(id="ContentPlaceHolder1_PropGeneralInfo_FundProgramReadGV")
	funding_labels = funding.tbody.tr.findAll('th')
	for th in funding_labels:
		if (headerBool):
			headers += th.text + ','
	funding_containers = funding.findAll('tr')[1:]
	program_data = ""
	applied_data = ""
	amount_data = ""
	for funding_container in funding_containers:
		funding_description = funding_container.findAll('td')
		program_data += funding_description[0].text.strip() + "/"
		applied_data += funding_description[1].text.strip() + "/"
		amount_data += funding_description[2].text.strip() + "/"
	data += ',"' + program_data[:-1] + '","' + applied_data[:-1] + '","' + amount_data[:-1] + '"'


	# MANAGEMENT
	management = detail_soup.find(id="ContentPlaceHolder1_PropGeneralInfo_ProjectMgmtDetailsGV")
	management_labels = management.tbody.tr.findAll('th')
	for th in management_labels:
		if (headerBool):
			headers += th.text + ','
	management_containers = management.findAll('tr')[1:]
	role = ""
	first_name = ""
	last_name = ""
	phone = ""
	fax = ""
	email = ""
	for management_container in management_containers:
		management_description = management_container.findAll('td')
		role += management_description[0].text.strip() + "/"
		first_name += management_description[1].text.strip() + "/"
		last_name += management_description[2].text.strip() + "/"
		phone += management_description[3].text.strip() + "/"
		fax += management_description[4].text.strip() + "/"
		email += management_description[5].text.strip() + "/"
	data += ',"' + role[:-1] + '","' + first_name[:-1] + '","' + last_name[:-1] + '","' + phone[:-1] + '","' + fax[:-1] + '","' + email[:-1] + '"'

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
			headers += 'Person Submitting ' + th.text.strip()[:-1] + ','
	person_container = person.findAll('div', {'class': 'DivTablColumnright'})
	person_name = person_container[0].text.strip()
	#need to fix for fax
	person_phone = person_container[1].text.strip()
	person_address = person_container[2].text.strip()
	data += ',"' + person_name + '","' + person_phone + '","' + person_address + '"'

	# LEGISLATIVE INFORMATION
	legislative = detail_soup.find(id='ContentPlaceHolder1_PropAddInfo_LegislativeInfoGV')
	legislative_labels = legislative.tbody.tr.findAll('th')
	for th in legislative_labels:
		if (headerBool):
			headers += th.text + ','
	legislative_containers = legislative.findAll('tr')[1:]
	district = ""
	primary = ""
	additional_districts = ""
	for legislative_container in legislative_containers:
		legislative_description = legislative_container.findAll('td')
		district += legislative_description[0].text.strip() + "/"
		primary += legislative_description[1].text.strip() + "/"
		additional_districts += legislative_description[2].text.strip() + "/"
	data += ',"' + district[:-1] + '","' + primary[:-1] + '","' + additional_districts[:-1] + '"'

	# CONTACTS
	contacts = detail_soup.find(id="ContentPlaceHolder1_PropAddInfo_AgencyContactListGV")
	contacts_labels = contacts.tbody.tr.findAll('th')
	for th in contacts_labels:
		if (headerBool):
			headers += th.text + ','
	contacts_containers = contacts.findAll('tr')[1:]
	contact_data = ""
	contact_name = ""
	contact_phone = ""
	contact_email = ""
	for contacts_container in contacts_containers:
		contacts_description = contacts_container.findAll('td')
		if (len(contacts_description) > 1):
			contact_data += contacts_description[0].text.strip() + "/"
			contact_name += contacts_description[1].text.strip() + "/"
			contact_phone += contacts_description[2].text.strip() + "/"
			contact_email += contacts_description[3].text.strip() + "/"
	data += ',"' + contact_data[:-1] + '","' + contact_name[:-1] + '","' + contact_phone[:-1] + '","' + contact_email[:-1] + '"'

	# COOPERATING ENTITIES
	entities = detail_soup.find(id="ContentPlaceHolder1_PropAddInfo_CoopEntityGV")
	entities_labels = entities.tbody.tr.findAll('th')
	for th in entities_labels:
		if (headerBool):
			headers += th.text + ','
	entities_containers = entities.findAll('tr')[1:]
	entities_data = ""
	entities_role = ""
	entities_name = ""
	entities_phone = ""
	entities_email = ""
	for entities_container in entities_containers:
		entities_description = entities_container.findAll('td')
		if (len(entities_description) > 1):
			entities_data += entities_description[0].text.strip() + "/"
			entities_role += entities_description[1].text.strip() + "/"
			entities_name += entities_description[2].text.strip() + "/"
			entities_phone += entities_description[3].text.strip() + "/"
			entities_email += entities_description[4].text.strip() + "/"
	data += ',"' + entities_data[:-1] + '","' + entities_role[:-1] + '","' + entities_name[:-1] + '","' + entities_phone[:-1] + '","' + entities_email[:-1] + '"'

	driver.execute_script("window.history.go(-1)")

	if (headerBool):
		f.write(headers[:-1] + '\n')
		headerBool = False

	f.write(data + '\n')

f.close()