from flask import Flask,render_template,request,redirect,jsonify
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker 
from sqlalchemy.sql import text
import logging
import json
import random,string

app = Flask(__name__)
engine = create_engine('mysql+mysqlconnector://yuri:test@localhost/educ_yuri')
session = sessionmaker(bind=engine)()

def randomname(n):
   randlst = [random.choice(string.ascii_letters + string.digits) for i in range(n)]
   return ''.join(randlst)

@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/form', methods=['POST'])
def post():
    html_name = request.form['form_name']
    html_pass = request.form['form_pass']
    token = randomname(10)
    t = text("SELECT * from  users WHERE name = '" + html_name + "'")
    results = session.execute(t)
    for result in results: 
        true_password = result.password
    if(true_password == html_pass):
        t = text("UPDATE users SET token = '" + token + "' WHERE name = '" + html_name + "' AND password = '"+ html_pass +"';")
        result = session.execute(t)
        session.commit()
        redirect_url = "/home?token=" + token
        # redirect_url = "/"+html_name+"?token="+token
        return redirect(redirect_url)
    else:
        return "login failed"

@app.route('/home')
def hello():
    req = request.args
    token = req.get("token")
    t = text("SELECT * from  users WHERE token = '" + token + "'")
    results = session.execute(t)
    for result in results: 
        name = result.name
        grade = result.grade 
    return render_template('hello.html', title='呼び出し側でタイトル設定', name=name, grade=grade)

@app.route('/after-line-login')
def form():
    req = request.args
    token = req.get("token")
    t = f"select * from users where token='{token}';"
    results = session.execute(t)
    name = results.name
    grade = results.grade
    # select * from user where 
    # name と gradeを取得
    return render_template('after-line-login.html', name=name, grade=grade)

@app.route('/send-message-form', methods=['post'])
def send_message():
        message = request.form['message']
        token = request.form['token']
		# tokenからline_tokenを取得(SELECT)
        # t = f"select * from users where token='{token}';"
        # results = session.execute(t)
        # for result in results: 
        #     line_token = result.line_token
        line_token="0mYfKNOzzipCxCxWl6h8AakuscN5jAxCW1oi56Vj8UO"
        headers = {
			"Content-Type":"application/x-www-form-urlencoded",
			"Authorization":"Bearer "+line_token
		}
        data = {"message":message}
        url = "https://notify-api.line.me/api/notify"
        response = requests.post(url,headers = headers,data= data)
        return render_template('after-line-send.html')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8080)
