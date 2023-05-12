import os

from manufacturer import AUTHORIZED_MFGS, NON_AUTHORIZED_MFGS, get_inventory_row
import csv
from operator import itemgetter
import pyodbc
from datetime import date
import re
import logging
from dotenv import load_dotenv


load_dotenv()

FILENAME = f"Stock_{date.today().isoformat()}.csv"
cnxn = pyodbc.connect(os.getenv("CONNECTION_STRING"))

# Create a cursor from the connection
cursor = cnxn.cursor()
cursor.execute(os.getenv("INVENTORY_QUERIES"))

AUTH_FILENAME = f"Auth_Stock_{date.today().isoformat()}.csv"
NON_AUTH_FILENAME = f"Non_Auth_Stock_{date.today().isoformat()}.csv"

authorized_mfg_list = []
non_authorized_mfg_list = []
for row in cursor:
    found = False
    for mfg in AUTHORIZED_MFGS:
        if re.match(mfg.pattern, row[0]) is not None:
            logging.debug(f"{mfg.name} matched for {row[0]}")
            authorized_mfg_list.append(get_inventory_row(mfg, row))
            found = True
            break
    if not found:
        for mfg in NON_AUTHORIZED_MFGS:
            if re.match(mfg.pattern, row[0]) is not None:
                logging.debug(f"{mfg.name} matched for {row[0]}")
                non_authorized_mfg_list.append(get_inventory_row(mfg, row))
                break
        else:
            pass
            #logging.critical(f"Match not found for: {row[0]}")

authorized_mfg_list.sort(key=itemgetter(1))
non_authorized_mfg_list.sort(key=itemgetter(1))
HEADER = [("P/N", "MANUFACTURE", "QTY")]

with open(AUTH_FILENAME, "w+", newline="") as output_file:
    writer = csv.writer(output_file, quoting=csv.QUOTE_ALL)
    writer.writerows(HEADER)
    writer.writerows(authorized_mfg_list)

with open(NON_AUTH_FILENAME, "w+", newline="") as output_file:
    writer = csv.writer(output_file)
    writer.writerows(HEADER)
    writer.writerows(non_authorized_mfg_list)

