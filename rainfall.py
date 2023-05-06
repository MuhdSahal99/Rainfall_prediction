import smtplib
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import numpy as np
from flask import Flask,render_template,request,redirect,session
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

from DBConnection import Db
import random
app = Flask(__name__)
app.secret_key="abc"

@app.route('/',methods=['GET','POST'])
def login():
    if request.method=="POST":
        username=request.form['textfield']
        password=request.form['textfield2']
        db=Db()
        ss=db.selectOne("select * from login where username='"+username+"'and password='"+password+"'")
        if ss is not None:
            if ss['usertype']=='admin':
                session['lg']='lin'
                return redirect ('/admin_home')
            elif ss['usertype']=='expert':
                session['lg']='lin'

                session['lid']=ss['login_id']
                return redirect('/expert_home')
            elif ss['usertype']=='user':
                session['lg']='lin'

                session['lid']=ss['login_id']
                return redirect('/uhome')
            else:
                return '''<script>alert('user not found');window.location="/"</script>'''
        else:
            return '''<script>alert('user not found');window.location="/"</script>'''
    return render_template("login.html")

@app.route('/admin_home')
def admin_home():
    if session['lg']=='lin':
         return render_template("admin/admin_index.html")
    else:
        return redirect('/')

@app.route('/admin_index')
def admin_index():
    return render_template("admin/index.html")

@app.route('/expert_add',methods=['GET','POST'])
def expert_add():
    if session['lg']=="lin":
        if request.method=="POST":
            name=request.form['textfield']
            emailid=request.form['textfield2']
            qualification=request.form['textfield4']
            pas=random.randint(000,999)
            db=Db()
            s=db.insert("insert into login VALUES ('','"+emailid+"','"+str(pas)+"','expert')")
            db.insert("insert into expert values ('"+str(s)+"','"+name+"','"+emailid+"','"+qualification+"')")
            return 'ok'
        else:
            return render_template("admin/expert_add.html")
    else:
        return redirect('/')

@app.route('/expert_edit/<e>',methods=['GET','POST'])
def expert_edit(e):
    if session['lg'] == "lin":
        if request.method == "POST":
            name = request.form['textfield']
            qualification = request.form['select']
            db=Db()
            db.update("update expert set name='" + name + "',qualification='" + qualification + "' where expert_id='"+e+"'")
            return 'ok'
        else:
            db=Db()
            res=db.selectOne("select * from expert where expert_id='"+e+"'")
        return render_template("admin/expert_edit.html",data=res)
    else:
        return redirect('/')

@app.route('/expert_delete/<d>')
def expert_delete(d):
    if session['lg'] == "lin":
        db=Db()
        db.delete("delete from expert where expert_id='"+d+"'")
        return redirect('/expert_view')
    else:
        return redirect('/')



@app.route('/expert_view')
def expert_view():
    if session['lg'] == "lin":
        db=Db()
        ss=db.select("select * from expert")
        return render_template("admin/expert_view.html",data=ss)
    else:
        return redirect('/')

@app.route('/view_feedback')
def view_feedback():
    if session['lg'] == "lin":
        db=Db()
        ss=db.select("select * from feedback")
        return render_template("admin/view_feedback.html",data=ss)
    else:
        return redirect('/')

@app.route('/view_notificatn')
def view_notificatn():
    if session['lg'] == "lin":
        db = Db()
        ss = db.select("select * from notification")
        return render_template("admin/view_notificatn.html",data=ss)
    else:
        return redirect('/')

@app.route('/view_user')
def view_user():
    if session['lg'] == "lin":
        db = Db()
        ss = db.select("select * from user")
        return render_template("admin/view_user.html",data=ss)
    else:
        return redirect('/')

@app.route('/add_notificatn',methods=['GET','POST'])
def add_notificatn():
    if session['lg'] == "lin":
        if request.method == "POST":
            expertname = request.form['textfield']
            date = request.form['textfield2']
            notification = request.form['textarea']
            db = Db()
            n = db.insert("insert into notification values ('','','" + date + "','" + notification + "') ")
            return "ok"
        else:
            return render_template("expert/add_notificatn.html")
    else:
        return redirect('/')

@app.route('/dataset',methods=['GET','POST'])
def dataset():
    if request.method == "POST":
        mintemp= request.form['textfield']
        maxtemp = request.form['textfield2']
        windspeed9am = request.form['textfield3']
        windspeed3pm = request.form['textfield4']
        humidity9am = request.form['textfield5']
        humidity3pm = request.form['textfield6']
        temp9am = request.form['textfield7']
        temp3pm = request.form['textfield8']
        raintoday = request.form['textfield9']
        raintoday=raintoday.lower()
        if raintoday=="yes":
            raintoday="1"
        else:
            raintoday="0"
        ar=[]
        ar.append(mintemp)
        ar.append(maxtemp)
        ar.append(windspeed9am)
        ar.append(windspeed3pm)
        ar.append(humidity9am)
        ar.append(humidity3pm)
        ar.append(temp9am)
        ar.append(temp3pm)
        ar.append(raintoday)
        arr=np.array([ar])

        import pandas as pd
        data=pd.read_csv(r"C:\Users\HP\Downloads\rainfall\static\dataset.csv")
        attributes=data.values[1:3001, :9]              #       X
        label=data.values[1:3001, 9]                    #       Y
        print(attributes)
        print(label)

        X_train, X_test, Y_train, Y_test = train_test_split(attributes, label, test_size=0.2)
        model=RandomForestClassifier()
        model.fit(attributes, label)
        pred=model.predict(arr)
        pred=list(pred)
        print("Prediction ", pred[0])
        if pred[0] == 0.0:
            stat="No rain tomorrow"
        else:
            stat="It will rain tomorrow"

        model.fit(X_train, Y_train)
        y_pred=model.predict(X_test)
        acc=accuracy_score(Y_test, y_pred)
        acc=round(acc*100, 2)

        # import numpy as  np
        # val=list(pred)

        db=Db()
        ss = db.selectOne("select * from prediction WHERE date= curdate()")
        if ss is None:
            db=Db()
            db.insert("insert into prediction(date, prediction) values(curdate(), '"+stat+"')")
        else:
            db=Db()
            db.update("update prediction set prediction='"+stat+"' where date=curdate()")
        return render_template("expert/dataset.html", data=stat, acc=acc)

    return render_template("expert/dataset.html")


@app.route('/expert_home')
def expert_home():
    if session['lg'] == 'lin':
        return render_template("expert/expert_index.html")
    else:
        return redirect('/')

@app.route('/expert_index')
def expert_index():
    if session['lg'] == "lin":
        return render_template("expert/expert_index.html")
    else:
        return redirect('/')


@app.route('/send_reply/<a>',methods=['GET','POST'])
def send_reply(a):
    if session['lg'] == "lin":
        if request.method == "POST":
            reply = request.form['textarea']
            db = Db()
            r = db.update("update doubt set reply='"+reply+"',expert_id='"+str(session['lid'])+"', reply_date=curdate() where doubt_id='"+str(a)+"' ")
            return "ok"
        else:
            return render_template("expert/send_reply.html")
    else:
        return redirect('/')

@app.route('/view_doubts')
def view_doubts():
    if session['lg'] == "lin":
        db = Db()
        ss = db.select("select * from doubt,user where user.user_id=doubt.user_id and reply='pending'")
        return render_template("expert/view_doubts.html",data=ss)
    else:
        return redirect('/')


@app.route('/expert_view_notificatn')
def expert_view_notificatn():
    if session['lg'] == "lin":
        db = Db()
        ss = db.select("select * from notification,expert where notification.expert_id=expert.expert_id")
        return render_template("expert/view_notificatn.html",data=ss)
    else:
        return redirect('/')

@app.route('/notification_delete/<d>')
def notification_delete(d):
    if session['lg'] == "lin":
        db=Db()
        db.delete("delete from notification where notification_id='"+d+"'")
        return redirect('/expert_view_notificatn')
    else:
        return redirect('/')

@app.route('/ask_doubt',methods=['get','post'])
def ask_doubt():
    if session['lg'] == "lin":
        if request.method == "POST":
            doubt = request.form['textarea']
            db=Db()
            qry="insert into doubt(doubt, doubt_date, reply, user_id) values('"+doubt+"', curdate(), 'pending', '"+str(session['lid'])+"')"
            db.update(qry)
            # aa=db.update("update doubt set doubt='"+doubt+"',doubt_date=curdate() where user_id='"+str(session['lid'])+"'")
            return "ok"
        else:
            return render_template("user/ask_doubt.html")
    else:
        return redirect('/')


@app.route('/user_index')
def user_index():
    if session['lg'] == "lin":
        return render_template("user/user_index.html")
    else:
        return redirect('/')



@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == "POST":
        name = request.form['textfield']
        area = request.form['textfield2']
        city = request.form['textfield3']
        post = request.form['textfield4']
        district = request.form['select2']
        state = request.form['select']
        email = request.form['textfield5']
        phoneno = request.form['textfield6']
        password = request.form['textfield7']
        db=Db()
        qry=db.insert("insert into login VALUES ('','"+email+"','"+password+"','user')")
        db.insert("insert into user values('"+str(qry)+"','"+name+"','"+area+"','"+city+"','"+post+"','"+district+"','"+state+"','"+email+"','"+phoneno+"')")
        return '''<script>alert('registered');window.location="/"</script>'''
    else:
        return render_template("user/register.html")



@app.route('/send_feedback',methods=['GET','POST'])
def send_feedback():
    if session['lg'] == "lin":
        if request.method == "POST":
            name = request.form['textarea']
            db=Db()
            db.insert("insert into feedback values('',curdate(),'"+name+"','"+str(session['lid'])+"')")
            return '''<script>alert('done');window.location="/uhome"</script>'''
        else:
            return render_template("user/send_feed.html")
    return redirect('/')

@app.route('/u_view_notificatn')
def u_view_notificatn():
    if session['lg'] == "lin":
        db = Db()
        ss = db.select("select * from notification")
        return render_template("user/view_notification.html",data=ss)
    else:
        return redirect('/')

@app.route('/view_reply')
def view_reply():
    if session['lg'] == "lin":
        db = Db()
        ss = db.select("select * from doubt,expert where doubt.expert_id=expert.expert_id and doubt.user_id='"+str(session['lid'])+"'")
        return render_template("user/view_reply.html",data=ss)
    else:
        return redirect('/')

@app.route('/view_result')
def view_result():
    if session['lg'] == "lin":
        db = Db()
        ss = db.select("select * from prediction order by date desc")
        return render_template("user/view_result.html",data=ss)
    else:
        return redirect('/')



@app.route('/uhome')
def uhome():
    if session['lg'] == 'lin':
        return render_template("user/user_index.html")
    else:
        return redirect('/')

@app.route('/logout')
def logout():
    session.clear()
    session['lg']=""
    return redirect('/')


@app.route('/forgot_password',methods=['get','post'])
def forgot_password():
    if request.method == "POST":
        email = request.form['textfield']
        db = Db()
        ss = db.selectOne("select * from login WHERE username='"+email+"'")
        print(ss['password'])
        pwd=ss['password']

        user="rainfallprediction25@gmail.com"
        password="tjmmzsskuwnbunra"
        subject="Password for RAINFALL PREDICTION SITE"
        content="Your password for RAINFALL PREDICTION WEBSITE is :"+str(pwd)
        host="smtp.gmail.com"
        port=465
        message=MIMEMultipart()
        message['From']=Header(user)
        message['To']=Header(email)
        message['Subject']=Header(subject)
        message.attach(MIMEText(content, 'plain', 'utf-8'))
        server=smtplib.SMTP_SSL(host, port)
        server.login(user, password)
        server.sendmail(user, email, message.as_string())
        server.quit()
        return redirect("/")
    return render_template("forgot_password.html")


if __name__=="__main__":
    app.run(port=4000)