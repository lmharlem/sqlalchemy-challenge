import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# find the last date in the database
last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

# Calculate the date 1 year ago from the last data point in the database
query_date = dt.date(2017,8,23) - dt.timedelta(days=365)

session.close()

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    return (
        f"Welcome to Surf's Up! Hawaii Climate API!<br/>"
        f"Available Routes:<br/>"
        f"<br/>"
        f"List of precipitation data with dates:<br/>" 
        f"/api/v1.0/precipitation<br/>"
        f"<br/>" 
        f"List of stations and names:<br/>"
        f"/api/v1.0/stations<br/>"
        f"<br/>" 
        f"List of temperature observations from a year from the last data point:<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>" 
        f"/api/v1.0/start_date<br/>"
        f"Please type your start_date in YYYY-MM-DD format to retrieve min, avg and max of observed temperatures.<br/>"
        f"<br/>" 
        f"/api/v1.0/start_date/end_date<br/>"
        f"Please type your start_date and end_date in YYYY-MM-DD/YYYY-MM-DD format to retrieve min, avg and max of observed temperatures."
        #f"/api/v1.0/temp/start/end"
        )


@app.route("/api/v1.0/precipitation")
def prcp():

    """Return the precipitation data for the last year"""

    # Calculate the date 1 year ago from last date in database
    session = Session(engine)

    # Query for the date and precipitation for the last year
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= query_date).all()

    session.close()

    # Dict with date as the key and prcp as the value
    precipitation = {date: prcp for date, prcp in results}
    return jsonify(precipitation)


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    """Return a list of stations."""
    results = session.query(Station.station, Station.name).all()
    
    session.close()

    stations = {station: name for station, name in results}
    return jsonify(stations)

################################################################################################################################

@app.route("/api/v1.0/tobs")
def temp_monthly():
    session = Session(engine)
    """Return the temperature observations (tobs) for previous year."""

    # Query the primary station for all tobs from the last year
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= query_date).all()

    session.close()

    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))

    # Return the results
    return jsonify(temps=temps)


##############################################################################################################################


@app.route("/api/v1.0/<start>")
def start_date(start):
    #Create Session
    session = Session(engine)
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start date."""
    # Query results

    dates = session.query(Measurement.date).all()

    dates = list(np.ravel(dates))
    
    if start in dates:
        calc_start = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

        session.close()
   

        result = list(np.ravel(calc_start))

        result_dict = {'Min Temperature (F)': result[0], 'Avg Temperature (F)': result[1], 'Max Temperature (F)': result[2]}

        return jsonify(result_dict)
    else:
        return (f'Oops, we have encountered a problem!<br>'
                f'Possible Results:<br>'
                f'1. The date you search for is not within the data set.<br>'
                f'2. You have not typed the date in the required format.<br>'
                f'Note: Required Date Format is YYYY-MM-DD'
        )

#################################################################################################################################

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    #Create Session
    session = Session(engine)

    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start and end dates."""

    # Query results

    dates = session.query(Measurement.date).all()

    dates = list(np.ravel(dates))
    
    if start in dates:
        if end in dates:

            calc_start = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).filter(Measurement.date <= end).all()

            session.close()
   
            result = list(np.ravel(calc_start))

            result_dict = {'Min Temperature (F)': result[0], 'Avg Temperature (F)': result[1], 'Max Temperature (F)': result[2]}

            return jsonify(result_dict)
        else:
            return (f'Oops, we have encountered a problem!<br>'
                    f'Possible Results:<br>'
                    f'1. The end date you search for is not within the data set.<br>'
                    f'2. You have not typed the end date in the required format.<br>'
                    f'Note: Required Date Format is YYYY-MM-DD'
            )

    return (f'Oops, we have encountered a problem!<br>'
            f'Possible Results:<br>'
            f'1. The start date you search for is not within the data set.<br>'
            f'2. You have not typed the start date in the required format.<br>'
            f'Note: Required Date Format is YYYY-MM-DD'
            )

if __name__ == '__main__':
    #app.run(debug=True)
    app.run()
