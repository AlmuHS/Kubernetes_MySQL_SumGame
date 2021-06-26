from flask import Flask, render_template

import mysql.connector
import os

SECRET_KEY='5f352379324c22463451387a0akklsaklakslaksodm'
app = Flask(__name__)
app.secret_key = SECRET_KEY
    
@app.route("/", methods=['GET', 'POST'])
def main():
        try:
            mydb = mysql.connector.connect(
              host=os.environ['MYSQL_HOST'],
              user="gameusr",
              password="game",
              database="GameDB"
            )
            
            cursor = mydb.cursor()
            
            query_ranking = f"select usuario, puntos_totales from JUGADORES ORDER BY puntos_totales DESC"
            cursor.execute(query_ranking)
            
            results = cursor.fetchall()
            headers = [header[0] for header in cursor.description]
            
        except mysql.connector.Error as err:
                error_message = err.msg
                return render_template("error.html", data=error_message)
        
        return render_template("ranking.html", data=results, headers=headers)
        
if __name__ == "__main__":
        app.run(host='0.0.0.0', port=5001)
