from slackclient import SlackClient
from oauth2client.service_account import ServiceAccountCredentials

import requests
import json
import time
import gspread

AuthToken = "xoxp-2170902585-79013916674-248543737477-06884267d4b84725365126f0ad6421c3"
BotToken = "xoxb-249274400247-AVDpFZJa1zcgjs2MrXawyEqW"
slack_client = SlackClient(BotToken)

AT_BOT = "@pghelper"

Example_Command = "Use @pghelper roll YOUR_RAW_NUMBER"



from oauth2client.service_account import ServiceAccountCredentials

def auth_gss_client(path, scopes):
    credentials = ServiceAccountCredentials.from_json_keyfile_name(path,
                      scopes)
    return gspread.authorize(credentials)


def bot_response(command, channel):
    response = handle_command(command)
    if response is None:
        response = Example_Command
    slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)     

def handle_command(command):
    command = command.strip()
    dicts = {"roll": "roll_cal"}
    ommand_list=[]

    try:
        command_list = command.split(" ")
    except:
        print("Error when split command")

    if len(command_list) < 1:
        return None
    
    if command_list[0].strip() in dicts.keys():
        if command_list[0] == "roll":
            print (command_list[1]).isdigit()
            if len(command_list)>1 and (command_list[1]).isdigit():
                return roll_call(command_list[1])
        return None
    return None

def roll_call(number):

    spreadsheet_key_path = 'spreadsheet_key'
    with open(spreadsheet_key_path) as f:
        key = f.read().strip()
        auth_json_path = 'auth.json'
        f = open("setup.json", "r")
        #gss_scopes = json.loads(f.read())["gss_scopes"]
        gss_scopes = ['https://spreadsheets.google.com/feeds']
        gss_client = auth_gss_client(auth_json_path, gss_scopes)
        wks = gss_client.open_by_key(key)
        sheet = wks.sheet1
        cell = "B"+number
        sheet.update_acell(cell , "v")

    return "Roll call for %s" % number

def parse_slack_output(slack_rtm_output):

    output = slack_rtm_output
    for opt in output:
        if output and len(output) > 0:
            if 'content' in opt and AT_BOT in opt['content']:
                return opt['content'].split(AT_BOT)[1].strip().lower(),opt['channel']
    return None,None

if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1
    if slack_client.rtm_connect():
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                bot_response(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connect Slack failed")
