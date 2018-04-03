from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from sys import argv, exit
import time

if __name__ == '__main__':
    if len(argv) != 3:
        print(*argv)
        exit(1)

    startdate = argv[1]
    enddate = argv[2]

    br = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver')
    br.get('http://iamresponding.com')
    
    # select desktop version
    elem = br.find_element_by_css_selector('#lnkDesktop')
    elem.click()

    # login
    elem = br.find_element_by_css_selector('#subscriberLogin')
    elem.click()

    elem = br.find_element_by_css_selector('#ddlsubsciribers')
    elem.send_keys('CVAC')

    elem = br.find_element_by_css_selector('#memberfname')
    elem.send_keys('XXXXXXXXX')

    elem = br.find_element_by_css_selector('#memberpwd')
    elem.send_keys('XXXXXXXXX')

    elem = br.find_element_by_css_selector('#chkRemberMe')
    elem.click()

    elem = br.find_element_by_css_selector('#login')
    elem.click()

    # click admin functions
    # elem = br.find_element_by_css_selector('#IAR_LeftCol > table > tbody > tr:nth-child(1) > td:nth-child(2) > div:nth-child(2)')
    # elem.click()

    delay = 3 # seconds
    try:
        myElem = WebDriverWait(br, delay).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#adminFunctions')))
        print("Page is ready!")
    except TimeoutException:
        print("Loading took too much time!")

    elem = br.find_element_by_css_selector('#adminFunctions')
    elem.click()

    # select message reports
    webdriver.ActionChains(br) \
        .move_to_element(
            br.find_element_by_css_selector('#ctl00_ctl00_MainContent_menu_lnkrunreport')) \
        .move_to_element(
            br.find_element_by_css_selector('#ctl00_ctl00_MainContent_menu_lnkrunreport > ul > li:nth-child(5) > a')) \
        .click() \
        .perform()

    # enter report parameters
    elem = br.find_element_by_css_selector('#ctl00_ctl00_MainContent_ContentPlaceHolder1_txtDispatchStart')
    elem.clear()
    elem.send_keys(startdate)

    elem = br.find_element_by_css_selector('#ctl00_ctl00_MainContent_ContentPlaceHolder1_txtDispatchEnd')
    elem.clear()
    elem.send_keys(enddate)

    elem = br.find_element_by_css_selector('#btnDispatch')
    elem.click()

    # switch windows
    for w in br.window_handles:
        if w != br.current_window_handle:
            win = w
            break

    br.switch_to.window(win)

    # download file
    delay = 30 # seconds
    try:
        myElem = WebDriverWait(br, delay).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#exportToExcel')))
        print("Page is ready!")
    except TimeoutException:
        print("Loading took too much time!")

    elem = br.find_element_by_css_selector('#exportToExcel')
    elem.click()

    time.sleep(45)
    br.quit()

