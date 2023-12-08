import requests
from bs4 import BeautifulSoup

import firebase_admin
from firebase_admin import credentials, firestore
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

from flask import Flask,render_template, request,make_response, jsonify
from datetime import datetime

import requests
from bs4 import BeautifulSoup


app = Flask(__name__)

@app.route("/")
def index():
	X = "作者:陳羿汶!2023-12-07a<br>"
	X += "<a href=/mis>資訊導論</a><br>"
	X += "<a href=/today>日期時間</a><br>"
	X += "<a href=/about>羿汶的網頁</a><br>"
	X += "<a href=/welcome?guest=Wanda>歡迎Wanda~ ~</a><br>"
	X += "<a href=/account>使用表單方式傳值</a><br><br>"
	X += "<a href=/wave>人選之人演員名單(按年齡由小到大)</a><br><br>"
	X += "<a href=/books>全部圖書</a><br>"
	X += "<a href=/search>根據書名關鍵字查詢圖書</a><br><br>"
	X += "<a href=/spider>網路爬蟲擷取子青老師課程資料</a><br><br>"
	X += "<a href=/movie>讀取開眼電影即將上映影片，寫入Firestore</a><br>"
	X += "<a href=/searchQ>查詢開眼電影即將上映影片</a><br><br>"
	X += "<a href=/movie_rate>讀取開眼電影即將上映影片(含分級資訊)，寫入Firestore</a><br>"
	return X

@app.route("/mis")
def course():
	return "<h1>資訊管理導論</h1>"

@app.route("/today")
def today():
	now = datetime.now()
	return render_template("today.html", datetime = str(now))

@app.route("/about")
def about():
	return render_template("about.html")

@app.route("/welcome", methods=["GET", "POST"])
def welcome():
    user = request.values.get("guest")
    return render_template("welcome.html", name=user)

@app.route("/account", methods=["GET", "POST"])
def account():
    if request.method == "POST":
        user = request.form["user"]
        pwd = request.form["pwd"]
        result = "您輸入的帳號是：" + user + "; 密碼為：" + pwd 
        return result
    else:
        return render_template("account.html")

@app.route("/wave")
def wave():
    Result = ""
    db = firestore.client()
    collection_ref = db.collection("人選之人─造浪者")    
    docs = collection_ref.order_by("birth",direction=firestore.Query.DESCENDING).get()    
    for doc in docs:         
        Result += "演員：{}".format(doc.to_dict()) + "<br>"    
    return Result

@app.route("/books")
def books():
	Result = ""
	db = firestore.client()
	collection_ref = db.collection("圖書精選")
	docs = collection_ref.order_by("anniversary").get()
	for doc in docs:
		bk = doc.to_dict()
		Result += "書名：<a href=" + bk["url"] + ">" + bk["title"] + "</a><br>"
		Result += "作者：" + bk["author"] + "<br>"
		Result += str(bk["anniversary"]) + "週年紀念版 " + "<br>"
		Result += "<img src = " + bk["cover"] + "></img><br><br>"
	return Result

@app.route("/search", methods=["GET", "POST"])
def search():
	if request.method == "POST":
		keyword = request.form["keyword"]
		Result = "您輸入的關鍵字是：" + keyword

		db = firestore.client()
		collection_ref = db.collection("圖書精選")
		docs = collection_ref.order_by("anniversary").get()
		for doc in docs:
			bk = doc.to_dict()
			if keyword in bk["title"]:
				Result += "書名：<a href=" + bk["url"] + ">" + bk["title"] + "</a><br>"
				Result += "作者：" + bk["author"] + "<br>"
				Result += str(bk["anniversary"]) + "週年紀念版 " + "<br>"
				Result += "<img src = " + bk["cover"] + "></img><br><br>"
		return Result
	else:
		return render_template("searchbk.html")

@app.route("/spider")
def spider():
	info = ""

	url = "https://www1.pu.edu.tw/~tcyang/course.html"
	Data = requests.get(url)
	Data.encoding = "utf-8"
	#print(Data.text)
	sp = BeautifulSoup(Data.text, "html.parser")
	result=sp.select(".team-box")

	for x in result:
		info += "<a href=" + x.find("a").get("href") + ">" + x.find("h4").text + "</a><br>"
		info += x.find("p").text + "<br>"
		info += x.find("a").get("href") + "<br>"
		info += "<img src=https://www1.pu.edu.tw/~tcyang/" + x.find("img").get("src") + " width=200 height=300" + "></img><br><br>"
	return info

@app.route("/movie")
def movie():
  url = "http://www.atmovies.com.tw/movie/next/"
  Data = requests.get(url)
  Data.encoding = "utf-8"
  sp = BeautifulSoup(Data.text, "html.parser")
  result=sp.select(".filmListAllX li")
  lastUpdate = sp.find("div", class_="smaller09").text[5:]

  for item in result:
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
        "lastUpdate": lastUpdate
      }

    db = firestore.client()
    doc_ref = db.collection("電影").document(movie_id)
    doc_ref.set(doc)    
  return "近期上映電影已爬蟲及存檔完畢，網站最近更新日期為：" + lastUpdate 

# @app.route("/search_movie")
# def search_movie():
#     info = ""
#     db = firestore.client()  
#     docs = db.collection("電影").get() 
#     for doc in docs:
#         if "飛鴨" in doc.to_dict()["title"]:
#             info += "片名：" + doc.to_dict()["title"] + "<br>" 
#             info += "海報：" + doc.to_dict()["picture"] + "<br>"
#             info += "影片介紹：" + doc.to_dict()["hyperlink"] + "<br>"
#             info += "片長：" + doc.to_dict()["showLength"] + " 分鐘<br>" 
#             info += "上映日期：" + doc.to_dict()["showDate"] + "<br><br>"           
#     return info

@app.route("/searchQ", methods=["POST","GET"])
def searchQ():
    if request.method == "POST":
        MovieTitle = request.form["MovieTitle"]
        info = ""
        db = firestore.client()     
        collection_ref = db.collection("電影")
        docs = collection_ref.order_by("showDate").get()
        for doc in docs:
        	mv = doc.to_dict()
        	if MovieTitle in mv["title"]:
        		info += "片名：" + mv["title"] + "<br>"
        		info += "影片介紹：<a href=" + mv["hyperlink"] + ">" + mv["hyperlink"] + "</a><br>"
        		info += "片長：" + mv["showLength"] + " 分鐘<br>" 
        		info += "上映日期：" + mv["showDate"] + "<br><br>"           
        return info
    else:  
        return render_template("input.html")

@app.route("/movie_rate")
def movie_rate():
    url = "http://www.atmovies.com.tw/movie/next/"
    Data = requests.get(url)
    Data.encoding = "utf-8"
    sp = BeautifulSoup(Data.text, "html.parser")
    result=sp.select(".filmListAllX li")
    lastUpdate = sp.find(class_="smaller09").text[5:]

    for x in result:
        picture = x.find("img").get("src").replace(" ", "")
        title = x.find("img").get("alt")    
        movie_id = x.find("div", class_="filmtitle").find("a").get("href").replace("/", "").replace("movie", "")
        hyperlink = "http://www.atmovies.com.tw" + x.find("a").get("href")

        t = x.find(class_="runtime").text
        showDate = t[5:15]

        showLength = ""
        if "片長" in t:
            t1 = t.find("片長")
            t2 = t.find("分")
            showLength = t[t1+3:t2]

        r = x.find(class_="runtime").find("img")
        rate = ""
        if r != None:
            rr = r.get("src").replace("/images/cer_", "").replace(".gif", "")
            if rr == "G":
                rate = "普遍級"
            elif rr == "P":
                rate = "保護級"
            elif rr == "F2":
                rate = "輔12級"
            elif rr == "F5":
                rate = "輔15級"
            else:
                rate = "限制級"

        doc = {
            "title": title,
            "picture": picture,
            "hyperlink": hyperlink,
            "showDate": showDate,
            "showLength": showLength,
            "rate": rate,
            "lastUpdate": lastUpdate
        }

        db = firestore.client()
        doc_ref = db.collection("電影含分級").document(movie_id)
        doc_ref.set(doc)
    return "近期上映電影已爬蟲及存檔完畢，網站最近更新日期為：" + lastUpdate


@app.route("/webhook", methods=["POST"])
def webhook():
    # build a request object
    req = request.get_json(force=True)
    # fetch queryResult from json
    action =  req.get("queryResult").get("action")
    msg =  req.get("queryResult").get("queryText")
    info = "動作：" + action + "； 查詢內容：" + msg
    return make_response(jsonify({"fulfillmentText": info}))





if __name__ == "__main__":
	app.run()