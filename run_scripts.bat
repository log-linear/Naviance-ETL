
:: Run file download script
cd naviance
python naviance_scraper.py

:: Rename files using current timestamp
cd output
set timestamp=%DATE:~-4,4%%DATE:~-7,2%%DATE:~-10,2%_%TIME:~0,2%%TIME:~3,2%%TIME:~6,2%
ren "appdata.csv" "appdata_%timestamp%.csv"
ren "Detailed List By Student.csv" "fin_aid_%timestamp%.csv"
ren "scholarship.csv" "fin_aid_categories_%timestamp%.csv"

:: Load financial aid tables
cd ..\naviance_financial_aid
python load_financial_aid_table.py "..\output\fin_aid_%timestamp%.csv" "..\output\fin_aid_categories_%timestamp%.csv"
sqlcmd -S TLXSQLPROD-01 -E -i update_production_table.sql 

:: Load college application data
cd ..\college_acceptance_status
python reformat_appdata_csv.py "..\output\appdata_%timestamp%.csv"
python upload_to_staging.py appdata.csv
sqlcmd -S TLXSQLPROD-01 -E -i bi_weekly_naviance_merge.sql