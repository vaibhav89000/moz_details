# -*- coding: utf-8 -*-
import scrapy
import time
import os
from scrapy.selector import Selector
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build


class MozSpider(scrapy.Spider):
    name = 'moz'

    sitename = []
    def start_requests(self):
        index = 0
        yield SeleniumRequest(
            url="https://moz.com/checkout/local/check",
            wait_time=1000,
            screenshot=True,
            callback=self.parse,
            meta={'index': index},
            dont_filter=True
        )
    def parse(self, response):

        driver = response.meta['driver']

        WebDriverWait(driver, 500).until(
            EC.presence_of_element_located((By.ID, "react-select-2--value-item"))
        )
        firstinput = os.path.abspath(os.curdir) + "\company.txt"
        f = open(firstinput, "r")
        company_name = f.read().splitlines()

        secondinput = os.path.abspath(os.curdir) + "\street.txt"
        f = open(secondinput, "r")
        street_name = f.read().splitlines()

        thirdinput = os.path.abspath(os.curdir) + "\postcode.txt"
        f = open(thirdinput, "r")
        postcode = f.read().splitlines()

        search_input1 = driver.find_element_by_xpath('//*[@id="check-listing"]/div/div[1]/span/div/div/form/div[2]/input')
        search_input1.send_keys(company_name[0])

        search_input2 = driver.find_element_by_xpath('//*[@id="check-listing"]/div/div[1]/span/div/div/form/div[3]/input')
        search_input2.send_keys(street_name[0])

        search_input3 = driver.find_element_by_xpath('//*[@id="check-listing"]/div/div[1]/span/div/div/form/div[4]/input')
        search_input3.send_keys(postcode[0])

        search_button = driver.find_element_by_xpath('//*[@id="check-listing"]/div/div[1]/span/div/div/form/div[5]/div/input')
        search_button.click()

        driver = response.meta['driver']
        # time.sleep(3)
        WebDriverWait(driver, 500).until(
            EC.presence_of_element_located((By.CLASS_NAME, "ubsc_results-top-box-results-wrapper"))
        )

        html = driver.page_source
        response_obj = Selector(text=html)

        details = response_obj.xpath('//div[@class="ubsc_result-listing-row ubsc_not-found"]')

        print("\n"*2)
        print(len(details))
        print("\n" * 2)

        if(len(details)==0):
            print('All listing found')
            scope = ['https://www.googleapis.com/auth/documents.readonly', "https://www.googleapis.com/auth/drive.file",
                     "https://www.googleapis.com/auth/drive"]

            path = os.path.abspath(os.curdir) + "\client_secret.json"
            creds = ServiceAccountCredentials.from_json_keyfile_name(path, scope)

            DOCUMENT_ID = '1bsIEfAclZ5hZa32HgFknpkJLBB2GjFESYt3vRgDgyE0'

            service = build('docs', 'v1', credentials=creds, cache_discovery=False)

            document = service.documents().get(documentId=DOCUMENT_ID).execute()

            requests = [
                {
                    "insertText":
                        {
                            "text": 'All listing found '+'\n',
                            "location":
                                {
                                    "index": 1
                                }
                        }
                }
            ]
            result = service.documents().batchUpdate(documentId=DOCUMENT_ID, body={'requests': requests}).execute()
        else:
            for detail in details:
                name = detail.xpath('.//div[1]/div[1]/span/text()').get()
                self.sitename.append(name)

            print("\n" * 2)
            print(self.sitename)
            print("\n" * 2)

            scope = ['https://www.googleapis.com/auth/documents.readonly', "https://www.googleapis.com/auth/drive.file",
                     "https://www.googleapis.com/auth/drive"]

            path = os.path.abspath(os.curdir) + "\client_secret.json"
            creds = ServiceAccountCredentials.from_json_keyfile_name(path, scope)

            DOCUMENT_ID = ''

            service = build('docs', 'v1', credentials=creds, cache_discovery=False)

            document = service.documents().get(documentId=DOCUMENT_ID).execute()

            for name in self.sitename:
                requests = [
                    {
                        "insertText":
                            {
                                "text": 'No listing found on '+name+'\n',
                                "location":
                                    {
                                        "index": 1
                                    }
                            }
                    }
                ]
                result = service.documents().batchUpdate(documentId=DOCUMENT_ID, body={'requests': requests}).execute()


