from bs4 import BeautifulSoup
from bs4.element import Comment

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from datetime import datetime

import re
import time

# Importing helperFunctions file:
import aiToolsLinksHelperFunctions

# Importing the csv document with links:
with open("aiToolsLinks.csv", "r") as aiTools:
    webpages = aiTools.read().splitlines()
with open("aiToolsLinks-logger.csv", "a") as logger:
    logger.close()

# Takes the website links from the csv file and script runs:
def aiToolsLinks(page_links):
    "Initial function. Accepts a list of page links to scrape."
    page_links = page_links

    # Create a cycle here to iterate over all the webpage links.
    for numberOfPages, page_link in enumerate(page_links, 2144):

        # Scrapes the main page body and returns body strings and filename.
        mainPageBody_strings, mainPageBody_filename = aiToolsLinksHelperFunctions.mainPageBodyScraper(page_link, numberOfPages)

        # Creates a text file and updates logger.
        if mainPageBody_strings:
            try:
                with open(mainPageBody_filename + ".txt", "w", encoding="utf-8") as file:
                    file.write(mainPageBody_strings)
                with open("aiToolsLinks-logger.csv", "a", encoding= "utf-8") as logger:
                    logger.write(f"{str(datetime.now())[:str(datetime.now()).index('.')]}: Webpage - {page_link} ({numberOfPages})\n")
            except Exception as exc:
                with open("aiToolsLinks-logger.csv", "a", encoding= "utf-8") as logger:
                    logger.write(f"\nEXCEPTION\n{str(datetime.now())[:str(datetime.now()).index('.')]}: Webpage - {page_link}. Exception occured when creating a main page body file. ({numberOfPages})\n\n")
        else:
            continue


        # Returns all the links from the navbar of the main link, subdirectories and the main link.
        processedHrefs, subdirectories, page_link = aiToolsLinksHelperFunctions.linksScraper(page_link, numberOfPages)

        if processedHrefs:
            processedHrefs = list(set(processedHrefs))

            # Iterates over navbar links, scrapes the visible text and creates a text file, updates logger.
            for hrefCounter, processedHref in enumerate(processedHrefs, 1):
                result = aiToolsLinksHelperFunctions.navLinkBodyScraper(processedHref, numberOfPages, hrefCounter)
                if result == None:
                    continue
        else:
            continue

aiToolsLinks(webpages[2144:])
