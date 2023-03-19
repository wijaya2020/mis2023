import firebase_admin
from firebase_admin import credentials, firestore
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

import requests
from bs4 import BeautifulSoup

from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import pprint


#utc time 23pm = 7am taiwan
#utc time 3pm = 23pm taiwan

from apscheduler.schedulers.blocking import BlockingScheduler
sched = BlockingScheduler()

@sched.scheduled_job("interval", minutes=1)
#@sched.scheduled_job(timed_job, 'cron', day_of_week='mon-fri', hour='7-23')
# weeks / days/ hours/ minutes / seconds
 
def timed_job():
    
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'

    parameters = {
      'start': 1 ,
      'limit' : 108,
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
      
      doc = {
                "Rank2": cmc_rank,
                "Name2": name,
                "Symbol": symbol,
                "Price": price,
                "Percent_Change_24h": percent_change_24h,
                "Percent_Change_7d": percent_change_7d,
                "Market Cap": market_cap,
                "volume_24h": volume_24h,
                "Market Cap Dominance": market_cap_dominance
             }

      doc_ref = db.collection("cryptocurrency").document(symbol)
      doc_ref.set(doc)

      # format price and number
      if (price < 0.0001):
        price = '{:,.8f}'.format(price)
      elif (price < 0.001):
        price = '{:,.7f}'.format(price)
      elif (price < 0.01):
        price = '{:,.6f}'.format(price)
      elif (price < 0.1):
        price = '{:,.5f}'.format(price)      
      elif (price < 1):
        price = '{:,.4f}'.format(price)      
      else:
        price = '{:,.2f}'.format(price)
        
      percent_change_24h = '{:+.2%}'.format(percent_change_24h/100) 
      percent_change_7d = '{:+.2%}'.format(percent_change_7d/100)
      market_cap = '{:,.0f}'.format(market_cap)
      market_cap_dominance = '{:,.2%}'.format( market_cap_dominance/100) 
      volume_24h = '{:,.0f}'.format(volume_24h)

      info += "Rank   : " + "#" + str(cmc_rank) + "<br>" + \
              "Name   : " + name + "<br>" + \
              "Symbol : " + symbol + "<br>" + \
              "Price  : " + "$" + str(price) + "<br>" + \
              "24h %  : " + str(percent_change_24h) + "<br>" + \
              "7d %   : " + str(percent_change_7d) + "<br>" + \
              "Market Cap : " + "$" + str(market_cap) + "<br>"  + \
              "volume_24h: " + "$" + str(volume_24h) + "<br>"  + \
              "Market Cap Dominance : " + str(market_cap_dominance) + "<br><br>"  
      
    
    timestamp = json.loads(response.text)["status"]["timestamp"]
    timestampDate = timestamp[0:10]
    timestampTime = timestamp[11:23]
    lastUpdate = "近期加密貨幣已爬蟲及存檔完畢，網站最近更新日期為： " 
    lastUpdate += timestampDate + " / " + timestampTime + " (UTC Time)" + "<br><br>" 
    
    doc = {
          "timestampDate": timestampDate,
          "timestampTime": timestampTime
    }

    doc_ref = db.collection("cryptocurrency").document("timestamp")
    doc_ref.set(doc)

sched.start()
