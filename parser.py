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

	# scrape info from first page
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
	data = pin + ',' + agreement + ',"' + proposal + '","' + applicant + '","' + county + '","' + watershed + '","' + rwqcb + '","' + reqfunds + '","' + status

	# click through to form
	time.sleep(0.5)
	driver.find_element_by_link_text(pin).click()
	detail_doc = driver.page_source
	detail_soup = BeautifulSoup(detail_doc, 'html.parser')
	#print(detail_soup.prettify())

	# scrape info from second page
	overview = detail_soup.find(id="ContentPlaceHolder1_PropGeneralInfo_ProposalGeneralInfoFV")
	overview_containers = overview.find('tr').findAll('tr')

	for overview_container in overview_containers:
		oDescription = overview_container.find("td", {"class": "left_column1"})
		if (oDescription != None):
			label = oDescription.text.strip()[:-1]
			if (headerBool):
				headers += label + ','
			if "Latitude" not in label:
				data += ',"' + overview_container.find("td", {"class": "right_column"}).text.strip() + '"'
			else:
				data += ',"' + overview_container.find("td", {"class": "right_column"}).text.strip()[:4] + '"'
		else:
			oDescription = overview_container.find("td", {"class": "left_column"})
			if (oDescription != None):
				label = oDescription.text.strip()[:-1]
				if (headerBool):
					headers += label + ','
				if "Latitude" not in label:
					data += ',"' + overview_container.find("td", {"class": "right_column"}).text.strip() + '"'
				else:
					data += ',"' + overview_container.find("td", {"class": "right_column"}).text.strip()[:4] + '"'

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
		program_data += funding_description[0].text + " "
		applied_data += funding_description[1].text + " "
		amount_data += funding_description[2].text + " "
	data = data + "," + program_data.strip() + "," + applied_data.strip() + "," + amount_data.strip()

	driver.execute_script("window.history.go(-1)")

	if (headerBool):
		f.write(headers[:-2] + '\n')
		headerBool = False

	f.write(data + '\n')

f.close()
