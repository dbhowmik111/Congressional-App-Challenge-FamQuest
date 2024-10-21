from flask import render_template, redirect, url_for, session

def login_int(s):
    return render_template('login.html', message = s)

def login_action_int(u, mysql):
    cursor=mysql.connection.cursor()
    sql1 = 'SELECT * FROM user WHERE mem_name = %s'
    val1 = (u, )
    cursor.execute(sql1, val1)
    userdet = cursor.fetchone()
    if cursor.rowcount == 0:
        return login_int("Username does not exist")
    else:
        sql2 = 'SELECT * FROM family WHERE id = %s'
        val2 = (userdet[3], )
        cursor.execute(sql2, val2)
        fam_det = cursor.fetchone()
        if int(fam_det[6]) != 4:
            return render_template('wait.html', message = "CURRENT MEMBERS SIGNED UP: " + str(fam_det[6]), message_2 = " WAITING FOR "+str(4-fam_det[6])+" MORE MEMBERS TO SIGN UP")
        session['u_id'] = userdet[0]
        session['username'] = u
        return redirect(url_for("quiz"))

