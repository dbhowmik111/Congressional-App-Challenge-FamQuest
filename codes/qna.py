from flask import session, render_template, request, app, Flask
import random
from PIL import Image 
import base64
import io


def get_quiz_assigned_today(u_id, mysql): #get quiz that was assigned today
    fam_id = get_famid(u_id, mysql)
    fq_rec = get_fq_rec(fam_id, mysql)
    
    if fq_rec == None:
        return -1, None, None, None
    else:
        artstr = fq_rec[4], fq_rec[5], fq_rec[6], fq_rec[7]
        artlist = list(artstr)
        qstr = fq_rec[8], fq_rec[9], fq_rec[10], fq_rec[11]
        qlist = list(qstr)
        return fq_rec[3], artlist, qlist, fq_rec #returns quiz_id, article list, question list
    
def assign_quiz_today(mysql, u_id, u_name): #make new fq_id
    cursor = mysql.connection.cursor()

    #make random article and question list
    list1 = [1,2,3,4]
    rand_list1 = random_generator(list1, 0)
    print("A randlist1", rand_list1)
    list2 = rand_list1.copy()
    print("B randlist1", rand_list1)
    rand_list2 = random_generator(list2, 1)
    print("C randlist1", rand_list1)

    print("C randlist2", rand_list2)

    fam_id = get_famid(u_id, mysql)
    quiz_id = get_unique_quiz(mysql, fam_id)
 
    #insert new fq row
    sql6 = "INSERT INTO fam_quiz_map (date, fam_id, quiz_id, mem1_art, mem2_art, mem3_art, mem4_art, mem1_ques, mem2_ques, mem3_ques, mem4_ques, today_score, red) VALUES (CAST(curdate() AS DATE), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    val6 = (fam_id, quiz_id, rand_list1[0], rand_list1[1], rand_list1[2], rand_list1[3], rand_list2[0], rand_list2[1], rand_list2[2], rand_list2[3], 0, 0)
    cursor.execute(sql6, val6) 
    mysql.connection.commit()

    fq_rec=get_fq_rec(fam_id, mysql)
    insert_user_quiz_map(mysql, u_id, fq_rec[0]) #insert new user_quiz_map row
    #return quiz_id, rand_list1, rand_list2
    return show_quiz(u_id, u_name, mysql, quiz_id)

def show_quiz(u_id, u_name, mysql, quiz_id):
    #get quiz info
    cursor = mysql.connection.cursor()
    sql5 = 'SELECT * FROM quiz WHERE quiz_id = %s'
    val5 = (quiz_id, )
    cursor.execute(sql5, val5)
    quiz_rec = cursor.fetchone()
    title = quiz_rec[9]
    filename= quiz_rec[10]

    article, q_id = assign_artques_user(mysql, u_id, quiz_rec) #get article and quiz_id for user
    print(article, "1")

    #get question statement, opt1, opt2, opt3, opt4
    sql6 = 'SELECT * FROM question WHERE q_id = %s'
    val6 = (q_id, )
    cursor.execute(sql6, val6)
    ques_rec = cursor.fetchone()
    q_statement = ques_rec[1]
    option1 = ques_rec[2]
    option2 = ques_rec[3]
    option3 = ques_rec[4]
    option4 = ques_rec[5]
    session['q_id'] = q_id
    session['article'] = article

    #get unique color for members
    color = get_mem_col(mysql,u_id)

    #get image
    filename1=filename+".png"

    app=Flask(__name__)
    app.config["IMAGE UPLOADS"]="/Users/sushr/OneDrive/Desktop/codes/FLASK/static/images"
    img=Image.open(app.config["IMAGE UPLOADS"]+"/"+filename1)
    data=io.BytesIO()
    img.save(data,"PNG")

    encode_img_data=base64.b64encode(data.getvalue())
    
    return render_template('quiz.html', question=q_statement, opt1=option1, opt2=option2, opt3=option3, opt4=option4, art=article, title= title, username = u_name, filename1=encode_img_data.decode("UTF-8"), filename = filename, color = color)

def get_real_ans(mysql, fq_id, user_answer): #gets real answer and returns check_answer
   cursor = mysql.connection.cursor()
   if 'q_id' in session:
    q_id = session['q_id']

    #get real answer
    sql3 = 'SELECT * FROM question WHERE q_id = %s' 
    val3 = (q_id, )
    cursor.execute(sql3, val3)
    ques_rec = cursor.fetchone()
    print(ques_rec, "\n")
    real_answer=ques_rec[6]

    return check_answer(user_answer, real_answer, mysql, fq_id)

from fam_score import fam_score_today, total_fam_score
def check_answer(u_ans, ans, mysql, fq_id): #checks answer using user answer and real answer
    u_name = session['username']
    u_id = session['u_id']
    if 'article' in session:
        art = session['article']
        print(art, "2")
    u_ans=int(u_ans)
    fam_id = get_famid(u_id, mysql)

    if u_ans == ans: #correct answer
        cursor = mysql.connection.cursor()
        sql1 = "UPDATE user_quiz_map SET result = 1 WHERE u_id = %s AND fq_id = %s"
        val1 = (u_id, fq_id)
        cursor.execute(sql1, val1)
        mysql.connection.commit()
        fam_score_today(mysql, fq_id, 50)
        total_fam_score(mysql, fam_id, fq_id, 50)
        return render_template('misc.html', message = "CORRECT ANSWER +50 xp", message_2 = "BIG WIN! LOGIN TOMORROW FOR MORE EXCITING QUIZZES", article = art, username = u_name)
        
    else:
        cursor=mysql.connection.cursor()
        sql2 = "UPDATE user_quiz_map SET result = 0 WHERE u_id = %s AND fq_id = %s"
        val2 = (u_id, fq_id)
        cursor.execute(sql2, val2)
        mysql.connection.commit()
        fam_score_today(mysql, fq_id, 10)
        total_fam_score(mysql, fam_id, fq_id, 10)
        return render_template('misc.html', message = "WRONG ANSWER +10 xp", message_2 = "GREAT TRY! LOGIN TOMORROW FOR MORE EXCITING QUIZZES", article = art, username = u_name)


def get_famid(u_id, mysql): #returns family id from user id
    cursor = mysql.connection.cursor()
    sql1 = 'SELECT * FROM user WHERE mem_id = %s'
    val1 = (u_id, )
    cursor.execute(sql1, val1)
    fam_rec = cursor.fetchone()
    return fam_rec[3] 

def get_fq_rec(fam_id, mysql): #returns fq_id
    cursor = mysql.connection.cursor()

    sql2 = 'SELECT * FROM fam_quiz_map WHERE CAST(date AS DATE) = CAST(curdate() AS DATE) AND fam_id = %s'
    val2 = (fam_id, )
    cursor.execute(sql2, val2)

    if cursor.rowcount == 0:
        return None #fq id not found, family don't have quiz assigned
    else:
        fq_rec = cursor.fetchone()
        return fq_rec
    

def random_generator(rand_list, shift): #returns random list(1 to 4)
    for i in range(3):
        num = random.randint(i + shift, 3)
        rand_list[i], rand_list[num] = rand_list[num], rand_list[i]
    return rand_list

def get_unique_quiz(mysql, fam_id):
    cursor = mysql.connection.cursor()

    sql3 = 'SELECT quiz_id FROM quiz'
    cursor.execute(sql3)
    quiz_tab = cursor.fetchall() #ex: [[1], [2], [3], [4], [5]]
    n = cursor.rowcount #ex: n=5
    i=0

    while True:
        i+=1
        row = random.randint(0, n-1) #ex:(0,4) row = 4
        quiz_list = quiz_tab[row] #ex: quiz_list = [[5]]
        quiz_id = quiz_list[0] #create new quiz id, ex: quiz_id = 5
        
        #find if family has used quiz before
        sql4 = 'SELECT * FROM fam_quiz_map WHERE fam_id = %s AND quiz_id = %s'
        val4 = (fam_id, quiz_id)
        cursor.execute(sql4, val4)
        if cursor.rowcount == 0 or i > 3:
            break

    return quiz_id

def assign_artques_user(mysql, u_id, quiz_rec):

    fam_id = get_famid(u_id, mysql)
    fq_rec = get_fq_rec(fam_id, mysql)

    #get family info
    cursor = mysql.connection.cursor()
    sql5 = 'SELECT * FROM family WHERE id = %s'
    val5 = (fam_id, )
    cursor.execute(sql5, val5)
    fam_rec = cursor.fetchone()

     #returns article, question id
    if u_id == fam_rec[2]: #mem1
        return quiz_rec[fq_rec[4]], quiz_rec[fq_rec[8]+4]
    if u_id == fam_rec[3]: #mem2
        return quiz_rec[fq_rec[5]], quiz_rec[fq_rec[9]+4]
    if u_id == fam_rec[4]: #mem3
        return quiz_rec[fq_rec[6]], quiz_rec[fq_rec[10]+4]
    if u_id == fam_rec[5]: #mem4
        return quiz_rec[fq_rec[7]], quiz_rec[fq_rec[11]+4]
    
def insert_user_quiz_map(mysql, u_id, fq_id):
    sql8 = "INSERT INTO user_quiz_map (u_id, fq_id, attempt, result) VALUES (%s, %s, %s, %s)"
    val8 = (u_id, fq_id, 0, 0 )
    cursor = mysql.connection.cursor()
    cursor.execute(sql8, val8)
    mysql.connection.commit()

def get_mem_col(mysql, u_id):

    cursor = mysql.connection.cursor()
    sql1 = 'SELECT * FROM user WHERE mem_id = %s'
    val1 = (u_id, )
    cursor.execute(sql1, val1)
    user_rec = cursor.fetchone()
    mem_num = str(user_rec[4])

    if mem_num == "1":
        color = "rgb(98, 161, 238)"
    elif mem_num == "2":
        color = "rgb(245, 140, 4)"
    elif mem_num == "3":
        color = "rgb(235, 146, 203)"
    elif mem_num =="4":
        color = "rgb(154, 205, 71)"
    
    return color



    

    


