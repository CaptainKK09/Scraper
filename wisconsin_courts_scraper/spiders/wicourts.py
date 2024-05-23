import csv
import json
import os
import time
from copy import deepcopy
from datetime import datetime, timedelta

import scrapy
from scrapy import Selector
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class WicourtsSpider(scrapy.Spider):
    name = 'wicourts'
    start_urls = ['http://wcca.wicourts.gov/']
    url = "https://wcca.wicourts.gov/jsonPost/advancedCaseSearch"
    case_url = "https://wcca.wicourts.gov/caseDetail/{}/{}"

    payload = {
        "includeMissingDob": True,
        "includeMissingMiddleName": True,
        "attyType": "partyAtty",
        "offenseDate": {
            "start": "",
            "end": ""
        }
    }
    headers = {
        'Accept': 'application/json',
        'Accept-Language': 'en-GB,en;q=0.9,ur-PK;q=0.8,ur;q=0.7,en-US;q=0.6',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'Origin': 'https://wcca.wicourts.gov',
        'Pragma': 'no-cache',
        'Referer': 'https://wcca.wicourts.gov/advanced.html',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'Cookie': '_ga=GA1.1.680619817.1715404151; JSessionId_9401=D3BE92E6D39D42959C7688FB1D5C774F; _ga_196ESBHXM4=GS1.1.1715420396.3.1.1715421909.0.0.0'
    }
    custom_settings = {
        'FEED_URI': f'wicourts_output.csv',
        'FEED_FORMAT': 'csv',
        'FEED_FORMAT_ENCODING': 'utf-8-sig',
        "ZYTE_API_TRANSPARENT_MODE": True,
    }

    def __init__(self):
        options = Options()
        self.driver = webdriver.Chrome(options=options,
                                  service=Service(ChromeDriverManager().install()))

    def start_requests(self):
        input_records = self.read_csv()
        print("Start input_records ", input_records)

        for input_date in input_records:
            payload = deepcopy(self.payload)
            start_date_str = input_date.get('start_date')
            start_date = datetime.strptime(start_date_str, '%m-%d-%Y')
            end_date = start_date + timedelta(days=1)

            print("Start Date ", start_date)
            print("End Date ", end_date)

            payload['offenseDate']['start'] = start_date.strftime('%m-%d-%Y')
            payload['offenseDate']['end'] = end_date.strftime('%m-%d-%Y')

#            payload['offenseDate']['start'] = input_date.get('start_date')
#            payload['offenseDate']['end'] = input_date.get('end_date')
            yield scrapy.Request(url=self.url, headers=self.headers, callback=self.parse,
                                 body=json.dumps(payload), method="POST")

    def parse(self, response):
        self.headers['Cookie'] = '; '.join([i.decode('utf-8') for i in response.headers.getlist('Set-Cookie')])
        json_data = json.loads(response.text)
        cases = json_data.get('result').get('cases')
        for case in cases:
            county_no = case.get('countyNo')
            case_no = case.get('caseNo')
            case_url = "https://wcca.wicourts.gov/caseDetail.html?caseNo={}&countyNo={}&index=0&isAdvanced=true"
            self.driver.get(case_url.format(case_no, county_no))
            # Replace time.sleep(5) with:
#            WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'span.link[role="link"]')))

            time.sleep(5)
            try:
                self.driver.find_element(By.CSS_SELECTOR, 'span.link[role="link"]').click()
#                time.sleep(3)
                input('Press Enter When Done: ')

            except Exception as e:
                pass
            self.driver.find_element(By.XPATH, "//a[contains(text(),'View case details')]").click()
            time.sleep(3)
            response = Selector(text=self.driver.page_source)
            item = dict()
            item['Name'] = response.xpath('//section[@id="defendant"]//dt[contains(text(),"Defendant name")]/following-sibling::dd/text()').get('')
            item['County'] = response.css("span.countyName::text").get('')
            item['DOB'] = response.xpath('//section[@id="defendant"]//dt[contains(text(),"Date of birth")]/following-sibling::dd/text()').get('')
            item['Caption'] = response.css('.caption::text').get('')
            item['Status'] = response.xpath('//section[@id="summary"]//dt[contains(text(),"Case status")]/following-sibling::dd/text()').get('')
            item['Filling date'] = response.xpath('//section[@id="summary"]//dt[contains(text(),"Filing date")]/following-sibling::dd/text()').get('')
            item['Gender'] = response.xpath('//section[@id="defendant"]//dt[contains(text(),"Sex")]/following-sibling::dd/text()').get('')
            item['Race'] = response.xpath('//section[@id="defendant"]//span[contains(text(),"Race")]/..//following-sibling::dd/text()').get('')
            item['Case Number'] = response.css('.caseNo::text').get('')
            for citation in response.css('#citations .citation'):
                item['Statute'] = citation.xpath('.//dt[contains(text(),"Statute")]//following-sibling::dd/text()').get('')
                item['Description'] = citation.xpath('.//dt[contains(text(),"Charge description")]//following-sibling::dd/text()').get('')
                # item['Disposition'] = citation.get('dispoDesc')
                item['offense Date'] = citation.xpath('.//dt[contains(text(),"Violation date")]//following-sibling::dd/text()').get('')
                item['Issuing agency'] = citation.xpath('.//dt[contains(text(),"Issuing agency")]//following-sibling::dd/text()').get('')
                yield item

    def read_csv(self):
        with open('../input_date.csv', "r", encoding='Utf-8-sig') as outfile:
            return list(csv.DictReader(outfile))
            # yield scrapy.Request(url=case_url.format(case_no, county_no),
            #                      headers=self.headers, callback=self.parse_case, method="POST",
            #                      meta={
            #                          "zyte_api": {
            #                              "browserHtml": True,
            #                          },
            #                      },
            #                      )

    # def parse_case(self, response):
    #     json_data = json.loads(response.text)
    #     result = json_data.get('result')
    #     item = dict()
    #     item['Name'] = result.get('defendant').get('name')
    #     item['County'] = result.get('countyName')
    #     item['DOB'] = result.get('defendant').get('dob')
    #     item['Caption'] = result.get('caption')
    #     item['Status'] = result.get('status')
    #     item['Filling date'] = result.get('filingDate')
    #     item['Gender'] = result.get('defendant').get('sex')
    #     item['Race'] = result.get('defendant').get('race')
    #     for citation in result.get('citations'):
    #         item['Statute'] = citation.get('statuteCite')
    #         item['Description'] = citation.get('chargeDescr')
    #         # item['Disposition'] = citation.get('dispoDesc')
    #         item['offense Date'] = citation.get('offenseDate')
    #         item['Case Number'] = citation.get('caseNo')
    #         item['Issuing agency'] = citation.get('issAgName')
    #         yield item

