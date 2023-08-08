import scrapy

from ..items import DataItem
from scrapy.loader import ItemLoader
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime as dt


class BlackRockSpider(scrapy.Spider):
    name = 'AEID6028_Car_Repairs'
    allowed_domains = ['pxdata.stat.fi']

    AEID_project_id = 'AEID6028'
    site = 'pxdata.stat.fi'
    source_country = 'FI'
    file_create_dt = dt.utcnow().strftime("%Y-%m-%d")

    start_urls = [
        'https://pxdata.stat.fi/PxWeb/pxweb/en/StatFin/StatFin__klv/statfin_klv_pxt_111t.px/'
    ]

    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 0,  # Set concurrent requests to 1 for sequential processing
        'DEFAULT_REQUEST_HEADERS': {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'max-age=0',
            'sec-ch-ua': '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
        },

    }

    def __init__(self):
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))


    def parse(self, response):
        self.driver.get(response.url)

        # Using Selenium to click on "Select all" buttons
        selectors = [
            "ctl00_ContentPlaceHolderMain_VariableSelector1_VariableSelector1_VariableSelectorValueSelectRepeater_ctl01_VariableValueSelect_VariableValueSelect_SelectAllButton",
            "ctl00_ContentPlaceHolderMain_VariableSelector1_VariableSelector1_VariableSelectorValueSelectRepeater_ctl02_VariableValueSelect_VariableValueSelect_SelectAllButton",
            "ctl00_ContentPlaceHolderMain_VariableSelector1_VariableSelector1_VariableSelectorValueSelectRepeater_ctl03_VariableValueSelect_VariableValueSelect_SelectAllButton",
            "ctl00_ContentPlaceHolderMain_VariableSelector1_VariableSelector1_VariableSelectorValueSelectRepeater_ctl04_VariableValueSelect_VariableValueSelect_SelectAllButton"]

        for selector in selectors:
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, selector))).click()

        # Click "Show table" button
        show_table_button = "ctl00_ContentPlaceHolderMain_VariableSelector1_VariableSelector1_ButtonViewTable"
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, show_table_button))).click()

        # We wait until the data is loaded
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
            (By.ID, "ctl00_ctl00_ContentPlaceHolderMain_cphMain_Table1_Table1_DataTable")))

        # Parse data
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')

        industries = soup.select('th.table-header-first')
        industries_colspans = [int(th['colspan']) for th in industries]

        variables = soup.select('th.table-header-middle')
        headers = [th.get_text() for th in soup.select('th.table-header-last')]

        # Extract all the data rows
        rows = soup.select('table#ctl00_ctl00_ContentPlaceHolderMain_cphMain_Table1_Table1_DataTable tbody tr')

        for row in rows:
            year = row.select_one('th.layout1-table-stub').get_text()
            data = [td.get_text() for td in row.select('td')]

            industry_index = 0
            colspan_remaining = industries_colspans[industry_index]

            idx = 0  # index to track the position in the data list

            for variable in variables:
                variable_colspan = int(variable['colspan'])

                for _ in range(variable_colspan):
                    loader = ItemLoader(item=DataItem())
                    loader.add_value('information', headers[idx % len(headers)])
                    loader.add_value('month_or_date', year)
                    loader.add_value('industry', industries[industry_index].get_text())
                    loader.add_value('variable', variable.get_text())
                    loader.add_value('value', data[idx])
                    yield loader.load_item()

                    colspan_remaining -= 1
                    if colspan_remaining == 0:
                        industry_index += 1
                        if industry_index < len(industries_colspans):
                            colspan_remaining = industries_colspans[industry_index]

                    idx += 1

    def close(self, reason):
        self.driver.quit()
        self.csvfile.close()
