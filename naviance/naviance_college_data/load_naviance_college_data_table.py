# -*- coding: utf-8 -*-
"""
Created on Tue Feb  5 10:50:36 2019

@author: vfaner

Description:  Module to upload naviance_college_data.csv to 
              CollegeData_STAGING. To be run periodically during 
              Naviance loads.
"""

import sys
import logging
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine


def main():
    logging.basicConfig(
        filename=Path.cwd().joinpath('naviance_college_data_periodic_load.log'),
        level=logging.INFO,
        format='%(asctime)s: %(message)s')
    csv = sys.argv[1]

    df = pd.read_csv(csv, header=1, usecols=['College ID', 
                                             'College Name',
                                             'CEEB'])
    df = df.rename({'College ID': 'naviance_college_id',
                    'College Name': 'naviance_college_name',
                    'CEEB': 'ceeb_code'}, axis=1)

    # Upload to Staging
    engine = create_engine(
        r'mssql+pyodbc://TLXSQLPROD-01/CollegeData_STAGING?driver=ODBC+Driver+13+for+SQL+Server',
        fast_executemany=True  # Faster loads - for SQLAlchemy 1.3+ ONLY
    )
    df.to_sql(
        name=r'naviance_college_data',
        con=engine,
        schema='Naviance',
        if_exists='replace',
        index=False
    )
    logging.info(f'Updated college_data table successfully loaded to Staging')


if __name__ == '__main__':
    main()
