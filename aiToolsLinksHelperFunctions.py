
from bs4 import BeautifulSoup
from bs4.element import Comment

from selenium.common import exceptions
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from datetime import datetime
import time

import re


#################################################################################################

def stringsRetrieverMainPage(main_page_bs4, page_link):
    "Retrieves and processes all visible strings from the page."
    def visible_strings(string):
        "Checks each string on the page and returns content-related strings."
        if string.parent.name in ["style", "script", "noscript", "head", 'title', "meta", "[document]"]:
            return False
        elif isinstance(string, Comment):
            return False
        else:
            return True


    def processedStrings(main_page_bs4, page_link):
        "Returns strings from the main page."

        try:
            main_page_strings = main_page_bs4.find_all(string=True)
        except AttributeError:
            filename_mainPage = filenameMainPage(page_link)
            with open("aiToolsLinks-logger.csv", "a", encoding= 'utf-8') as logger:
                logger.write(f"\n{str(datetime.now())[:str(datetime.now()).index('.')]}: Webpage '{page_link}' doesn't contain visible strings on the page. Moving to the next link.\n\n")
            return None
        else:
            main_page_strings = filter(visible_strings, main_page_strings)
            main_page_strings_processed = [string.strip() for string in main_page_strings if string]
            strings = "\n".join(main_page_strings_processed)
            strings = "".join([string.encode(encoding="utf-8", errors="replace").decode("utf-8") for string in list(strings)])

            return strings

    strings = processedStrings(main_page_bs4, page_link)
    print("String: ", bool(strings))
    if strings:
        return strings
    else:
        return None

#################################################################################################

def hrefsProcessor(rawTagLinks, page_link):
    "Returns a list of processed hyperlinks."
    def linkProcessor(rawTagLink):
        "Filters individual link. Returns True if none of the patterns match"
        if str(rawTagLink.string).strip().lower():
            if re.search("(.*log.*)|(.*sign.*)|(.*reg.*)|(.*get\s?(started)?.*)|(.*subscri.*)|(.*start.*)", str(rawTagLink.string).strip().lower()):
                return False
            else:
                if rawTagLink.get("href") == "/":
                    return False
                elif rawTagLink.get("href"):
                    if re.search("^#(.*)?", rawTagLink.get("href")):
                        if re.search("^#(.*)?", rawTagLink.get("href")).group() == rawTagLink.get("href"):
                            return False
                        else:
                            return False
                    elif re.search("(^https?://.*)|(/.*)|(^www.*)", rawTagLink.get("href")):
                        return True
                else:
                    return False
        else:
            return False

    processedTagLinks = filter(linkProcessor, rawTagLinks)
    print("AFTER PRE_PROCESSING")

    def hrefsProcessor(processedTagLinks, page_link):
        "Composes a list of processed hyperlinks."

        processedHrefs = []
        subdirectories = []
        rawHrefs = list(set([processedLink.get("href") for processedLink in processedTagLinks]))
        for rawHref in rawHrefs:
            subdirectories.append(rawHref)
            if re.search("^/.*", rawHref):
                processedHrefs.append(page_link + rawHref)
            else:
                processedHrefs.append(rawHref)

        return processedHrefs, subdirectories, page_link

    processedHrefs, subdirectories, page_link = hrefsProcessor(processedTagLinks, page_link)
    return processedHrefs, subdirectories, page_link

#################################################################################################

def filenameMainPage(page_link):
    "Defines main page filename using regular expressions."
    # page_link = "https://10web.io/?_from=theresanaiforthat"

    filename_mainPage = list(re.search("https?://(.*)", page_link).group(1))
    for counter, letter in enumerate(filename_mainPage):
        if letter in "!@#$%^&*()?/":
            filename_mainPage[counter] = "-"
    else:
        filename_mainPage = "".join(filename_mainPage)
    return filename_mainPage

" -------------------------------------------------------------------------------------------- "

def filenameNavBody(filename_mainPage, subdirectory):
    "Returns a filename for the navlink."

    filename_subdirectory = list(subdirectory)
    for counter, letter in enumerate(filename_subdirectory):
        if letter in "!@#$%^&*()?/":
            filename_subdirectory[counter] = "-"
    else:
        subdirectory = "".join(filename_subdirectory)
        processed_subdirectory = filename_mainPage + subdirectory
        return processed_subdirectory

#################################################################################################
#################################################################################################

def mainPageBodyScraper(page_link, numberOfPages):
    "Scrapes the visible strings of the main page body."

    options = ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    driver = Chrome(options=options)
    try:
        driver.get(page_link)
    except Exception:
        with open("aiToolsLinks-logger.csv", "a", encoding='utf-8') as logger:
            logger.write(
                f"\n{str(datetime.now())[:str(datetime.now()).index('.')]}: Webpage '{page_link}' could not be reached. Moving to the next link. ({numberOfPages + 1})\n\n")
        driver.close()
        return [[],[]]
    try:
        mainPageBodySelenium = driver.page_source
    except Exception:
        with open("aiToolsLinks-logger.csv", "a", encoding='utf-8') as logger:
            logger.write(
                f"\n{str(datetime.now())[:str(datetime.now()).index('.')]}: Webpage: '{page_link}' Page source can not be extracted. Moving to the next link. ({numberOfPages})\n\n")
        driver.close()
        return [[],[]]

    mainPageBodySoup = BeautifulSoup(mainPageBodySelenium, "html.parser").body

    mainPageBody_strings = stringsRetrieverMainPage(mainPageBodySoup, page_link)
    if mainPageBody_strings:
        filename_mainPage = filenameMainPage(page_link)
        driver.close()
        return [mainPageBody_strings, filename_mainPage]
    else:
        driver.close()
        return [[], []]


###############################################################################################

def linksScraper(page_link, numberOfPages):
    "Returns a list of scraped links from the navbar."

    # page_link = "https://www.quetext.com"
    options = ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    driver = Chrome(options=options)
    try:
        driver.get(page_link)
    except:
        with open("aiToolsLinks-logger.csv", "a", encoding='utf-8') as logger:
            logger.write(f"\n{str(datetime.now())[:str(datetime.now()).index('.')]}: Webpage {page_link}. Could not reach the website.\n")

    try:
        search_tag = "nav"
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "nav")))
    except exceptions.TimeoutException:
        try:
            search_tag = "header"
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "header")))
        except exceptions.TimeoutException:
            with open("aiToolsLinks-logger.csv", "a") as logger:
                logger.write(
                    f"\n{str(datetime.now())[:str(datetime.now()).index('.')]}: Webpage - {page_link}. An element with a name 'nav' or 'header' are not present on the page.\n\n")
            driver.close()
            return [None, None, page_link]
    except Exception:
        with open("aiToolsLinks-logger.csv", "a") as logger:
            logger.write(f"\n{str(datetime.now())[:str(datetime.now()).index('.')]}: Webpage - {page_link}. Some error occurred when searcing for a nav tag. \n\n")

    if search_tag == "header":
        with open("aiToolsLinks-logger.csv", "a") as logger:
            logger.write(f"\n{str(datetime.now())[:str(datetime.now()).index('.')]}: Webpage - {page_link}. A tag with a name 'nav' has not been detected.\n")

    try:
        pageBody_selenium = driver.page_source
    except Exception as exc:
        with open("aiToolsLinks-logger.csv", "a", encoding='utf-8') as logger:
            logger.write(
                f"\n{str(datetime.now())[:str(datetime.now()).index('.')]}: Webpage: '{page_link}' Page source of the main page can not be extracted. Moving to the next link. ({numberOfPages})\n\n")
            driver.close()
            return [None, None, page_link]
    if search_tag == "nav":
        pageBody_soup = BeautifulSoup(pageBody_selenium, "html.parser").nav
    elif search_tag == "header":
        pageBody_soup = BeautifulSoup(pageBody_selenium, "html.parser").header

    rawTagLinks = pageBody_soup.find_all("a")
    processedHrefs, subdirectories, page_link = hrefsProcessor(rawTagLinks, page_link)

    # print(type(rawLinks), rawLinks, sep="\n")
    # for link in rawLinks:
    #     print(link)

    driver.close()
    return [processedHrefs, subdirectories, page_link]

processedHrefs, subdirectories, page_link = linksScraper("https://10web.io/?_from=theresanaiforthat", 1)
print(processedHrefs)

###############################################################################################

def pageBodyScraper(page_link, navLink, numberOfPages, linkCounter, mainPageBody_filename, subdirectory):
    "Opens the provided navLink, returns the scraped page body."

    # Chrome driver pre-configuration.
    options = ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    driver = Chrome(options=options)

    # Extracting the page and parsing through BeautifulSoup.
    try:
        driver.get(navLink)
    except Exception as exc:
        with open("aiToolsLinks-logger.csv", "a", encoding='utf-8') as logger:
            logger.write(f"\n{str(datetime.now())[:str(datetime.now()).index('.')]}: Webpage: '{page_link}' Navlink can not be reached. Moving to the next navlink. ({numberOfPages}) - {linkCounter}\n\n")
        driver.close()
        return [None, None]

    # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "nav")))
    try:
        scraped_page_selenium = driver.page_source
    except Exception as exc:
        with open("aiToolsLinks-logger.csv", "a", encoding="utf-8") as logger:
            logger.write(f"\n{str(datetime.now())[:str(datetime.now()).index('.')]}: Webpage: '{page_link}' Page source of the navlink can not be extracted. Moving to the next navlink. ({numberOfPages}) - {linkCounter}\n\n")
        driver.close()
        return [None, None]

    scraped_page_bs = BeautifulSoup(scraped_page_selenium, "html.parser").body

    navLinkBody_strings = stringsRetrieverMainPage(scraped_page_bs, navLink)
    filename_navLink = filenameNavBody(mainPageBody_filename, subdirectory)
    driver.close()

    return navLinkBody_strings, filename_navLink

#########################################################################################################


def navLinkBodyScraper(navLink, numberOfPages, hrefCounter):
    "Returns processed visible strings of the navlink."
    options = ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    driver = Chrome(options=options)

    try:
        driver.get(navLink)
    except:
        with open("aiToolsLinks-logger.csv", "a", encoding="utf-8") as logger:
            logger.write(f"\n{str(datetime.now())[:str(datetime.now()).index('.')]}: Navlink - {navLink} ({numberOfPages}). Webpage could not be reached.\n")
        driver.close()
        return None

    try:
        body_selenium = driver.page_source
    except:
        with open("aiToolsLinks-logger.csv", "a", encoding="utf-8") as logger:
            logger.write(f"\n{str(datetime.now())[:str(datetime.now()).index('.')]}: Navlink - {navLink} ({numberOfPages}). Error in getting the navlink page source.\n")
        driver.close()
        return None

    body_bs = BeautifulSoup(body_selenium, "html.parser").body

    def visibleStrings_navLink(body_bs):
        "Returns visible strings from the navlink body."

        def stringsFilter(string):
            "Returns a NavigableString if passes through filters."
            if string.parent.name in ["style", "script", "noscript", "head", 'title', "meta", "[document]"]:
                return False
            elif isinstance(string, Comment):
                return False
            else:
                return True

        def stringsScraper(body_bs):
            "Returns processed string."

            try:
                visibleStrings = body_bs.find_all(string= True)
            except:
                with open("aiToolsLinks-logger.csv", "a", encoding='utf-8') as logger:
                    logger.write(f"\n{str(datetime.now())[:str(datetime.now()).index('.')]}: Navlink - {numberOfPages}. Navlink does not have visible strings. Moving to the next navlink.\n")
                return None

            visibleStringsFiltered = filter(stringsFilter, visibleStrings)      # function is used here

            visibleStringsEncoded = [string.encode(encoding="utf-8", errors= "replace").decode("utf-8").strip() for string in visibleStringsFiltered]
            visibleStringsAsList = [string for string in visibleStringsEncoded if string != "\n" if string]
            visibleStringsFinal = "\n".join(visibleStringsAsList)

            return visibleStringsFinal

        visibleStringsFinal = stringsScraper(body_bs)
        return visibleStringsFinal

    visibleStringsFinal = visibleStrings_navLink(body_bs)
    driver.close()
    if visibleStringsFinal == None:
        return None
    # print(visibleStringsFinal)
    # return visibleStringsFinal

    def navLinkFilename(navLink):
        "Returns a navLink filename."
        navLink = navLink

        # Additonal filter to name a file.
        if len(navLink) > 120:
            extractedLink = f"Unknown link {hrefCounter}"
            with open("aiToolsLinks-logger.csv", "a", encoding='utf-8') as logger:
                logger.write(
                    f"{str(datetime.now())[:str(datetime.now()).index('.')]}: Did not manage to generate a filename. {navLink}")
            print(f"\nDid not manage to generate a filename - {navLink}\n")
        elif re.search("^https?://(.*)", navLink):
            extractedLink = re.search("^https?://(.*)", navLink).group(1)
        else:
            extractedLink = f"Unknown link {hrefCounter}"
            with open("aiToolsLinks-logger.csv", "a", encoding='utf-8') as logger:
                logger.write(f"{str(datetime.now())[:str(datetime.now()).index('.')]}: Did not manage to generate a filename. {navLink}")
            print(f"\nDid not manage to generate a filename - {navLink}\n")

        # print("This is extracted navLink: ", extractedLink)
        extractedLink = list(extractedLink)
        print("This is list", extractedLink)
        for counter, letter in enumerate(extractedLink):
            if letter in "!@#$%^&*()?/=,<>\\"   :
                extractedLink[counter] = "-"
        else:
            extractedLink = "".join(extractedLink)
            print("After processing: ", extractedLink)
        return extractedLink

    composedNavLinkFilename = navLinkFilename(navLink)

    # Creates a file and a log entry.
    with open(f"{composedNavLinkFilename}.txt", "w", encoding="utf-8") as file:
        file.write(visibleStringsFinal)
    with open("aiToolsLinks-logger.csv", "a", encoding='utf-8') as logger:
        logger.write(f"{str(datetime.now())[:str(datetime.now()).index('.')]}: Navlink: {navLink}\n" )


































