import os

import psycopg2
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


from helpers import apology

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response










@app.route("/edit", methods=["POST"])
def edit():
    button_type = request.form.get("button_type")


    host = request.form.get("host")
    database = request.form.get("database")
    user = request.form.get("user")
    password = request.form.get("password")

    # Configure psycopg2 to use POSTGRESQL database if credentials are correct
    mydb = psycopg2.connect(user=user, password = password, host = host, database=database)
    db = mydb.cursor()

    # get a list of column names from database from TABLE_NAME
    TABLE_NAME = request.form.get("TABLE_NAME")
    db.execute("select column_name from information_schema.columns where table_name= %s", (TABLE_NAME,))
    heads = db.fetchall()

    # select tables from datbaase
    db.execute("""SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'""")
    tables = db.fetchall()


    # save info from added row in dict
    data = {}
    for head in heads:
        data[head[0]] = request.form.get("old_" + head[0])
    #query database to insert new row
        #save conditions in one string
    conditions = ""
    for i in range(len(heads)):
        if i == len(heads) - 1:
            conditions += heads[i][0] + " = '" + data[heads[i][0]] + "'"
            break
        conditions += heads[i][0] + " = '" + data[heads[i][0]] + "' AND "

    if button_type == 'delete':

        db.execute('DELETE FROM "' + TABLE_NAME + '"' + ' WHERE ' + conditions)
        mydb.commit()

        #get all rows data from database
        db.execute('select * from "' + TABLE_NAME + '"')
        rows = db.fetchall()


        return render_template("change.html", rows = rows, heads = heads, tables = tables, host=host, database=database, user=user, password=password, exit="Exit", TABLE_NAME = TABLE_NAME)
    if button_type == 'edit':

        #get all rows data from database
        db.execute('SELECT * FROM "' + TABLE_NAME + '"' + ' WHERE ' + conditions)
        row = db.fetchall()[0]


        return render_template("edit.html",data = data, row = row, heads = heads, tables = tables, host=host, database=database, user=user, password=password, exit="Exit", TABLE_NAME = TABLE_NAME)
    if button_type == 'confirm':

        # save info from edited row in dict
        data = {}
        for head in heads:
            data[head[0]] = request.form.get(head[0])
        #query database to edit row
            #save new values string
        new = ""
        for i in range(len(heads)):
            if i == len(heads) - 1:
                new += heads[i][0] + " = '" + data[heads[i][0]] + "'"
                break
            new += heads[i][0] + " = '" + data[heads[i][0]] + "' , "

        db.execute('UPDATE "' + TABLE_NAME + '"' + ' SET '  + new + ' WHERE ' + conditions)
        mydb.commit()

        #get all rows data from database
        db.execute('select * from "' + TABLE_NAME + '"')
        rows = db.fetchall()

        return render_template("change.html", rows = rows, heads = heads, tables = tables, host=host, database=database, user=user, password=password, exit="Exit", TABLE_NAME = TABLE_NAME)

@app.route("/add", methods=["POST"])
def add():
    host = request.form.get("host")
    database = request.form.get("database")
    user = request.form.get("user")
    password = request.form.get("password")


    # Configure psycopg2 to use POSTGRESQL database if credentials are correct
    mydb = psycopg2.connect(user=user, password = password, host = host, database=database)
    db = mydb.cursor()

    # get a list of column names from database from TABLE_NAME
    TABLE_NAME = request.form.get("TABLE_NAME")
    db.execute("select column_name from information_schema.columns where table_name= %s", (TABLE_NAME,))
    heads = db.fetchall()

    # save info from added row in dict
    data = {}
    for head in heads:
        data[head[0]] = request.form.get(head[0])

    #query database to insert new row
        #save values in one string
    values = "('"
    for i in range(len(heads)):
        if i == len(heads) - 1:
            values += data[heads[i][0]] + "')"
            break
        values += data[heads[i][0]] + "', '"

        #save column names in one string
    cols = "("
    for i in range(len(heads)):
        if i == len(heads) - 1:
            cols += heads[i][0] + ")"
            break
        cols += heads[i][0] + ", "

    db.execute('INSERT INTO "' + TABLE_NAME + '"' + cols + ' VALUES' + values)
    mydb.commit()

    # select tables from datbaase
    db.execute("""SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'""")
    tables = db.fetchall()

    #get all rows data from database
    db.execute('select * from "' + TABLE_NAME + '"')
    rows = db.fetchall()

    return render_template("change.html", rows = rows, heads = heads, tables = tables, host=host, database=database, user=user, password=password, exit="Exit", TABLE_NAME = TABLE_NAME)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":

        host = request.form.get("host")
        database = request.form.get("database")
        user = request.form.get("user")
        password = request.form.get("password")

        host = "ec2-54-74-14-109.eu-west-1.compute.amazonaws.com"
        database= "d8lued2265pr44"
        user= "kdjmispwzuqrpa"
        password= "79fabf4112ead809504789c52d5037b2ecdd9967a4a4ef9c64c79df78bf36064"

        # Configure psycopg2 to use POSTGRESQL database if credentials are correct
        try:
            mydb = psycopg2.connect(user=user, password = password, host = host, database=database)
            db = mydb.cursor()
        except:
            return render_template("apology.html", top ='Database not found' , exit = 'EXIT')

        # select tables from datbaase
        db.execute("""SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'""")
        tables = db.fetchall()
        if tables[0][0] == None:
            return apology("Database empty")

        return render_template("indexed.html", tables = tables, host=host, database=database, user=user, password=password, exit="EXIT")

    else:
        return render_template("index.html")


@app.route("/change", methods=["POST"])
def change():
    host = request.form.get("host")
    database = request.form.get("database")
    user = request.form.get("user")
    password = request.form.get("password")

    # Configure psycopg2 to use POSTGRESQL database if credentials are correct
    mydb = psycopg2.connect(user=user, password = password, host = host, database=database)
    db = mydb.cursor()

    # select tables from datbaase
    db.execute("""SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'""")
    tables = db.fetchall()

    # get a list of column names from database
    TABLE_NAME = request.form.get("TABLE_NAME")
    db.execute("select column_name from information_schema.columns where table_name= %s", (TABLE_NAME,))
    heads = db.fetchall()

    #get all rows data from database
    db.execute('select * from "' + TABLE_NAME + '"')
    rows = db.fetchall()

    #get columns type
    db.execute("SELECT DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = %s", (TABLE_NAME,))
    types = db.fetchall()

    return render_template("change.html",types = types, rows = rows, heads = heads, tables = tables, host=host, database=database, user=user, password=password, exit="Exit", TABLE_NAME = TABLE_NAME)




def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
