from flask import Flask,render_template,request,redirect,url_for
from flask.helpers import url_for
from flask_sqlalchemy import SQLAlchemy
import requests # to get the data from api.

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dizzywinds.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
class City(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(65), nullable = False)

def get_weather_data(city):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={ city }&units=metric&appid=3c2b749a88295ae0e8183ea712ee2425'#this is the api key along with the url to fetch the weather data's.   
    r = requests.get(url).json()
    return r

@app.route('/')
def dizzywinds_get():
    cities = City.query.all()
    weather_data = []
    for city in cities:
        r = get_weather_data(city.name)
        print(r) #I used this to see in what way is the requested data stored in 'r'.
        weather = {
          'city' : r['name'],
          'country' : r['sys']['country'],
          'temperature' :  r['main']['temp'],
          'feeltemp' : r['main']['feels_like'],
          'description' :  r['weather'][0]['description'],
          'icon' : r['weather'][0]['icon'],
          'windspeed' : r['wind']['speed'],
        }
        weather_data.append(weather)

    return render_template('base.html', weather = weather_data)

@app.route('/', methods = ['POST'])
def dizzywinds_post():
    err_msg = ''
    new_city = request.form['city'] #earlier like .form.get('city')
    if new_city:#if the new city to be added is in the api's record then only we'll create the entry into the database.
        existing_city = City.query.filter_by(name=new_city).first()
        if not existing_city:
            new_city_data =get_weather_data(new_city)
            if new_city_data['cod'] == 200:
                new_city = City(name=new_city)
                db.session.add(new_city)
                db.session.commit()
            else:
                err_msg = 'City does not exist in the world!'
        else:
            err_msg = 'City already exists!'
    return redirect(url_for('dizzywinds_get'))
   
@app.route('/delete/<name>')
def delete_city(name):
    city = City.query.filter_by(name = name).first()
    db.session.delete(city)
    db.session.commit()

    return redirect(url_for('dizzywinds_get'))

   

if __name__ == "__main__":
    app.run(debug=True, port=8000)
    