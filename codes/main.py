from flask import Flask, redirect, url_for, render_template, request, session

from flask_mysqldb import MySQL
#import MySQLdb.cursors

app = Flask(__name__)
app.secret_key = 'your secret key'
app.app_context()
 
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'abc123'
app.config['MYSQL_DB'] = 'database_1'
app.config['MYSQL_PORT'] = 3306
mysql = MySQL(app)

from qna import check_answer, get_quiz_assigned_today, assign_quiz_today, show_quiz, insert_user_quiz_map, assign_artques_user
from fam_score import check_fam_finish, bonus_score

@app.route("/quiz")
def quiz():
    if 'username' in session:
        u_id = session['u_id']
        u_name = session['username']
    else:
        return redirect(url_for("login"))
    
    qzid, artlist, qlist, fq_rec = get_quiz_assigned_today(u_id, mysql)

    if qzid == -1: #no fq_id found, quiz not assigned for today
        return assign_quiz_today(mysql, u_id, u_name)

    attempt = 0
    #check if user_quiz_map exists
    cursor = mysql.connection.cursor()
    sql2= 'SELECT * FROM user_quiz_map WHERE u_id = %s AND fq_id = %s'
    val2 = (u_id, fq_rec[0])
    cursor.execute(sql2, val2)

    #if not, then insert
    if cursor.rowcount == 0:
        insert_user_quiz_map(mysql, u_id, fq_rec[0]) 
    else: #if exists, check if user attempted or not
        uq_rec = cursor.fetchone()
        attempt =  int(uq_rec[2])
                
    if attempt == 1: #if attempt 1, show leaderboard; otherwise, show
        cursor = mysql.connection.cursor()
        sql5 = 'SELECT * FROM quiz WHERE quiz_id = %s'
        val5 = (qzid, )
        cursor.execute(sql5, val5)
        quiz_rec = cursor.fetchone()

        art, q_id = assign_artques_user(mysql, u_id, quiz_rec)
        print(art, "1")
        return redirect(url_for("leaderboard"))
    return show_quiz(u_id, u_name, mysql, qzid) #not attempted, show quiz
        
from qna import get_famid, get_fq_rec, get_real_ans
@app.route("/submitanswer", methods = ['POST'])
def submitanswer():
    if 'username' in session:
        u_id = session['u_id']
        u_name = session['username']
    else:
        return redirect(url_for("login"))
    
    fam_id = get_famid(u_id, mysql)
    fq_rec = get_fq_rec(fam_id, mysql)
    q_id = fq_rec[3] #get quiz id
    fq_id = fq_rec[0] #get fq id
    user_answer = request.form.get("answer")

    cursor=mysql.connection.cursor() #update user_quiz_map and set attempt as 1
    sql1 = "UPDATE user_quiz_map SET attempt = 1 WHERE u_id = %s AND fq_id = %s"
    val1 = (u_id, fq_id)
    cursor.execute(sql1, val1)
    mysql.connection.commit()

    return get_real_ans(mysql, fq_id, user_answer)

from family import familyreg_int
@app.route("/familyreg")
def familyreg():
    return familyreg_int("")

from family import family
@app.route("/familyregaction", methods = ['POST'])
def familyregaction():
    fam_name = request.form.get("family name")
    print(fam_name)
    return family(fam_name, mysql)

from user import userreg_int
@app.route("/userreg")
def userreg():
    return userreg_int("")

from user import user
@app.route("/userregaction", methods = ['POST'])
def userregaction():
    username = request.form.get("username")
    code = request.form.get("code")
    fam_name = request.form.get("famname")
    return user(username, code, fam_name, mysql)

from login import login_int
@app.route("/")
@app.route("/login")
def login():
    if 'username' in session:
        return redirect(url_for("quiz"))
    return login_int("")

from login import login_action_int
@app.route("/loginaction", methods = ['POST'])
def loginaction():
    user_name = request.form.get("user_name")
    return login_action_int(user_name, mysql)


from lboard import leaderboard_int
@app.route("/leaderboard", methods = ['GET'])
def leaderboard():
    if 'username' in session:
        u_id = session['u_id']
        u_name = session['username']
    else:
        return redirect(url_for("login"))
    
    fam_id = get_famid(u_id, mysql)
    return leaderboard_int(u_name, u_id, mysql)

from qna import get_famid, get_fq_rec
from lboard import lboardaction_int
@app.route("/lboardaction", methods =['GET'])
def lboardaction():
    if 'username' in session:
        u_id = session['u_id']
        u_name = session['username']
    else:
        return redirect(url_for("login"))
    fam_id = get_famid(u_id, mysql)
    fq_rec = get_fq_rec(fam_id, mysql)
    return lboardaction_int(mysql, u_name, u_id, fq_rec[0])

from logout import logout_int
@app.route("/logout")
def logout():
    return logout_int()

if __name__ == "__main__":
    app.run()