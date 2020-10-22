# STEP-BY-STEP INSTRUCTIONS:

1. Log in to **[id.naviance.com](id.naviance.com)**.

2. Click on the gear icon in the top right and navigate to the **Data Export** page

3. Under the **Data type** drop-down menu, choose **scholarship data** (no need to change any other fields). Click on **Export Data**.

4. Navigate to the **Analytics** > **Reports** page in the top left.

5. Under **Scholarship Reports**, **Detailed List By Student**, click on **Customize**.

6. Under **Columns**, click on **Add All**. **Student ID** should now be listed in the box on the right. Click on **View Report**.

7. Click on the **CSV** button near the top of the page.

8. Save both csvs in the same directory as the python script.

9. Open up a terminal, cd into the directory where the scripts/csvs are located, then run the following command:

```shell
python load_financial_aid_table.py 'Detailed List by Student.csv' 'scholarship.csv'
``` 

10. Run __*update_production_table.sql*__

Done!

# NOTES:

- You must have Python with the pandas and sqlalchemy libraries installed on your computer to run the .py files.
- If you need to rebuild the production tables, you will need to change the Class Year/Grade field (See Step 6) and pull individual reports for each class from 2011 to present. You can then combine the files into one .csv, or run the .py file for each individual .csv. Be sure to update the load_financial_aid_table.py file to point to CollegeData, rather than CollegeData_STAGING.
