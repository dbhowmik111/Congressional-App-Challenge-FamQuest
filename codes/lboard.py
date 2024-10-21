from flask import Flask, redirect, url_for, render_template, request, session


def leaderboard_int(u_name, u_id, mysql):
    top_fam_table = lboard_winners(mysql)
    f_n1, f_n2, f_n3, f_n4, f_n5, r = which_family(mysql, u_id, top_fam_table)
    name5 = top_fam_table[4][0] 
    fam5 = f_n5
    print(name5, fam5)
    if int(r)>5: #if rank isn't 5
        print(r)
        name5 = top_fam_table[int(r)-1][0] #change name 5 to correct name
        fam5="family"
    return render_template('lboard.html', username = u_name,
                           n1 = top_fam_table[0][0], 
                           n2 = top_fam_table[1][0], 
                           n3 = top_fam_table[2][0], 
                           n4 = top_fam_table[3][0],
                           n5 = name5, 
                           s1 = top_fam_table[0][1], 
                           s2 = top_fam_table[1][1], 
                           s3 = top_fam_table[2][1],
                           s4 = top_fam_table[3][1],
                           s5 = top_fam_table[4][1],
                           f1 = f_n1,
                           f2 = f_n2,
                           f3 = f_n3,
                           f4 = f_n4, 
                           f5 = fam5,
                           r = r)

def lboardaction_int(mysql, u_name, u_id, fq_id):
    #get user result
    cursor = mysql.connection.cursor()
    sql1 = 'SELECT * FROM user_quiz_map WHERE fq_id = %s AND u_id = %s'
    val1 = (fq_id, u_id)
    cursor.execute(sql1, val1)
    user_rec = cursor.fetchone()
    result = user_rec[3]
    attempt = user_rec[2]
    art = get_art(mysql, u_id, fq_id)
    if attempt == 1:
        if result == 1:
            return render_template('misc.html', message = "CORRECT ANSWER +50 xp", message_2 = "BIG WIN! LOGIN TOMORROW FOR MORE EXCITING QUIZZES", article = art, username = u_name)
        else:
            return render_template('misc.html', message = "WRONG ANSWER +10 xp \n CORRECT ANSWER:", message_2 = "GREAT TRY! LOGIN TOMORROW FOR MORE EXCITING QUIZZES", article = art, username = u_name)
    else:
        return redirect(url_for("quiz"))


def get_art(mysql, u_id, fq_id):
    #get mem_num
    cursor = mysql.connection.cursor()
    sql2 = 'SELECT * FROM user WHERE mem_id = %s'
    val2 = (u_id, )
    cursor.execute(sql2, val2)
    user_rec = cursor.fetchone()
    n = user_rec[4]

    #get quiz and article number from fq_map
    cursor = mysql.connection.cursor()
    sql3 = 'SELECT * FROM fam_quiz_map WHERE fq_id = %s'
    val3 = (fq_id, )
    cursor.execute(sql3, val3)
    fq_rec = cursor.fetchone()
    quiz_id = fq_rec[3]
    art_num = int(fq_rec[3+n])

    cursor = mysql.connection.cursor()
    sql4 = 'SELECT * FROM quiz WHERE quiz_id = %s'
    val4 = (quiz_id, )
    cursor.execute(sql4, val4)
    quiz_rec = cursor.fetchone()
    art = quiz_rec[art_num]
    return art

def lboard_winners(mysql):
    #get total score of all families
    cursor = mysql.connection.cursor()
    sql4 = 'SELECT name, total_score FROM family ORDER BY total_score DESC'
    cursor.execute(sql4, )
    top_fam_table = cursor.fetchall()

    return top_fam_table

def which_family(mysql, u_id, top_fam_table):
    cursor = mysql.connection.cursor()

    #get fam id
    sql5 = 'SELECT * FROM user WHERE mem_id = %s'
    val5 = (u_id, )
    cursor.execute(sql5, val5)
    u_rec = cursor.fetchone()

    #get fam name
    sql6 = 'SELECT * FROM family WHERE id = %s'
    val6 = (u_rec[3], )
    cursor.execute(sql6, val6)
    fam_rec = cursor.fetchone()

    #return if family or not
    if top_fam_table[0][0] == fam_rec[1]:
        return "family", "nf", "nf", "nf", "nf", "5"
    elif top_fam_table[1][0] == fam_rec[1]:
        return "nf", "family", "nf", "nf", "nf", "5"
    elif top_fam_table[2][0] == fam_rec[1]:
        return "nf", "nf", "family", "nf", "nf", "5"
    elif top_fam_table[3][0] == fam_rec[1]:
        return "nf", "nf", "nf", "family", "nf", "5"
    elif top_fam_table[4][0] == fam_rec[1]:
        return "nf", "nf", "nf", "nf", "family", "5"
    else:
        rank= find_rank(mysql, fam_rec[1])
        print(rank, "1")
        return "nf", "nf", "nf", "nf", "nf", str(rank)

def find_rank(mysql, fam_name):
    
    cursor = mysql.connection.cursor()
    sql4 = 'SELECT name FROM family ORDER BY total_score DESC'
    cursor.execute(sql4, )
    count = cursor.rowcount
    top_fam_table = cursor.fetchall()

    for i in range(0, count):
        if top_fam_table[i][0] == fam_name:
            return i+1 #return rank (i+1)

    



    

    




