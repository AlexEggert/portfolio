import csv
import os
from datetime import date

import pyodbc
from dotenv import load_dotenv

load_dotenv()

FILENAME = f"mfg_names_{date.today().isoformat()}.csv"
cnxn = pyodbc.connect(os.getenv("CONNECTION_STRING"))

# Create a cursor from the connection
cursor = cnxn.cursor()
cursor.execute(os.getenv("INVENTORY_QUERIES"))

array = []

# mfg_names = set()
# for row in cursor:
#    mfg_names.add(row[0].split(" ")[0])

mfg_names = set()
name_to_row = {}
for row in cursor:
    name = row[0].split(" ")[0]
    mfg_string = f"Manufacturer('{name}', r'^{name} '),"
    mfg_names.add(mfg_string)
    name_to_row[mfg_string] = row[0]

with open(FILENAME, "w+", newline="") as output_file:
    writer = csv.writer(output_file)
    writer.writerows(sorted([name, name_to_row[name]] for name in mfg_names))
