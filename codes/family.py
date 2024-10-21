from flask import render_template, redirect, url_for

def familyreg_int(s):
    return render_template('family.html', message = s)

def family(name, mysql):
    cursor=mysql.connection.cursor()
    sql1 = 'SELECT * FROM family WHERE name = %s'
    val1 = (name, )
    cursor.execute(sql1, val1)

    if cursor.rowcount>0:
        return familyreg_int("Family name already exists. Please choose a different name.")
    else:
        sql2 = "INSERT INTO family (name, mem_1, mem_2, mem_3, mem_4, num_mems, total_score) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        val2 = (name, '0', '0', '0', '0', '0', '0')
        cursor.execute(sql2, val2)
        mysql.connection.commit()

        sql3 = 'SELECT * FROM family WHERE name = %s'
        val3 = (name, )
        cursor.execute(sql3, val3)
        fam_det= cursor.fetchone()
        print("\n\nfam_id:",fam_det[0],"\n\n")
        return render_template('code.html', code = str(fam_det[0]))
