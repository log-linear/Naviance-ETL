import openpyxl
import os
import shutil
import re
from pathlib import Path

y26_root = 'C:/Users/tharpin/Desktop/year_26/unzipped'
os.chdir(y26_root)

y26_paths = [path for path in Path.cwd().iterdir()]

regex = r'\\'
formatted_paths = [re.sub(regex, '/', str(path)) for path in y26_paths]

for path in formatted_paths:
    for root, dir, files in os.walk(path):
        if root[-7:] != '_MACOSX':
            date_var = root[-7:]
            for file in files:
                if file == 'CollegeStatsDataByStudent.csv':
                    print(file)
