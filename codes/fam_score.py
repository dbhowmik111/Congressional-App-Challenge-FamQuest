
def fam_score_today(mysql, fq_id, add_score): 
    cursor = mysql.connection.cursor()
    #gets todays score
    sql1 = 'SELECT today_score FROM fam_quiz_map WHERE fq_id = %s'
    val1 = (fq_id, )
    cursor.execute(sql1, val1)
    tod_score = cursor.fetchone()

    #update today's fam score
    new_score = int(tod_score[0]) + add_score
    sql2 = "UPDATE fam_quiz_map SET today_score = %s WHERE fq_id = %s"
    val2 = (new_score, fq_id)
    cursor.execute(sql2, val2)
    mysql.connection.commit()

def total_fam_score(mysql, fam_id, fq_id, add_score):
    cursor = mysql.connection.cursor()

    sql1 = 'SELECT red FROM fam_quiz_map WHERE fq_id = %s'
    val1 = (fq_id, )
    cursor.execute(sql1, val1)
    red = cursor.fetchone()
    #if past fam score not reduced, then reduce
    if red[0] == 0:
        red_prev_scores(mysql, fam_id)

    #get total fam score
    sql2 = 'SELECT total_score FROM family WHERE id = %s'
    val2 = (fam_id, )
    cursor.execute(sql2, val2)
    tot_score = cursor.fetchone()

    #update total fam score
    real_score = tot_score[0] + add_score
    print(real_score)
    sql3 = "UPDATE family set total_score = %s WHERE id = %s" 
    val3 = (real_score, fam_id)
    cursor.execute(sql3, val3)
    mysql.connection.commit()

    fam_done = check_fam_finish(mysql, fq_id)
    if fam_done == 1: #if fam is done, add bonus
        bonus_score(mysql, fq_id, fam_id)

def bonus_score(mysql, fq_id, fam_id):
    cursor = mysql.connection.cursor()

    #get today's score
    sql1 = 'SELECT today_score FROM fam_quiz_map WHERE fq_id = %s'
    val1 = (fq_id, )
    cursor.execute(sql1, val1)
    tod_score = cursor.fetchone()

    #get total score
    sql2 = 'SELECT total_score FROM family WHERE id = %s'
    val2 = (fam_id, )
    cursor.execute(sql2, val2)
    tot_score = cursor.fetchone()

    #get results
    sql1 = 'SELECT result FROM user_quiz_map WHERE fq_id = %s'
    val1 = (fq_id, )
    cursor.execute(sql1, val1)
    results = cursor.fetchall()
    count = cursor.rowcount

    x=1
    for i in range(0,count):
        #some member(s) has wrong answer
        r = results[i]
        if r[0] !=1: 
            x=0
            break

    if x == 1: #everyone has right answer
        bonus_today_score= int(tod_score[0])+50
        bonus_total_score = int(tot_score[0])+50
    else:
        bonus_today_score = int(tod_score[0])+20
        bonus_total_score = int(tot_score[0])+20

    #update today's score with bonus
    sql3 = "UPDATE fam_quiz_map SET today_score = %s WHERE fq_id = %s"
    val3 = (bonus_today_score, fq_id)
    cursor.execute(sql3, val3)
    mysql.connection.commit()

    #update total score with bonus
    sql3 = "UPDATE family SET total_score = %s WHERE id = %s"
    val3 = (bonus_total_score, fam_id)
    cursor.execute(sql3, val3)
    mysql.connection.commit()

def red_prev_scores(mysql, fam_id):
    cursor = mysql.connection.cursor()
    print("\nfam id:", fam_id)
    #get past scores of all members
    sql1 = 'SELECT total_score FROM family WHERE id = %s'
    val1 = (fam_id, )
    cursor.execute(sql1, val1)
    total_score = cursor.fetchone()

    #turn into 90%
    new_score = total_score[0]*0.90 #change to 98
    print(new_score)

    sql2 = "UPDATE family SET total_score = %s WHERE id = %s"
    val2 = (new_score, fam_id)
    cursor.execute(sql2, val2)
    mysql.connection.commit()

    sql3 = "UPDATE fam_quiz_map set red = %s" 
    val3 = ('1', )
    cursor.execute(sql3, val3)
    mysql.connection.commit()

def check_fam_finish(mysql, fq_id):
    cursor = mysql.connection.cursor()

    #check if everyone in fam has attempted
    sql1 = 'SELECT attempt FROM user_quiz_map WHERE fq_id = %s'
    val1 = (fq_id, )
    cursor.execute(sql1, val1)
    count = cursor.rowcount
    print("\n", count,"\n")

    if count < 4: #not everyone opened
        return 0
    
    attempts = cursor.fetchall()
    x = 1
    for i in range(0, count):
        attempt_list = attempts[i]
        if attempt_list[0] != 1:
            x = 0 #not everyone attempted
            break
    return x




#def update_uscore(mysql, fam_id, u_id, fq_id, t_f):
    #find which mem
   # mem_num = find_mem_num(mysql, fam_id, u_id) 
    #x = "10" #wrong answer default
 #   if t_f == "t": #right answer
  #      x = "50"
#
 #   #find past scores
  #  sql1 = 'SELECT %s FROM fam_score WHERE fam_id = %s'
   # val1 = (mem_num, fam_id)
   # cursor = mysql.connection.cursor()
   # cursor.execute(sql1, val1)
   # mem_score = cursor.fetchone()
   # print(mem_score)
    #add todays points
   # real_score = mem_score[0]+x 
    #print(real_score)

    #update member score
    #sql2 = "UPDATE fam_score set %s = %s" 
    #val2 = (mem_num, real_score)
   # cursor = mysql.connection.cursor()
   # cursor.execute(sql2, val2)
   # mysql.connection.commit()

   # total_fam_score(mysql, fam_id, fq_id, real_score)

   #def new_famscore_row(mysql, fam_id ): 
    #make new fam_score row if not exist
  #  sql1 = 'SELECT * FROM fam_score WHERE fam_id = %s'
   # val1 = (fam_id)
   # cursor = mysql.connection.cursor()
  #  cursor.execute(sql1, val1)
 #   if cursor.rowcount == 0:
    #    sql2 = "INSERT INTO fam_score (fam_id, mem_1, mem_2, mem_3, mem_4) VALUES (%s, %s, %s, %s, %s)" 
   #     val2 = (fam_id, '0', '0', '0', '0')
  #      cursor = mysql.connection.cursor()
 #       cursor.execute(sql2, val2)
#        mysql.connection.commit()
    
#def find_mem_num(mysql, fam_id, u_id):
 #   sql1 = 'SELECT * FROM family WHERE id = %s'
  #  val1 = (fam_id, )
  #  cursor = mysql.connection.cursor()
  #  cursor.execute(sql1, val1)
   # fam_det = cursor.fetchone()

    #find which member of the fam it is
 #   if fam_det[2] ==  u_id:
 #       return "mem_1"
 #   if fam_det[3] == u_id:
  #      return "mem_2"
   # if fam_det[4] ==  u_id:
   #     return "mem_3"
   # if fam_det[4] == u_id:
   #     return "mem_4"



