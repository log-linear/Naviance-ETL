
# BATCH FILE INSTRUCTIONS:

As of August 2019, The Naviance financial aid and college data loads are now fully 
automated. In order, the __run_scripts.bat__ file runs 
1. naviance_scraper.py
2. load_financial_aid_table.py
3. update_production_table.sql
3. reformat_appdata_csv.py
4. upload_to_staging.py
5. bi_weekly_naviance_merge.sql

To run it, double click on the file, or enter in the file's location and name in 
the command line, e.g.:

```
S:\Student Data\Data Loads 2017-2018\naviance\naviance_financial_aid\run_scripts.bat
```

Alternatively, you can use Windows Task Scheduler to set the script to run on
a schedule.

Note that the batch file is set to run in a conda virtual environment in Victor's
Uplift account. This will need to be updated to run on your computer/account.

# INSTRUCTIONS FOR RUNNING __naviance_scraper.py__ AS A STANDALONE SCRIPT

__NOTE:__ Before running, ensure you have Google Chrome and Python with the 
Selenium library installed on your computer. This script was written in Python 
3.7.3, though older versions may also work.

1. Download __chromedriver.exe__ from 
https://sites.google.com/a/chromium.org/chromedriver/downloads
and place the unzipped file in the main script directory 
(__naviance_scraper/__). Be sure to  choose the appropriate driver for your 
version of Chrome.

2. If it does not already exist, open up a text editor and create a file in the 
main directory called __config.cfg__, formatted as follows:

    ```
    [CREDENTIALS]
    EMAIL = youremail@uplifteducation.org
    PASSWORD = yournaviancepassword
    
    [OPTIONS]
    CLASS = class of 2020 (grade 11)
    ```

    Where EMAIL and PASSWORD are your Naviance login email and password. You may
    also need to update the CLASS field if you wish to pull data for another
    Uplift class. See the Naviance website for options.

3. Open up a terminal and run:

    ```
    python naviance_scraper.py
    ```
    
    The script will automatically open up Chrome and will close on its own once 
    the files are downloaded. Be sure not to close the browser before the script 
    finishes.
    
4. **OPTIONAL:** Open up a terminal and run:

    ```
    python scrape_naviance_colleges.py
    ```
    
    This script does **not** need to be run on a regular basis, as Naviance's 
    master college list is generally stable over time. This script will need 
    about 2 hours to complete.
