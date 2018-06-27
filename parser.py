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

  #scrape info from first page
  pin = container.a.text
  description = container.findAll('td')[1:]
  agreement = description[0].text.strip()
  proposal = description[1].text
  applicant = description[2].text
  county = description[3].text
  watershed = description[4].text
  rwqcb = description[5].text
  reqfunds = description[6].text
  status = description[7].text

  #click through to form
  time.sleep(0.5)
  driver.find_element_by_link_text(pin).click()
  detail_doc = driver.page_source
  detail_soup = BeautifulSoup(detail_doc, 'html.parser')
  #print(detail_soup.prettify())

  #scrape info from second page
  overview = detail_soup.find(id="ContentPlaceHolder1_PropGeneralInfo_ProposalGeneralInfoFV")
  overview_containers = overview.find('tr').findAll('tr')
  data = pin + ',' + agreement + ',' + proposal.replace(',', '|') + ',' + applicant.replace(',', '|') + ',' + county.replace(',', '|') + ',' + watershed.replace(',', '|') + ',' + rwqcb.replace(',', '|') + ',' + reqfunds.replace(',', '|') + ',' + status + '\n'
  for overview_container in overview_containers:
  	oDescription = overview_container.find("td", {"class": "left_column1"})
  	if (oDescription != None):
  		label = oDescription.text.strip()[:-1]
  		headers = headers + ", " + label
  		data = data + ", " + overview_container.find("td", {"class": "right_column"}).text.strip()[:-1].replace(',', '|')
  	else:
  		oDescription = overview_container.find("td", {"class": "left_column"})
  		if (oDescription != None):
  			label = oDescription.text.strip()[:-1]
  			headers = headers + ", " + label
  			data = data + ", " + overview_container.find("td", {"class": "right_column"}).text.strip()[:-1].replace(',', '|')

  	funding = detail_soup.find(id="ContentPlaceHolder1_PropGeneralInfo_FundProgramReadGV")
  	funding_containers = funding.findAll('tr')
  	for funding_container in funding_containers:
  		print(funding_container.text)

  driver.execute_script("window.history.go(-1)")

  if (headerBool):
  	f.write(headers + '\n')
  	headerBool = False

  f.write(data)

f.close()
