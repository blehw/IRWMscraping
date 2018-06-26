from bs4 import BeautifulSoup
import urllib
import urllib.request
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select

uri = 'http://faast.waterboards.ca.gov/Public_Interface/PublicPropSearchMain.aspx'
headers = {
    'HTTP_USER_AGENT': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.13) Gecko/2009073022 Firefox/3.0.13',
    'HTTP_ACCEPT': 'text/html,application/xhtml+xml,application/xml; q=0.9,*/*; q=0.8',
    'Content-Type': 'application/x-www-form-urlencoded'
}

driver = webdriver.Firefox()
driver.get("http://faast.waterboards.ca.gov/Public_Interface/PublicPropSearchMain.aspx")

link = driver.find_element_by_id("GotoSearch")
link.click()

mySelect = Select(driver.find_element_by_id("ContentPlaceHolder1_RfpDDL"))
my=mySelect.select_by_value('310') 
wait = WebDriverWait(driver, 300)

search = driver.find_element_by_id("ContentPlaceHolder1_PublicSearchBtn")
search.click()

print(driver.page_source)