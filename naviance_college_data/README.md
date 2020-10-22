# INSTRUCTIONS:

- As of May 2019, we are only able to get the **naviance_college_data.csv** file via the biweekly FTP from Naviance. To reload/update this table:

1. open up a terminal, cd into the directory where the scripts/csvs are located, then run the following command:

```shell
python load_financial_aid_table.py naviance_college_data.csv
```

2. Run **update_production_table.sql**