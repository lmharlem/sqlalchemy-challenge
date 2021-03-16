# Python code for homework SQL Chalenge
# Juan F Ramirez Tovar

# Import libraries
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
from flask import Flask, jsonify
from datetime import datetime
from sqlalchemy import and_


app = Flask(__name__)
user_name = 'Juanfer'
user_message = f'Welcome {user_name}'
user_result = 20* 1000


engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
measurement = Base.classes.measurement
station = Base.classes.station
session = Session(engine)
inspector = inspect(engine)
#for table_name in inspector.get_table_names():
 #   for column in inspector.get_columns(table_name):
  #      print(column['name'], column['type'])


@app.route("/")
def home():
    print("Server received a GET request...")
    str = f"""<h1>Wellcome to Tempeture and Precipitation Application for Hawai</h1>
    <p>------------------------------------</p>
    <h2>Below please find availible routes</h2>
    <p>------------------------------------</p>
    <ul>
        <li>List of Precipitations by date: <b><a href="/api/v1.0/precipitation">/api/v1.0/precipitation</a></b></li>
        <li>Stations Dataset: <b><a href="/api/v1.0/stations">/api/v1.0/stations</a></b></li>
        <li>Most active station last 12 months Tempeture observation: <b><a href="/api/v1.0/tobs">/api/v1.0/tobs</a></b></li>
        <li>Temperature analisis from start (yyyy-mm-dd):<b><a href="/api/v1.0/2016-08-23">/api/v1.0/&lt;start&gt;</a></b></li>
        <li>Temperature analisis from start/end (yyyy-mm-dd):<b><a href="/api/v1.0/2016-08-23/2017-08-23">/api/v1.0/&lt;start&gt;/&lt;end&gt;</a></b></li>
    """
    return str

@app.route("/api/v1.0/precipitation")
def precipitation():
    print('Server received a GET request on /api/v1.0/precipitation')
    
    prcp_query = (
        session.query(measurement)
        .order_by(measurement.date.desc())
        .all()
    )
    prcp_dictionary = {}
    for prcp in prcp_query:
        prcp_dictionary.update({prcp.date: prcp.prcp})

    return jsonify(prcp_dictionary)

@app.route("/api/v1.0/stations")
def stations():
    print('Server received a GET request on /api/v1.0/stations')
    
    stations_query = (
        session.query(station)
        .all()
    )

    stations_db = []

    for stations in stations_query:
    
        stations_dictionary = {}
        stations_dictionary["Station"] = stations.station
        stations_dictionary["Name"] = stations.name
        stations_db.append(stations_dictionary)
    
    return jsonify(stations_db)


@app.route("/api/v1.0/tobs")
def tobs():
    print('Server received a GET request on /api/v1.0/tobs')
    
    find_most_active = (
        session
        .query(measurement.station)
        .group_by(measurement.station)
        .order_by(func.count(measurement.station).desc())
        .first()
    )
 
    date_finder = (
        session.query(measurement.date)
        .order_by(measurement.date.desc())
        .first()
        )
    year,month,day = date_finder.date.split("-")
    last_date = dt.date(int(year),int(month),int(day))
    date4query=last_date-dt.timedelta(days=365)

    tobs_query = (
        session
        .query(measurement)
        .filter(and_(measurement.station == find_most_active.station, measurement.date >= date4query))
        .all()
    )

    tobs_data = []
    for record in tobs_query:
        tobs_dictionary = {}
        tobs_dictionary["Date"] = record.date
        tobs_dictionary["TOBS"] = record.tobs
        tobs_data.append(tobs_dictionary)
    
    return jsonify(tobs_data)


@app.route("/api/v1.0/<date>")
def above(date):
    print(f"Server received a GET request on /api/v1.0/{date}")
    
    
    maximum = (
        session
        .query(func.max(measurement.tobs))
        .filter(measurement.date >= date)
        .all()
    )

    minimum = (
        session
        .query(func.min(measurement.tobs))
        .filter(measurement.date >= date)
        .all()
    )
    
    average = (
        session
        .query(func.avg(measurement.tobs))
        .filter(measurement.date >= date)
        .all()
    )

    temp_dictionary = {
        "Maximum_Tempeture": maximum,
        "Minimum_Tempeture": minimum,
        "Average_Tempeture": average,
    }

    return jsonify(temp_dictionary)
    
@app.route("/api/v1.0/<start>/<end>")
def range(start,end):
    print(f"Server received a GET request on /api/v1.0/{start}/{end}")
    
    
    maximum2 = (
        session
        .query(func.max(measurement.tobs))
        .filter(and_(measurement.date >= start, measurement.date <= end))
        .all()
    )

    minimum2 = (
        session
        .query(func.min(measurement.tobs))
        .filter(and_(measurement.date >= start, measurement.date <= end))
        .all()
    )
    
    average2 = (
        session
        .query(func.avg(measurement.tobs))
        .filter(and_(measurement.date >= start, measurement.date <= end))
        .all()
    )

    temp_dictionary2 = {
        "Maximum_Tempeture": maximum2,
        "Minimum_Tempeture": minimum2,
        "Average_Tempeture": average2,
    }

    return jsonify(temp_dictionary2)

if __name__ == "__main__":
    app.run(debug=True)

    