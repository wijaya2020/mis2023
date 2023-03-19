import firebase_admin
from firebase_admin import credentials, firestore
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

import requests
from bs4 import BeautifulSoup

from flask import Flask, render_template, request, abort, make_response, jsonify
from datetime import datetime, timezone, timedelta

from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json

from linebot import (
    LineBotApi, WebhookHandler
 )
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage
)
line_bot_api = LineBotApi("eL+gmj3lyu5VYqwvRzzl2Q5t2nsq7qOBFzHU+/jhPr0pFjfUDhgPWz0o29BgfBppYz8u28wPu/MF5f/zV1R4jlZ47uFBEdH2Wh8DUi9Sc0p2Oa8bzT3CBf3KR++J/SXQLyPmpfXNwN5/gY8ju14UJAdB04t89/1O/w1cDnyilFU=")
handler = WebhookHandler("95907cca0ae5ecf5aa0c7453174d97da")

app = Flask(__name__)

@app.route("/")
def index():
    homepage = "<h1>清昊Python+Flask+Linebot+dialogflow測試網頁</h1>"
    homepage += "<a href=/mis>MIS</a><br>"
    homepage += "<a href=/current>開啟網頁及顯示日期時間</a><br>"
    homepage += "<a href=/welcome?nick=魏清昊>開啟網頁及傳送使用者暱稱</a><br>"
    homepage += "<a href=/hi>計算總拜訪次數</a><br>"
    homepage += "<a href=/about>Qinghao Profile</a><br><br>"
    homepage += "<a href=/spiderMovie>電影爬蟲(含分級資訊)</a><br>"
    homepage += "<a href=/spider>讀取開眼電影即將上映影片，寫入Firestore</a><br>"
    homepage += "<a href=/search>輸入片名關鍵字，進行電影搜尋(含分級資訊)</a><br><br>"
    homepage += "<a href=/crypto>crypto listing price </a><br>"
    homepage += "<a href=/cryptoUpload>upload data crypto listing price to Firestore</a><br>"
    homepage += "<a href=/cryptosearch>輸入加密貨幣符號，進行搜尋</a><br><br>"
    
    return homepage

@app.route("/mis")
def course():
    return "<h1>資訊管理導論</h1>"

@app.route("/current")
def current():
    now = datetime.now()
    return render_template("current.html", datetime = str(now))

@app.route("/welcome", methods=["GET", "POST"])
def welcome():
    user = request.values.get("nick")
    return render_template("welcome.html", name=user)

@app.route("/hi")
def hi():
    # 載入原始檔案
    f = open("count.txt", "r")
    count = int(f.read())
    f.close()

    # 計數加1
    count += 1

    # 覆寫檔案
    f = open("count.txt", "w")
    f.write(str(count))
    f.close()
    return "本網站總拜訪人次：" + str(count)

@app.route("/login", methods=["POST","GET"])
def login():
    if request.method == "POST":
        user = request.form["nm"]
        return "您輸入的名字為：" + user 
    else:
        return render_template("login.html")

@app.route("/about")
def about():
    return render_template("about2.html")

@app.route("/spider")
def spider():
    url = "http://www.atmovies.com.tw/movie/next/"
    Data = requests.get(url)
    Data.encoding = "utf-8"
    sp = BeautifulSoup(Data.text, "html.parser")
    result=sp.select(".filmListAllX li")
    lastUpdate = sp.find("div", class_="smaller09").text[5:]

    for item in result:
        MovieRating = "本片尚無分級資料"
        pictures = item.select("img")
        for pic in pictures:
            picName = pic.get("src")
            if (picName[0:7] == "/images"):
              if (picName[12:] == "G.gif"):
                  MovieRating = "普遍級(0歲以上)"        
              elif (picName[12:] == "P.gif"):
                  MovieRating = "保護級(6歲以上)"
              elif (picName[12:] == "F2.gif"):
                  MovieRating = "輔導12歲級(12歲以上)"
              elif (picName[12:] == "F5.gif"):
                  MovieRating = "輔導15歲級(15歲以上)"
              else:
                  MovieRating = "限制級(18歲以上)"
            
        picture = item.find("img").get("src").replace(" ", "")    
        title = item.find("div", class_="filmtitle").text
        movie_id = item.find("div", class_="filmtitle").find("a").get("href").replace("/", "").replace("movie", "")
        hyperlink = "http://www.atmovies.com.tw" + item.find("div", class_="filmtitle").find("a").get("href")
        show = item.find("div", class_="runtime").text.replace("上映日期：", "")
        show = show.replace("片長：", "")
        show = show.replace("分", "")
        showDate = show[0:10]
        showLength = show[13:]
        
      
        doc = {
            "title": title,
            "picture": picture,
            "hyperlink": hyperlink,
            "showDate": showDate,
            "showLength": showLength,
            "lastUpdate": lastUpdate,
            "MovieRating": MovieRating
         }

        doc_ref = db.collection("電影").document(movie_id)
        doc_ref.set(doc)
    return "近期上映電影已爬蟲及存檔完畢，網站最近更新日期為：" + lastUpdate 

@app.route("/spiderMovie")
def spiderMovie():
    
    url = "http://www.atmovies.com.tw/movie/next/"
    Data = requests.get(url)
    Data.encoding = "utf-8"
    sp = BeautifulSoup(Data.text, "html.parser")
    result=sp.select(".filmListAllX li")
    lastUpdate = sp.find("div", class_="smaller09").text[5:]
    info = "作者：清昊<br>[開眼電影即將上映電影]最近更新日期為：" + lastUpdate +"<br><br>"
    MovieRating = ""
    picture = ""
    PictureText = ""

    for item in result:
      MovieRating = "本片尚無分級資料"
      pictures = item.select("img")
        
      for pic in pictures:
        picName = pic.get("src")
        if (picName[0:7] == "/images"):
          if (picName[12:] == "G.gif"):
              MovieRating = "普遍級(0歲以上)"        
          elif (picName[12:] == "P.gif"):
              MovieRating = "保護級(6歲以上)"
          elif (picName[12:] == "F2.gif"):
              MovieRating = "輔導12歲級(12歲以上)"
          elif (picName[12:] == "F5.gif"):
              MovieRating = "輔導15歲級(15歲以上)"
          else:
              MovieRating = "限制級(18歲以上)"
        
      picture = item.find("img").get("src").replace(" ", "")   
      
      title = item.find("div", class_="filmtitle").text
      hyperlink = "http://www.atmovies.com.tw" + item.find("div", class_="filmtitle").find("a").get("href")
      show = item.find("div", class_="runtime").text[5:15]
      duration = item.find("div", class_="runtime").text[21:]
      info += "影片海報：" + picture + "<br>"  
      info += "影片片名：" + title + "<br>"  
      info += "影片介紹：" + hyperlink + "<br>"  
      info += "上映日期：" + show + "<br>"  
      info += "影片片長：" + duration + "<br>" 
      info += "影片分級：" + MovieRating + "<br> <br>" 

    return info

@app.route("/search", methods=["POST","GET"])
def search():
    if request.method == "POST":
        MovieTitle = request.form["MovieTitle"]  
        collection_ref = db.collection("電影")
        #docs = collection_ref.where("title","==", "濁水漂流").get()
        docs = collection_ref.order_by("showDate").get()

        info = ""
        for doc in docs:
            if MovieTitle in doc.to_dict()["title"]: 
                info += "影片片名：" + doc.to_dict()["title"] + "<br>" 
                info += "影片海報：" + doc.to_dict()["picture"] + "<br>"
                info += "影片介紹：" + doc.to_dict()["hyperlink"] + "<br>"
                info += "影片片長：" + doc.to_dict()["showLength"] + " 分鐘<br>" 
                info += "上映日期：" + doc.to_dict()["showDate"] + "<br>"          
                info += "影片分級：" + doc.to_dict()["MovieRating"] + "<br><br>"          

        return info
    else:
        return render_template("input.html")

@app.route("/crypto")
def crypto():
    
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

      # format price and number
      price = '{:,.2f}'.format(price)
      percent_change_24h = '{:+.2%}'.format(percent_change_24h/100) 
      percent_change_7d = '{:+.2%}'.format(percent_change_7d/100)
      market_cap = '{:,.0f}'.format(market_cap)
      volume_24h = '{:,.0f}'.format(volume_24h)
      market_cap_dominance = '{:,.2%}'.format( market_cap_dominance/100) 

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
    lastUpdate = "Last Update : " + timestampDate + " / " + timestampTime + " (UTC Time)" + "<br><br>" 
    
    return lastUpdate + info

@app.route("/cryptoUpload")
def cryptoUpload():
    
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
                "Rank": cmc_rank,
                "Name": name,
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

    #return lastUpdate + info 
    return lastUpdate 

@app.route("/cryptosearch", methods=["POST","GET"])
def cryptosearch():
    if request.method == "POST":
        CryptoSymbol = request.form["CryptoSymbol"]  

        collection_ref = db.collection("cryptocurrency")
        #docs = collection_ref.where("title","==", "濁水漂流").get()
        docs = collection_ref.order_by("Rank").get()

        info = ""
        timestampDate =""
        timestampTime =""

        for doc in docs:
            if CryptoSymbol.upper() in doc.to_dict()["Symbol"]:
                
                #get data
                cmc_rank = str(doc.to_dict()["Rank"])
                name = doc.to_dict()["Name"]
                symbol = doc.to_dict()["Symbol"]
                price = doc.to_dict()["Price"]
                percent_change_24h = doc.to_dict()["Percent_Change_24h"] 
                percent_change_7d = doc.to_dict()["Percent_Change_7d"] 
                market_cap = doc.to_dict()["Market Cap"]
                volume_24h = doc.to_dict()["volume_24h"]
                market_cap_dominance = doc.to_dict()["Market Cap Dominance"]

                # format price and number
                price = '{:,.2f}'.format(price)
                percent_change_24h = '{:+.2%}'.format(percent_change_24h/100) 
                percent_change_7d = '{:+.2%}'.format(percent_change_7d/100)
                #market_cap = '{:,.0f}'.format(market_cap)
                #volume_24h = '{:,.0f}'.format(volume_24h)
                market_cap_dominance = '{:,.2%}'.format( market_cap_dominance/100) 

                info += "Rank   : " + "#" + str(cmc_rank) + "<br>" 
                info += "Name   : " + name + "<br>" 
                info += "Symbol : " + symbol + "<br>" 
                info += "Price  : " + "$" + str(price) + "<br>" 
                info += "24h %  : " + str(percent_change_24h) + "<br>" 
                info += "7d %   : " + str(percent_change_7d) + "<br>" 
                info += "Market Cap : " + "$" + str(market_cap) + "<br>"  
                info += "volume_24h: " + "$" + str(volume_24h) + "<br>"  
                info += "Market Cap Dominance : " + str(market_cap_dominance) + "<br>"  
                info += "<br>" 
        

        doc_ref = db.document("cryptocurrency/timestamp")
        doc = doc_ref.get()
        result = doc.to_dict()
        timestampDate = result.get("timestampDate")
        timestampTime = result.get("timestampTime")

        #print("文件內容為：{}".format(result))
        #print("教師姓名："+ result.get("name"))
        #print("教師郵件：" + result["mail"])

        lastUpdate = "Last Update : " + timestampDate + " / " + timestampTime + " (UTC Time)" + "<br><br>" 
        return lastUpdate + info   
    else:
        return render_template("search_by_symbol.html")

@app.route("/callback", methods=["POST"])
def callback():
    # get X-Line-Signature header value
    signature = request.headers["X-Line-Signature"]

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = event.message.text
    
    #ALL - latest price
    if (message[:4].upper() == 'RANK'):
        res = searchCryptoRANK(message)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = res))
    
    #A - latest price
    elif (message[:6].upper() == 'LATEST'):
        res = searchCryptoLATEST(message[7:])
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = res))

    #B - top 10 gainners 24h chg %    
    elif (message[:8].upper() == 'GAINNERS'):
        res = searchCryptoGAINNERS(message)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = res))

    #C - top 10 losers 24h chg %   
    elif (message[:6].upper() == 'LOSERS'):
        res = searchCryptoLOSERS(message)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = res))

    #D - top 10 24h vol %   
    elif (message[:3].upper() == 'VOL'):
        res = searchCryptoVOL(message)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = res))

    #E - HOT coin / myFav coin (manual setting)  
    elif (message[:3].upper() == 'FAV'):
        res = searchCryptoFAV(message)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = res))

    #F - print list coin symbol & name   
    elif (message[:4].upper() == 'LIST'):
        res = searchCryptoLIST(message)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = res))

    #G - crypto terms   
    elif (message[:5].upper() == 'TERMS'):
        res = searchCryptoTERMS(message)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = res))

    #Z or ? - help  (how to type keyword) 
    elif (message[:4].upper() == 'HELP' or message[:1] == '?'):
        res = searchCryptoHELP(message)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = res))

    else:
        info = "Search keyword format : "
        info += "\n\n" 
        info += "0. Type: RANK --> for Top 10 coin latest price." 
        info += "\n\n" 
        info += "1. Type: LATEST <coin symbol> --> for a coin latest price." 
        info += "\n" 
        info += "   e.g.: LATEST BTC" 
        info += "\n\n" 
        info += "2. Type: GAINNERS --> for Top 10 coin gainners 24h chg%." 
        info += "\n\n" 
        info += "3. Type: LOSERS --> for Top 10 coin losers 24h chg%." 
        info += "\n\n" 
        info += "4. Type: VOL --> for Top 10 coin 24h vol chg%." 
        info += "\n\n" 
        info += "5. Type: FAV --> or My favourite's coin." 
        info += "\n\n" 
        info += "6. Type: LIST --> for List of all coin's names & symbols." 
        info += "\n\n" 
        info += "7. Type: TERMS --> for cypto terms."
        info += "\n\n" 
        info += "8. Type: HELP or ?? --> for help how to type search keyword." 
        info += "\n\n" 

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text = "我是Crypto機器人，您輸入的是：" + message + "。 祝福您有個美好的一天！\n\n" + info))

def searchCryptoRANK(keyword):
    #info = "您要查詢加密貨幣符號，關鍵字為：" + keyword + "\n\n"    
    info = "Latest Price Top 30 Coin by Rank：" + keyword + "\n\n"    
    
    collection_ref = db.collection("cryptocurrency")
    docs = collection_ref.order_by("Rank").limit(30).get()

    for doc in docs:
        #get data        
        cmc_rank = doc.to_dict()["Rank"]
        name = doc.to_dict()["Name"]
        symbol = doc.to_dict()["Symbol"]
        price = doc.to_dict()["Price"]
        percent_change_24h = doc.to_dict()["Percent_Change_24h"] 
        percent_change_7d = doc.to_dict()["Percent_Change_7d"] 
        market_cap_dominance = doc.to_dict()["Market Cap Dominance"]

        # format price and number
        price = '{:,.2f}'.format(price)
        percent_change_24h = '{:+.2%}'.format(percent_change_24h/100) 
        percent_change_7d = '{:+.2%}'.format(percent_change_7d/100)
        market_cap_dominance = '{:,.2%}'.format(market_cap_dominance/100) 

        info += "Rank   : " + "#" + str(cmc_rank) + "\n" 
        info += "Name   : " + name + "\n" 
        info += "Symbol : " + symbol + "\n" 
        info += "Price  : " + "$" + str(price) + "\n" 
        info += "24h %  : " + str(percent_change_24h) + "\n" 
        info += "7d %   : " + str(percent_change_7d) + "\n" 
        info += "Market Cap Dominance : " + str(market_cap_dominance) 
        info += "\n\n"

    doc_ref = db.document("cryptocurrency/timestamp")
    doc = doc_ref.get()
    result = doc.to_dict()
    timestampDate = result.get("timestampDate")
    timestampTime = result.get("timestampTime")

    lastUpdate = "Last Update : " + timestampDate + " / " + timestampTime + " (UTC Time)" + "\n\n" 

    return info + lastUpdate 

def searchCryptoLATEST(keyword):
    #info = "您要查詢加密貨幣符號，關鍵字為：" + keyword + "\n\n"    
    info = "Latest Price Top 10：" + keyword + "\n\n"    
    
    collection_ref = db.collection("cryptocurrency")
    docs = collection_ref.order_by("Rank").limit(10).get()
    found = False

    for doc in docs:
        if keyword.upper() in doc.to_dict()["Symbol"]:
            found = True    
            #get data        
            cmc_rank = doc.to_dict()["Rank"]
            name = doc.to_dict()["Name"]
            symbol = doc.to_dict()["Symbol"]
            price = doc.to_dict()["Price"]
            percent_change_24h = doc.to_dict()["Percent_Change_24h"] 
            percent_change_7d = doc.to_dict()["Percent_Change_7d"] 
            market_cap_dominance = doc.to_dict()["Market Cap Dominance"]

            # format price and number
            price = '{:,.2f}'.format(price)
            percent_change_24h = '{:+.2%}'.format(percent_change_24h/100) 
            percent_change_7d = '{:+.2%}'.format(percent_change_7d/100)
            market_cap_dominance = '{:,.2%}'.format( market_cap_dominance/100) 

            info += "Rank   : " + "#" + str(cmc_rank) + "\n" 
            info += "Name   : " + name + "\n" 
            info += "Symbol : " + symbol + "\n" 
            info += "Price  : " + "$" + str(price) + "\n" 
            info += "24h %  : " + str(percent_change_24h) + "\n" 
            info += "7d %   : " + str(percent_change_7d) + "\n" 
            info += "Market Cap Dominance : " + str(market_cap_dominance) + "\n\n"

        doc_ref = db.document("cryptocurrency/timestamp")
        doc = doc_ref.get()
        result = doc.to_dict()
        timestampDate = result.get("timestampDate")
        timestampTime = result.get("timestampTime")

        lastUpdate = "Last Update : " + timestampDate + " / " + timestampTime + " (UTC Time)" + "\n\n" 
        
    if not found:
       info += "很抱歉，目前無符合這個關鍵字的相關電影喔"
       return info                   
    else:
       return info + lastUpdate 

def searchCryptoGAINNERS(keyword):
    info = "Top 10 Gainners 24h chg%：" + "\n\n"

    collection_ref = db.collection("cryptocurrency")
    docs = collection_ref.order_by("Percent_Change_24h", direction=firestore.Query.DESCENDING).limit(10).get()
    
    found = False
    
    for doc in docs:
        percent_change_24h = doc.to_dict()["Percent_Change_24h"] 
        
        if (percent_change_24h >= 0):        
            found = True
            symbol = doc.to_dict()["Symbol"]
            price = doc.to_dict()["Price"]
            #percent_change_24h = doc.to_dict()["Percent_Change_24h"] 

            price = '{:,.2f}'.format(price)
            percent_change_24h = '{:+.2%}'.format(percent_change_24h/100) 
            #percent_change_7d = '{:+.2%}'.format(percent_change_7d/100)
            #market_cap = '{:,.0f}'.format(market_cap)
            #market_cap_dominance = '{:,.2%}'.format( market_cap_dominance/100) 
            #volume_24h = '{:,.0f}'.format(volume_24h)

            info += "Symbol : " + symbol + "\n" 
            info += "Price  : " + "$" + str(price) + "\n" 
            info += "24h %: " + str(percent_change_24h) + "\n\n" 
    
    doc_ref = db.document("cryptocurrency/timestamp")
    doc = doc_ref.get()
    result = doc.to_dict()
    timestampDate = result.get("timestampDate")
    timestampTime = result.get("timestampTime")
        
    lastUpdate = "Last Update : " + timestampDate + " / " + timestampTime + " (UTC Time)" + "\n\n" 
          
    if not found:
       info += "No Gainners ! It's look like all coin is below 0 %"
       return info + lastUpdate                   
    else:
       return info + lastUpdate 

def searchCryptoLOSERS(keyword):
    info = "Top 10 Losers 24h chg%：" + "\n\n"

    collection_ref = db.collection("cryptocurrency")
    docs = collection_ref.order_by("Percent_Change_24h").limit(10).get()
    
    found = False

    for doc in docs:
        
        percent_change_24h = doc.to_dict()["Percent_Change_24h"] 

        if (percent_change_24h <= 0):        
            found = True
        
            symbol = doc.to_dict()["Symbol"]
            price = doc.to_dict()["Price"]
            percent_change_24h = doc.to_dict()["Percent_Change_24h"] 

            price = '{:,.2f}'.format(price)
            percent_change_24h = '{:+.2%}'.format(percent_change_24h/100) 


            info += "Symbol : " + symbol + "\n" 
            info += "Price  : " + "$" + str(price) + "\n" 
            info += "24h %: " + str(percent_change_24h) + "\n\n" 

    doc_ref = db.document("cryptocurrency/timestamp")
    doc = doc_ref.get()
    result = doc.to_dict()
    timestampDate = result.get("timestampDate")
    timestampTime = result.get("timestampTime")
    
    lastUpdate = "Last Update : " + timestampDate + " / " + timestampTime + " (UTC Time)" + "\n" 
          
    if not found:
       info += "No Losers! It's look like all coin is above 0 %." + "\n\n"
       return info + lastUpdate                   
    else:
       return info + lastUpdate 

def searchCryptoVOL(keyword):
    info = "Top 10 24h Volume：" + "\n\n"

    collection_ref = db.collection("cryptocurrency")
    docs = collection_ref.order_by("volume_24h", direction=firestore.Query.DESCENDING).limit(10).get()

    for doc in docs:
        symbol = doc.to_dict()["Symbol"]
        price = doc.to_dict()["Price"]
        volume_24h = doc.to_dict()["volume_24h"]
        
        price = '{:,.2f}'.format(price)
        volume_24h = '{:,.0f}'.format(volume_24h)

        info += "Symbol : " + symbol + "\n" 
        info += "Price  : " + "$" + str(price) + "\n" 
        info += "Vol 24h: " + "$" + str(volume_24h) + "\n\n" 
    
    doc_ref = db.document("cryptocurrency/timestamp")
    doc = doc_ref.get()
    result = doc.to_dict()
    timestampDate = result.get("timestampDate")
    timestampTime = result.get("timestampTime")

    lastUpdate = "Last Update : " + timestampDate + " / " + timestampTime + " (UTC Time)" + "\n\n" 
          
    return info + lastUpdate
 
def searchCryptoFAV(keyword):
    info = "My Favourite's Coin：" + "\n\n"

    collection_ref = db.collection("cryptocurrency")
    docs = collection_ref.order_by("Rank").get()

    for doc in docs:
        symbol = doc.to_dict()["Symbol"]
        
        if (symbol == "BTC" or \
            symbol == "ADA" or \
            symbol == "SAND" or \
            symbol == "WAXP"):
            
            cmc_rank = doc.to_dict()["Rank"]
            name = doc.to_dict()["Name"]
            price = doc.to_dict()["Price"]
            percent_change_24h = doc.to_dict()["Percent_Change_24h"] 
            percent_change_7d = doc.to_dict()["Percent_Change_7d"] 
            market_cap_dominance = doc.to_dict()["Market Cap Dominance"]
            
            # format price and number
            price = '{:,.2f}'.format(price)
            percent_change_24h = '{:+.2%}'.format(percent_change_24h/100) 
            percent_change_7d = '{:+.2%}'.format(percent_change_7d/100)
            market_cap_dominance = '{:,.2%}'.format( market_cap_dominance/100) 

            info += "Rank   : " + "#" + str(cmc_rank) + "\n" 
            info += "Name   : " + name + "\n" 
            info += "Symbol : " + symbol + "\n" 
            info += "Price  : " + "$" + str(price) + "\n" 
            info += "24h %  : " + str(percent_change_24h) + "\n" 
            info += "7d %   : " + str(percent_change_7d) + "\n" 
            info += "Market Cap Dominance : " + str(market_cap_dominance) + "\n"   
            info += "\n"

        doc_ref = db.document("cryptocurrency/timestamp")
        doc = doc_ref.get()
        result = doc.to_dict()
        timestampDate = result.get("timestampDate")
        timestampTime = result.get("timestampTime")

        lastUpdate = "Last Update : " + timestampDate + " / " + timestampTime + " (UTC Time)" + "\n\n" 
          
    return info

def searchCryptoLIST(keyword):
    info = "List of Coin Symbol (sort by alaphabet)：" + "\n\n"

    collection_ref = db.collection("cryptocurrency")
    docs = collection_ref.order_by("Symbol").limit(100).get()

    for doc in docs:      
        name = doc.to_dict()["Name"]
        symbol = doc.to_dict()["Symbol"]
        info += symbol + " (" + name + ")"   
        info += "\n" 
    
    return info                   

def searchCryptoTERMS(keyword):
    info = "Terms in Crypto you must know :" 
    info += "\n\n" 
    info += "1. FOMO = Fear of Missing Out." 
    info += "\n\n" 
    info += "2. FUD  =  Fear, Uncertainty, and Doubt." 
    info += "\n\n" 
    info += "3. HOLD = Hold On for Dear Life."
    info += "\n\n" 
    info += "4. Pump and Dump."
    info += "\n" 
    info += "   Pump is means that the price of a coin will be increased." 
    info += "\n" 
    info += "   Dump is means that the price of a coin will be decreased." 
    info += "\n\n" 
    info += "5. Bearish and Bullish."
    info += "\n" 
    info += "   Bearish is a term when a prices stagnate and decline."
    info += "\n" 
    info += "   Bullish is a term when a prices has increased." 
    info += "\n\n" 
    return info

def searchCryptoHELP(keyword):
    info = "Search keyword format : "
    info += "\n\n" 
    info += "0. Type: RANK --> for Top 30 coin latest price." 
    info += "\n\n"    
    info += "1. Type: LATEST <coin symbol> --> for a coin latest price." 
    info += "\n" 
    info += "   e.g.: LATEST BTC" 
    info += "\n\n" 
    info += "2. Type: GAINNERS --> for Top 10 coin gainners 24h chg%." 
    info += "\n\n" 
    info += "3. Type: LOSERS --> for Top 10 coin losers 24h chg%." 
    info += "\n\n" 
    info += "4. Type: VOL --> for Top 10 coin 24h vol chg%." 
    info += "\n\n" 
    info += "5. Type: FAV --> for My favourite's coin." 
    info += "\n\n" 
    info += "6. Type: LIST --> for List of all coin's names & symbols" 
    info += "\n\n" 
    info += "7. Type: TERMS --> for cypto terms."
    info += "\n\n" 
    info += "8. Type: HELP or ? --> for help how to type search keyword." 
    info += "\n\n" 
    return info

#@app.route("/webhook", methods=["POST"])
#def webhook():
#    # build a request object
#    req = request.get_json(force=True)
#    # fetch queryResult from json
#    action =  req.get("queryResult").get("action")
#    msg =  req.get("queryResult").get("queryText")
#    info = "動作：" + action + "； 查詢內容：" + msg
    
#    #if (action == "CoinPrice"):
#    #    city =  req.get("queryResult").get("parameters").get("coin")
#    #    info = "查詢都市名稱：" + coin
#    #    return make_response(jsonify({"fulfillmentText": info}))

if __name__ == "__main__":
    app.run()

