A miner for getting the even spread and total lines from betexplorer.com. The default bookie is pinnacle,
if pinnacle is not found it uses the most frequent lines.

For windows, chromedriver is needed due to the javascript implementations where the lines are shown.

https://sites.google.com/a/chromium.org/chromedriver/downloads

If you want to save the lines to a db, change dbinfo in dbscript.py.
If not, uncomment the insert_into_db functions in main. 

pip install -r /path/to/requirements.txt
