from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select

url = 'http://faast.waterboards.ca.gov/Public_Interface/PublicPropSearchMain.aspx'
# headers = {
#     'HTTP_USER_AGENT': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.13) Gecko/2009073022 Firefox/3.0.13',
#     'HTTP_ACCEPT': 'text/html,application/xhtml+xml,application/xml; q=0.9,*/*; q=0.8',
#     'Content-Type': 'application/x-www-form-urlencoded'
# }

# get to appropriate page
driver = webdriver.Chrome()
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

# grab labels for data
labels = table.tbody.tr # haven't yet figured out how to loop through this and extract each label's text one at a time

# grab each row of data
containers = table.findAll('tr')[1:]

# write each row of data to csv file
filename = 'pin_descriptions.csv'
f = open(filename, 'w')
headers = 'Pin #, Agreements, Proposal Title, Applicant, County, WaterShed, RWQCB, Req Funds, Status'
f.write(headers)
for container in containers:
  pin = container.a.text
  description = container.findAll('td')[1:]
  agreement = description[0].text
  proposal = description[1].text
  applicant = description[2].text
  county = description[3].text
  watershed = description[4].text
  rwqcb = description[5].text
  reqfunds = description[6].text
  status = description[7].text

  f.write(pin + ',' + agreement + ',' + '"' + proposal + '"' + ',' + '"' + applicant + '"' + ',' + '"' + county + '"' + ',' + '"' + watershed + '"' + ',' + '"' + rwqcb + '"' + ',' + '"' + reqfunds + '"' + ',' + status + '\n')

f.close()
