#!/bin/bash

python3 ./01a_scrape_mobilede.py
python3 ./01b_update-items-from-web.py
python3 ./02_derive_further_fields.py
python3 ./03_dump_for_analysis.py
python3 ./04_regression.py

# TODO: fix the regression.py script.
# It seems to convert some fields (like, price or so),
# and the export does not work as expected
python3 ./02_derive_further_fields.py
python3 ./05_dump_for_user.py