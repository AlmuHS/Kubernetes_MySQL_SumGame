from flask import Flask, render_template, request, session, redirect
from flask_wtf import FlaskForm
from flask_session import Session
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired

from redis import Redis, RedisError

from random import randint, getrandbits
from datetime import datetime

import mysql.connector 
import os

redis = Redis(host="redis", db=0, socket_connect_timeout=2, socket_timeout=2)

app = Flask(__name__)

SECRET_KEY='5f352379324c22463451387a0aec5d2f'
app.secret_key = SECRET_KEY
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

class QuestForm(FlaskForm):
    username = StringField('Nombre de Usuario', validators=[DataRequired()])
    result = StringField('Resultado', validators=[DataRequired()])
    submit_result = SubmitField('Comprobar respuesta')
        
class ReturnIndexForm(FlaskForm):
    return_submit = SubmitField('Volver al inicio')

def register_user(db, cursor, user: str):
        query_user_exists = f"select id from JUGADORES where usuario = '{user}'"
        cursor.execute(query_user_exists)
        
        results = cursor.fetchone()
        if not results:
                insert_user = f"insert into JUGADORES(usuario, puntos_totales) VALUES ('{user}', 0)"
                cursor.execute(insert_user)
               
                db.commit()

def insert_game(cursor, user: str, points: int):
        date = datetime.now()
        formatted_date = date.strftime('%Y-%m-%d %H:%M:%S')
        
        query_userid = f"select id from JUGADORES where usuario = '{user}'"
        cursor.execute(query_userid)
        userid = cursor.fetchone()[0]
        
        insert = f"insert into PARTIDAS(jugador, fecha, puntos) VALUES ({userid}, '{formatted_date}', {points})"
        
        cursor.execute(insert)                    

def update_points(cursor, user: str):
        update_pt = f"update JUGADORES set puntos_totales = puntos_totales + 5 where usuario = '{user}'"
        cursor.execute(update_pt)


def get_keys():
        client_id = session.get('id')
        
        if not client_id:
                session['id'] = getrandbits(10)
                client_id = session_id
        
        key1 = f"num1-{client_id}"
        key2 = f"num2-{client_id}"
        
        print(key1)
        
        return key1, key2

def gen_numbers():
        num1 = randint(10, 30)
        num2 = randint(10, 30)
        
        key1, key2 = get_keys()

        redis.set(key1, num1)
        redis.set(key2, num2)

def get_numbers():
        key1, key2 = get_keys()

        num1 = -1
        num2 = -1
        
        value1 = redis.get(key1)
        value2 = redis.get(key2)
        
        if value1 and value2:
                num1 = int(value1)
                num2 = int(value2)
        
        return num1, num2

@app.route('/')
def set():
    session['id'] = getrandbits(10)
    return redirect("/game")

@app.route("/game", methods=['GET', 'POST'])
def main():
        form = QuestForm()
        return_index = ReturnIndexForm()
                                     
        try:
            mydb = mysql.connector.connect(
              host=os.environ['MYSQL_HOST'],
              user="gameusr",
              password="game",
              database="GameDB"
            )
        except mysql.connector.Error as err:
                error_message = err.msg
                return render_template("error.html", data=error_message)
        
        num1 = 0
        num2 = 0
        question = ""
        
        try:
                if request.method == 'GET' or return_index.return_submit.data:
                        gen_numbers()
                
                num1, num2 = get_numbers()
                question = f"{num1} + {num2} = ?"
                
        except RedisError:
                error_message = "cannot connect to Redis"
                return render_template("error.html", data=error_message)
       
        cursor = mydb.cursor()
        
        if form.submit_result.data and form.validate_on_submit():
                try:
                        register_user(mydb, cursor, form.username.data)
                
                        points = 0
                        message = "Respuesta incorrecta :("
                
                        if (form.result.data.isdigit()):
                                if num1 + num2 == int(form.result.data):
                                        print("Respuesta correcta")
                                        
                                        update_points(cursor, form.username.data)
                                        
                                        points = 5
                                        message = "Respuesta correcta!!"
                        
                        insert_game(cursor,form.username.data, points)
                        
                        mydb.commit()
                        
                        return render_template("message.html", data=message, form=return_index)
                        
                except mysql.connector.Error as err:
                        error_message = err.msg
                        return render_template("error.html", data=error_message)
                        
        return render_template('quest.html', title='Pregunta', form=form, data=question)
        
if __name__ == "__main__":
        app.run(host='0.0.0.0', port=80)

        
