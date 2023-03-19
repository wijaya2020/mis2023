#This example uses Python 2.7 and the python-request library.

from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import pprint

url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'

parameters = {
  'start': 1 ,
  'limit' : 10,
  'convert':'USD'
}

headers = {
  'Accepts': 'application/json',
  'X-CMC_PRO_API_KEY': 'ee0e9b1a-351a-435a-89a9-b25cc8036d58',
}

session = Session()
session.headers.update(headers)

response = session.get(url, params=parameters)

data = json.loads(response.text)["data"]
info = ""

for item in data:
  cmc_rank = item["cmc_rank"]
  name = item["name"]
  symbol = item["symbol"]
  price = item["quote"]["USD"]["price"]
  percent_change_24h = item["quote"]["USD"]["percent_change_24h"] 
  percent_change_7d = item["quote"]["USD"]["percent_change_7d"] 
  market_cap = item["quote"]["USD"]["market_cap"]
  market_cap_dominance = item["quote"]["USD"]["market_cap_dominance"]
  volume_24h = item["quote"]["USD"]["volume_24h"]

  # format price and number
  price = '{:,.2f}'.format(price)
  percent_change_24h = '{:+.2%}'.format(percent_change_24h/100) 
  percent_change_7d = '{:+.2%}'.format(percent_change_7d/100)
  market_cap = "$" + '{:,.3f}'.format(market_cap)
  market_cap_dominance = '{:,.2%}'.format( market_cap_dominance/100) 
  volume_24h = "$" + '{:,.3f}'.format(volume_24h)

  info += "Rank   : " + "#" + str(cmc_rank) + "\n" + \
          "Name   : " + name + "\n" + \
          "Symbol : " + symbol + "\n" + \
          "Price  : " + "$" + str(price) + "\n" + \
          "24h %  : " + str(percent_change_24h) + "\n" + \
          "7d %   : " + str(percent_change_7d) + "\n" + \
          "Market Cap : " + str(market_cap) + "\n"  + \
          "volume(24h): " + str(volume_24h) + "\n"  + \
          "Market Cap Dominance : " + str(market_cap_dominance) + "\n"  + "\n"  
  
print(info)

timestamp = json.loads(response.text)["status"]["timestamp"]
timestamp = "Last Update : " + timestamp + " (UTC time)" 
print(timestamp)
 
