import logging
import re
import requests
import demjson
import ast

from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters

from pprint import *

# -------------------------------------------------------------------------- #
                            # Globals & Setup

''' Setup Telegram '''
TelegramToken = "1619470892:AAEioNLmnri45iN8KLADRKS7v1XGyN9DQdA"
# setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
# connect to telegram API
updater = Updater(token=TelegramToken , use_context=True)
dispatcher = updater.dispatcher

''' Telegram Globals '''
# setup arrays managed by user
keywords = []
locations = []

''' Indeed Globals '''
# search template "https://uk.indeed.com/jobs?q=web+developer&l=Guildford"
search_url = "https://uk.indeed.com/jobs?q={}&l={}"
# view template "https://uk.indeed.com/viewjob?jk=eb6e56041d3fee98"
view_url = "https://uk.indeed.com/viewjob?jk={}"


# -------------------------------------------------------------------------- #

# -------------------------------------------------------------------------- #
                                # Indeed

def fetchJobs(keywords=["Web Developer"], locations=["guildford"]):
    page = requests.get(search_url.format('+'.join(keywords), locations[0]))

    # Parse page.text...
    #   JobMap[0-n] - contains all of the jobs on the page
    #   jk          - the ID we can use on view_url
    #   city, loc   - the city?
    #   cmplink     - company link
    #   cmp esc     - fullname of company?
    #   title       - the title

    # decoded document
    html = (page.content).decode('utf-8')

    # extract all jobs
    regBraces = "\{.*\}"
    jobmap = [line for line in html.split('\n') if "jobmap" in line and "{" in line]

    result = []
    for i in range(1, len(jobmap)):
        
        
        jobmap_obj = re.findall(regBraces, jobmap[i])[0]
        jobmap_obj = demjson.decode(jobmap_obj)
        jobmap_obj['view_url'] = view_url.format(jobmap_obj['jk'])

        result.append("\n\tTitle: {} at {}, \n\tcity: {}, \n\tview at: {}".format(jobmap_obj['title'], jobmap_obj['cmp'], jobmap_obj['city'], jobmap_obj['view_url']))

    _str = ""
    for i in range(len(result)):
        _str += "({}) : {} \n\n".format(i, result[i])

    return _str


# -------------------------------------------------------------------------- #

# -------------------------------------------------------------------------- #
                                # Telegram


def getJobs(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=fetchJobs())

get_handler = CommandHandler('getJobs', getJobs)
dispatcher.add_handler(get_handler)


updater.start_polling()
# -------------------------------------------------------------------------- #
