# -*- coding: utf-8 -*-
"""
Created on Thu Feb 7 16:37:36 2019

@author: vfaner

Description:  Module to clean and join 'scholarship.csv' and
              'Detailed List By Student with ID.csv'.  The resulting
              table is then uploaded to CollegeData_STAGING.
"""

import sys
import logging
import re
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine

# Regular expressions to search
RE_PRIMARY = re.compile(
    r'(scholarship|grant|loan|work.study|workstudy|efc|pell|\bsub\b'
    r'|\bparent\b|\bseog\b|\bteog\b|\btpeg\b|\bteg\b|\bpell\b|\bteach\b'
    r'|\bfseog\b|\bsar\b|national merit|\bsubsid|\bunsubsid|\bperkins\b'
    r'|schoalrship|sholarship|schloarship|scholarsip|scholarsshipi)'
)
RE_SUB = re.compile(
    r'(\bsub\b|\bunsub\b|national merit|\bperkins\b|\bsubsid|\bunsubsid'
    r'|\bparent\b|\bseog\b|\bteog\b|\btpeg\b|\bteg\b|\bpell\b|\bteach\b'
    r'|\bhazlewood\b|\bfseog\b|\bsar\b)'
)
RE_SOURCE = re.compile(
    r'(fed|institutional|private|loanf|grantf|stategrant|teg|tpeg|pell'
    r'|state grants|granti)'
)

# dict objects for mapping regex matches to appropriate aid categories
D_PRIMARY = {
    'scholarship': 'Scholarship',
    'national merit': 'Scholarship',
    'schoalrship': 'Scholarship',
    'sholarship': 'Scholarship',
    'schloarship': 'Scholarship',
    'scholarsip': 'Scholarship',
    'scholarsshipi': 'Scholarship',
    'grant': 'Grant',
    'pell': 'Grant',
    'seog': 'Grant',
    'teog': 'Grant',
    'tpeg': 'Grant',
    'teg': 'Grant',
    'fseog': 'Grant',
    'teach': 'Grant',
    'loan': 'Loan',
    'sub': 'Loan',
    'unsub': 'Loan',
    'subsid': 'Loan',
    'unsubsid': 'Loan',
    'perkins': 'Loan',
    'parent': 'Loan',
    'workstudy': 'Work Study',
    'work study': 'Work Study',
    'work_study': 'Work Study',
    'efc': 'EFC',
}
D_SUB = {
    'sub': 'Subsidized',
    'subsid': 'Subsidized',
    'unsubsid': 'Unsubsidized',
    'unsub': 'Unsubsidized',
    'perkins': 'Perkins',
    'parent': 'Parent Plus',
    'hazlewood': 'Hazlewood Act',
    'teg': 'TEG',
    'tpeg': 'TPEG',
    'seog': 'FSEOG',
    'fseog': 'FSEOG',
    'teog': 'TEOG',
    'teach': 'TEACH',
    'pell': 'Pell',
    'national merit': 'National Merit',
    'sar': 'SAR',
}
D_SOURCE = {
    'fed': 'Federal',
    'seog': 'Federal',
    'fseog': 'Federal',
    'pell': 'Federal',
    'loanf': 'Federal',
    'grantf': 'Federal',
    'fedloanf': 'Federal',
    'hazlewood': 'Federal',
    'stategrant': 'State',
    'state grants': 'State',
    'teg': 'State',
    'tpeg': 'State',
    'private': 'Private/Alternative',
    'institutional': 'Institutional',
    'granti': 'Institutional',
}


def main():
    logging.basicConfig(
        filename=Path.cwd().joinpath(
            'scholar_financial_aid_awards_biweekly_load.log'
        ),
        level=logging.INFO,
        format='%(asctime)s: %(message)s'
    )
    awards_csv = sys.argv[1]
    categories_csv = sys.argv[2]

    # Clean individual awards table
    awards = pd.read_csv(awards_csv, usecols=['Student ID', 'Scholarship',
                                              'Dollars Awarded'])
    awards = awards.rename({'Student ID': 'local_student_id',
                            'Class-Year': 'naviance_class_year',
                            'Scholarship': 'naviance_scholarship_name',
                            'Dollars Awarded': 'scholarship_amount'}, axis=1)
    awards['naviance_college_id'] = (  # Pull CEEB code from award name
        awards['naviance_scholarship_name'].str.extract(r'^(\d{3,4})')
    )
    awards = awards.drop_duplicates()

    # Clean award categories table
    categories = pd.read_csv(categories_csv, header=2, usecols=['Name',
                                                                'Categories'])
    categories = categories.rename({'Name': 'naviance_scholarship_name',
                                    'Categories': 'naviance_categories'},
                                   axis=1)
    categories = categories.drop_duplicates()

    # Clean out remaining duplicates from categories table
    dupes = (
        categories[categories.duplicated(subset=['naviance_scholarship_name'],
                                         keep=False)].copy()
    )
    categories = categories.drop_duplicates(
        subset=['naviance_scholarship_name'], keep=False
    )
    dupes = dupes.dropna(subset=['naviance_categories'])
    categories = categories.append(dupes)
    categories = categories.drop_duplicates(
        subset=['naviance_scholarship_name'], keep='first'
    )

    # Merge dfs, drop duplicates
    df = awards.merge(categories, how='left', on=['naviance_scholarship_name'])
    df = df.drop_duplicates()

    # Clean award names
    df['award_name'] = (
        df['naviance_scholarship_name']
            .str.strip()
            .str.replace(r'^\d{3,4}', '')
            .str.replace('-|_', ' ')
            .str.replace('  +', ' ')
            .str.strip()
    )

    # Extract aid categories via regex
    df['regex'] = df['award_name'].str.cat(df['naviance_categories'].fillna(''),
                                           sep=' ')  # concat for regex
    df['regex'] = df['regex'].str.strip().str.lower()
    df['primary_aid_type'] = df['regex'].str.extract(RE_PRIMARY)
    df['sub_type'] = df['regex'].str.extract(RE_SUB)
    df['source'] = df['regex'].str.extract(RE_SOURCE)
    df = df.replace({'primary_aid_type': D_PRIMARY,
                     'sub_type': D_SUB,
                     'source': D_SOURCE})

    # Upload to Staging
    engine = create_engine(
        r'mssql+pyodbc://TLXSQLPROD-01/CollegeData_STAGING?driver=ODBC+Driver+13+for+SQL+Server',
        fast_executemany=True  # Faster loads - for SQLAlchemy 1.3+ ONLY
    )
    df.drop(['regex'], axis=1).to_sql(
        name=r'scholar_financial_aid_awards',
        con=engine,
        schema='Naviance',
        if_exists='replace',
        index=False,
    )
    logging.info('Updated scholarships table successfully loaded to Staging')


if __name__ == '__main__':
    main()
