import requests

req = requests.get('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')
with open('../plik.csv', 'w') as csv:
    csv.write(req.text)