import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt
from datetime import datetime
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite",connect_args={'check_same_thread': False})

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Base.classes.keys()
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/precipitation<br/>"
        f"/api/stations<br/>"
        f"/api/temperature<br/>"
        f"/api/start_date(YYYY-MM-DD)<br/>"
        f"/api/start_date(YYYY-MM-DD)/end_date(YYYY-MM-DD)<br/>"
    )


@app.route("/api/precipitation")
def prcp():
    """Return the query results to a Dictionary using date as the key and prcp as the value."""
    # Query all precipitaion data
    results = session.query(Measurement.date, Measurement.prcp).all()

    # Create a dictionary from the row data and append to a list 
    all_prcp = []
    for rain in results:
        prcp_dict = {}
        prcp_dict[str(rain.date)] = rain.prcp
        all_prcp.append(prcp_dict)

    return jsonify(all_prcp)

@app.route("/api/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
    # Query all stations
    results = session.query(Measurement.station).distinct().all()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

@app.route("/api/temperature")
def temperature():
    """Return a JSON list of stations from the dataset."""
    # Query temperature from last one year in the data
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]

    first_date = (datetime.strptime(last_date, '%Y-%m-%d').date() - (dt.timedelta(days=365))).strftime('%Y-%m-%d')
    results = session.query(Measurement.date,Measurement.tobs).filter(Measurement.date >=first_date)\
        .filter(Measurement.date <= last_date).order_by(Measurement.date).all()

    # Create a dictionary from the row data and append to a list 
    all_temp = []
    for temperature in results:
        temp_dict = {}
        temp_dict[str(temperature.date)] = temperature.tobs
        all_temp.append(temp_dict)

    return jsonify(all_temp)

@app.route('/api/<start>')
def temp_start_stats(start=None, end=None):
    #when given the start calculate the TMIN, TAVG, and TMAX for dates after'''
    start_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).all()

    #convert list of tuples into normal list
    start_temp = list(np.ravel(start_results))

    #return json representation of the list
    return jsonify(start_temp)


@app.route('/api/<start>/<end>')
def temp_start_end_stats(start=None, end=None):
    #when given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates in between '''
    start_end_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= str(start)).filter(Measurement.date <= str(end)).all()

    #convert list of tuples into normal list
    start_end_temp = list(np.ravel(start_end_results))

    #return json representation of the list
    return jsonify(start_end_temp)

if __name__ == '__main__':
    app.run(debug=True)