from flask import redirect, url_for, session

def logout_int():
    session.pop('username', None)
    session.pop('u_id', None)
    session.pop('article', None)
    session.pop('q_id', None)
    return redirect (url_for("login"))