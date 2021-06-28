from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired

from redis import Redis, RedisError

from random import randint
from datetime import datetime

import mysql.connector 
import os

SECRET_KEY='5f352379324c22463451387a0aec5d2f'

redis = Redis(host="redis", db=0, socket_connect_timeout=2, socket_timeout=2)

app = Flask(__name__)
app.secret_key = SECRET_KEY

class QuestForm(FlaskForm):
    username = StringField('Nombre de Usuario', validators=[DataRequired()])
    result = IntegerField('Resultado', validators=[DataRequired()])
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
        client_ip = request.remote_addr

        key1 = f"num1-{client_ip}"
        key2 = f"num2-{client_ip}"
        
        return key1, key2

def gen_numbers():
        num1 = randint(10, 30)
        num2 = randint(10, 30)
        
        key1, key2 = get_keys()

        redis.set(key1, num1)
        redis.set(key2, num2)

def get_numbers():
        key1, key2 = get_keys()

        num1 = int(redis.get(key1))
        num2 = int(redis.get(key2))
        
        return num1, num2

@app.route("/", methods=['GET', 'POST'])
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
                visits = "<i>cannot connect to Redis</i>"
       
        cursor = mydb.cursor()
        
        if form.submit_result.data and form.validate_on_submit():
                try:
                        register_user(mydb, cursor, form.username.data)
                
                        points = 0
                        message = "Respuesta incorrecta :("
                
                        if num1 + num2 == form.result.data:
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
        app.run(host='0.0.0.0', port=5000)

        
