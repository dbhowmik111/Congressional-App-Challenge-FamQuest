from flask import render_template, redirect, url_for

def userreg_int(s):
    return render_template('signup.html', message = s)

def user(u, c, f, mysql):
    print(u, c, f)
    cursor=mysql.connection.cursor()

    #check if family name exists
    sql1 = 'SELECT * FROM family WHERE name = %s'
    val1 = (f, )
    cursor.execute(sql1, val1)
    if cursor.rowcount == 0:
            return userreg_int("Family account does not exist")
    else:
        sql1 = 'SELECT * FROM family WHERE name = %s'
        val1 = (f, )
        cursor.execute(sql1, val1)
        #checks if code entered matches family name
        fam_det=cursor.fetchone()
        if int(fam_det[0]) != int(c):
            return userreg_int("Family code does not match family name. Check again.")

    
    #checks if username already exists
    sql2 = 'SELECT * FROM user WHERE mem_name = %s'
    val2 = (u, )
    cursor.execute(sql2, val2)
    if cursor.rowcount > 0:
        return userreg_int("Username already exists. Please choose a different name.")
    
    #checks if family is full
    nmems = int(fam_det[6])
    x, y = target_mems(nmems)
    print(x)
    if x == "full" or x == "error":
        return userreg_int("4 members already in family. Space full.")
    sql3 = "INSERT INTO user (mem_name, fam_id, mem_num) VALUES (%s, %s, %s)"
    val3 = (u, c, y)
    cursor.execute(sql3, val3)
    mysql.connection.commit()
                
    sql4 = 'SELECT * FROM user WHERE mem_name = %s'
    val4 = (u, )
    cursor.execute(sql4, val4)
    userdet = cursor.fetchone()
    print(userdet)
    print(userdet[0])

    
    sql5 = "UPDATE family SET " + x + " = %s, num_mems = %s WHERE id = %s"
    val5 = (userdet[0], nmems+1, c)
    cursor.execute(sql5, val5)
    mysql.connection.commit()
    return redirect(url_for("login"))

    

def target_mems(nm):
    if nm == 0:
        return "mem_1", 1
    
    if nm == 1:
        return "mem_2", 2
    
    if nm == 2:
        return "mem_3", 3
    
    if nm == 3:
        return "mem_4", 4
    
    if nm == 4:
        return "full", 0
    
    if nm > 4:
        return "error", 0