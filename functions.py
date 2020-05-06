import json
import requests

BANNED_WORDS = (open('files/swearWords.txt', 'r').read().replace(" ", "").split(",") +
                open('files/swearWordsPL.txt', 'r').read().replace("'", "").replace("\n", "").replace(" ", "").split(
                    ","))


def update_covid_database(confirmed_localization, deaths_localization, recovered_localization):
    c_req = requests.get(
        'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data'
        '/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')
    d_req = requests.get(
        'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data'
        '/csse_covid_19_time_series/time_series_covid19_deaths_global.csv')
    r_req = requests.get(
        'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data'
        '/csse_covid_19_time_series/time_series_covid19_recovered_global.csv')
    with open(confirmed_localization, "w") as c_file:
        c_file.write(c_req.text)
    with open(deaths_localization, "w") as d_file:
        d_file.write(d_req.text)
    with open(recovered_localization, "w") as r_file:
        r_file.write(r_req.text)


def write_json(data):
    try:
        print("Trying to save to file...")
        with open("files/data.json", 'w') as f:
            print(data)
            json.dump(data, f)
            print("Saved")
    except:
        print("Couldnt write to JSON file")


def contains_banned_words(message):
    print("Looking for curse words ( ͡° ͜ʖ ͡°)")
    if len(message.content)==0:
        return False
    if not(" " in message.content):
        print("No spaces found ( ͡° ͜ʖ ͡°)")
        for word in BANNED_WORDS:
            if word==message.content:
                return True
    else:
        for el in message.content.split(" "):

            for word in BANNED_WORDS:
                if el==word:
                    print("Found banned word ( ͡° ͜ʖ ͡°)")
                    return True
    return False


def open_json():
    try:
        with open("files/data.json", 'r') as f:
            data = json.load(f)
            print("Opened json file")
            return data
    except FileNotFoundError:
        with open("files/data.json", 'x') as f:
            data = {'people': []}
            data['people'].append({
                'userID': 0,
                'xp': 0,
                'level' : 1
            })
            json.dump(data, f)
            print("Created json file")
            return data