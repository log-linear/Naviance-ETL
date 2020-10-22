"""
Author:         Victor Faner
Date Created:   2019-06-07
Description:    Automation script to download .csv files from Naviance.
"""

import os
import time
from configparser import ConfigParser
from pathlib import Path

from selenium import webdriver


def get_detailed_list_by_student_csv(browser, class_year):
    """
    Download Detailed List By Student.csv

    :param browser:     selenium webdriver object
    :param class_year:  str class year to scrape - refer to Naviance
                        website for options
    """
    browser.get(r'https://succeed.naviance.com/district/reporting-framework/reports/customize?report_instance_id=1306')
    browser.find_element_by_xpath(
        r'//select[@name="settings_custom[ClassYear]"]'
        f'/option[text()="{class_year}"]'
    ).click()
    browser.find_element_by_css_selector('input.button.add-all').click()
    browser.find_element_by_css_selector('input.button.submit-selected').click()
    browser.find_element_by_xpath(
        r'//a[@href="view?report_instance_id=1306&format=csv"]'
    ).click()


def get_scholarship_csv(browser):
    """
    Download scholarship.csv

    :param browser:     selenium webdriver object
    """
    browser.get(r'https://succeed.naviance.com/district/setupmain/export.php')
    browser.find_element_by_xpath(
        '//select[@name="type"]/option[text()="scholarship data"]'
    ).click()
    browser.find_element_by_id('exportData').click()


def get_appdata_csv(browser, class_year):
    """
    Download appdata.csv

    :param browser:     selenium webdriver object
    :param class_year:  str class year - refer to Naviance website for
                        options
    """
    browser.get(r'https://succeed.naviance.com/district/setupmain/export.php')
    browser.find_element_by_xpath(
        r'//select[@name="type"]/option[text()="application data"]'
    ).click()
    browser.find_element_by_xpath(
        f'//select[@name="start_year"]/option[text()="{class_year}"]'
    ).click()
    browser.find_element_by_xpath(
        f'//select[@name="end_year"]/option[text()="{class_year}"]'
    ).click()
    browser.find_element_by_id('exportData').click()


if __name__ == '__main__':
    os.environ['PATH'] += os.pathsep + os.curdir  # Add chromedriver.exe to PATH
    cfg = ConfigParser()
    cfg.read(Path.cwd() / 'config.cfg')
    email = cfg['CREDENTIALS']['EMAIL']
    password = cfg['CREDENTIALS']['PASSWORD']
    class_year = cfg['OPTIONS']['CLASS']

    options = webdriver.ChromeOptions()
    Path.cwd().joinpath('output').mkdir(exist_ok=True)
    prefs = {'download.default_directory': str(Path.cwd() / 'output')}
    options.add_experimental_option('prefs', prefs)

    with webdriver.Chrome(options=options) as browser:
        browser.implicitly_wait(5)

        browser.get('https://id.naviance.com/login')
        browser.find_element_by_xpath(r'//a[@href="/login"]').click()

        browser.find_element_by_name('email').send_keys(email)
        browser.find_element_by_name('password').send_keys(password)
        browser.find_element_by_class_name('auth0-lock-submit').click()

        time.sleep(5)  # Wait for login to complete

        get_appdata_csv(browser, class_year)
        get_detailed_list_by_student_csv(browser, class_year)
        get_scholarship_csv(browser)

        time.sleep(3)  # Ensure last file is downloaded
