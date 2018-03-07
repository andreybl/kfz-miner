# #!/usr/bin/env python

import sys
from os.path import join, dirname

from dotenv import load_dotenv
from prompt_toolkit import prompt
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.history import FileHistory

import analysis
import commons
import crawling

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


def scrape():
    crawling.scrapeOverSearchPages()
    commons.deriveFurtherField()
    commons.dumpForAnalysis()
    analysis.regression()
    commons.dumpForUser()
    commons.readCsvCheckGone()
    commons.dumpForUser()


def readcsv():
    commons.readCsvCheckGone()


def regression():
    commons.deriveFurtherField()
    commons.dumpForAnalysis()
    analysis.regression()


def dump():
    commons.dumpForUser()


def quit():
    sys.exit()


def help():
    for key in commands:
        print("({}) {} \t\t{}".format(commands[key][0], key, commands[key][1]))


commands = {
    "scrape": ["s", "Find new vehicles from the search URLs, defined in the '/dir-configs/searchpages.txt' file. " +
               "\n" +
               "After scraping of the web, the regression analysis is applied to the vehicles and the price of the vehicle " +
               "and the price of the vehicle is predicted if possible. The difference between predicted and asked price " +
               "can be used as a clue about financial attractiveness of the vehicle: we may be interested in finding underestimated vehicles. " +
               "\n" +
               "The vehicles with its properties are dumped as CSV file into '/dir-data/' directory."],

    "allscrape": ["a", "Scrape all items (time intensive), apply regression and dump"],

    "readcsv": ["r", "Read CSV for user inputs to be persisted, check for gone items"],

    "regression": ["g", "Apply regression analysis to the vehicles. " +
                   "\n" +
                   "If possible, the price of the vehicle is predicted. The difference between predicted and asked price " +
                   " should help to identified underestimated vehicles."],

    "dump": ["d", "Dump found items to CSV according to search pattern"],

    "help": ["h", "Print help for commands and legend for output"],

    "quit": ["q", "Quit the programm"],
}

commandsShort = {}

CommandsCompleter = WordCompleter([], ignore_case=True)

for key in commands:
    commandsShort[commands[key][0]] = key
    CommandsCompleter.words.append(key)

while 1:
    user_input = prompt('> ',
                        history=FileHistory('history.txt'),
                        auto_suggest=AutoSuggestFromHistory(),
                        completer=CommandsCompleter,
                        )
    if user_input in commands:
        locals()[user_input]()
    elif user_input in commandsShort:
        locals()[commandsShort[user_input]]()
    else:
        print("Use \"help\" to list available commands")
