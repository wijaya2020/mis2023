#This example uses Python 2.7 and the python-request library.

from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import pprint

url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'

parameters = {
  'start': 1 ,
  'limit' : 5,
  'convert':'USD'
}

headers = {
  'Accepts': 'application/json',
  'X-CMC_PRO_API_KEY': '24da8ddc-ac4a-43ae-82bb-78a42e0a48a3',
}

session = Session()
session.headers.update(headers)

response = session.get(url, params=parameters)

data = json.loads(response.text)
info = ""

for item in data:
  cmc_rank = json.loads(response.text)["data"][0]["cmc_rank"]
  name = json.loads(response.text)["data"][0]["name"]
  symbol = json.loads(response.text)["data"][0]["symbol"]
  price = json.loads(response.text)["data"][0]["quote"]["USD"]["price"]
  percent_change_24h = json.loads(response.text)["data"][0]["quote"]["USD"]["percent_change_24h"] 
  percent_change_7d = json.loads(response.text)["data"][0]["quote"]["USD"]["percent_change_7d"] 
  market_cap = json.loads(response.text)["data"][0]["quote"]["USD"]["market_cap"]
  market_cap_dominance = json.loads(response.text)["data"][0]["quote"]["USD"]["market_cap_dominance"]
  volume_24h = json.loads(response.text)["data"][0]["quote"]["USD"]["volume_24h"]
  timestamp = json.loads(response.text)["status"]["timestamp"]

  price = "$" + '{:,.2f}'.format(price)
  percent_change_24h = '{:.2%}'.format(percent_change_24h/100) 
  percent_change_7d = '{:.2%}'.format(percent_change_7d/100) 
  market_cap = "$" + '{:,.3f}'.format(market_cap)
  market_cap_dominance = '{:,.2%}'.format( market_cap_dominance/100) 
  volume_24h = "$" + '{:,.3f}'.format(volume_24h)

  info += "Rank   : " + str(cmc_rank) + "\n" + \
        "Name   : " + name + "\n" + \
        "Symbol : " + symbol + "\n" + \
        "Price  : " + str(price) + "\n" + \
        "24h %  : " + str(percent_change_24h) + "\n" + \
        "7d %   : " + str(percent_change_7d) + "\n" + \
        "Market Cap : " + str(market_cap) + "\n"  + \
        "Market Cap Dominance : " + str(market_cap_dominance) + "\n"  + \
        "volume(24h): " + str(volume_24h) + "\n" +  "\n"
  
  print(info)

timestamp = "Last Update : " + timestamp + "UTC time" 
print(timestamp)