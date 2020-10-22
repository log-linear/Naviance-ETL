"""
Author:         Victor Faner
Date Created:   2019-06-10
Description:    Automation script to scrape college pages from Naviance
                into a csv file.
"""

import os
import time
import re
from configparser import ConfigParser
from pathlib import Path
from string import ascii_lowercase

import pandas as pd
from selenium import webdriver


def scrape_college_data(browser, url, regex):
    """
    Scrape relevant elements from a Naviance college page

    :param browser:     selenium webdriver object
    :param url:         str - URL of Naviance college page to scrape
    :param regex:       str or re.Pattern - regex pattern used to pull
                        Naviance college_id from URL

    :return:            str - college_id, str - college_name, str -
                        ceeb_code
    """
    browser.get(url)

    try:
        college_id = re.search(regex, url).groups()[2]
    except IndexError:
        college_id = None

    college_name = browser.find_element_by_xpath(
        '/html/body/div/table/tbody/tr[1]/td[2]/table/tbody/tr[2]/td[2]/table'
        '/tbody/tr[2]/td[2]/table/tbody/tr[1]/td/span[1]'
    ).text

    ceeb_code = browser.find_element_by_xpath(
        '/html/body/div/table/tbody/tr[1]/td[2]/table/tbody/tr[2]/td[2]/table'
        '/tbody/tr[3]/td[2]/table/tbody/tr[1]/td[2]/table/tbody/tr[9]/td[2]'
        '/table/tbody/tr[7]/td[2]'
    ).text
    if ceeb_code == 'N/A':
        ceeb_code = None

    return college_id, college_name, ceeb_code


if __name__ == '__main__':
    os.environ['PATH'] += os.pathsep + os.curdir  # Add main dir to PATH
    cfg = ConfigParser()
    cfg.read(Path.cwd() / 'config.cfg')
    email = cfg['CREDENTIALS']['EMAIL']
    password = cfg['CREDENTIALS']['PASSWORD']
    class_year = cfg['OPTIONS']['CLASS']
    cid_re = re.compile(r'(https://succeed.naviance.com/district'
                        r'/collegesmain/viewcollege.php\?)'
                        r'(cid=)(\w{4,6})')

    options = webdriver.ChromeOptions()
    Path.cwd().joinpath('output').mkdir(exist_ok=True)
    prefs = {'download.default_directory': str(Path.cwd() / 'output')}
    options.add_experimental_option('prefs', prefs)

    college_data = {
        'college_id': [],
        'college_name': [],
        'ceeb_code': [],
    }

    with webdriver.Chrome(options=options) as browser:
        browser.implicitly_wait(5)

        browser.get('https://id.naviance.com/login')
        browser.find_element_by_xpath(r'//a[@href="/login"]').click()

        browser.find_element_by_name('email').send_keys(email)
        browser.find_element_by_name('password').send_keys(password)
        browser.find_element_by_class_name('auth0-lock-submit').click()

        time.sleep(5)  # Wait for login to complete

        # Loop through college page indices alphabetically
        for letter in ascii_lowercase:
            browser.get(f'https://succeed.naviance.com/district/collegesmain'
                        f'/index.php?letter={letter}')

            # Get individual college URLs within each letter index
            college_urls = []
            for college_url in browser.find_elements_by_class_name('dark11'):
                college_urls.append(college_url.get_attribute('href'))

            # Open each college page and scrape data
            for college_url in college_urls:
                college_id, college_name, ceeb_code = scrape_college_data(
                    browser, college_url, cid_re
                )
                college_data['college_id'].append(college_id)
                college_data['college_name'].append(college_name)
                college_data['ceeb_code'].append(ceeb_code)

    final_df = pd.DataFrame(college_data)
    final_df.to_csv(Path.cwd() / 'output' / 'naviance_college_data.csv',
                    index=False)
