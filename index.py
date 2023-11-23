import firebase_admin
from firebase_admin import credentials, firestore
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)


from flask import Flask,render_template, request
from datetime import datetime
app = Flask(__name__)

@app.route("/")
def index():
	X = "作者:陳羿汶!2023-11-23a<br>"
	X += "<a href=/mis>資訊導論</a><br>"
	X += "<a href=/today>日期時間</a><br>"
	X += "<a href=/about>羿汶的網頁</a><br>"
	X += "<a href=/welcome?guest=Wanda>歡迎Wanda~ ~</a><br>"
	X += "<a href=/account>使用表單方式傳值</a><br><br>"
	X += "<a href=/wave>人選之人演員名單(按年齡由小到大)</a><br><br>"
	X += "<a href=/books>全部圖書</a><br>"
	X += "<a href=/search>根據書名關鍵字查詢圖書</a><br>"
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

if __name__ == "__main__":
	app.run()