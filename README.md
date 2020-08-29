# yalecovid

> A Python program for parsing data from Yale's COVID-19 statistics webpages.

Use this program to download Yale's provided COVID-19 data in a more flexible format than a webpage. Graphs are saved as images and the online HTML tables are saved as CSV spreadsheets, which are easier to use programatically or for data processing applications.

## Use
Make sure you have Python installed. Install all prerequisite packages thus:
```sh
pip3 install -r requirements.txt
```
Then simply run the program:
```sh
python3 scrape.py
```
All the output files will be written into the `data/` directory.

## License
[GPL](LICENSE)

## Author
[Erik Boesen](https://github.com/ErikBoesen)
