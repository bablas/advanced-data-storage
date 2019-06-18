import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify
import datetime as dt

engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False}, echo=True)
Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)

app = Flask(__name__)

@app.route("/")
def welcome():
    """List all available api routes."""
    return"""<html>
    <h1>HOMEPAGE</h1>
    <br>
    <h2>List of all API routes</h2>
    <ul>
    <br>
    <li>
    List of Dates and Precipitation:
    <br>
    <a href="/api/v1.0/precipitation">/api/v1.0/precipitation</a>
    </li>
    <br>
    <li>
    List of stations from the dataset: 
    <br>
   <a href="/api/v1.0/stations">/api/v1.0/stations</a>
   </li>
    <br>
    <li>
    List of Temperature Observations (tobs) for the previous year:
    <br>
    <a href="/api/v1.0/tobs">/api/v1.0/tobs</a>
    </li>
    <br>
    <li>
    List of the minimum temperature, the average temperature, and the max temperature for a given start date:
    <br>
    <a href="/api/v1.0/2017-02-28">/api/v1.0/2017-02-28</a>
    </li>
    <br>
    <li>
    List the minimum temperature, the average temperature, and the max temperature for a given range of dates:
    <br>
    <a href="/api/v1.0/2017-02-28/2017-03-05">/api/v1.0/2017-02-28/2017-03-05</a>
    </li>
    <br>
    </ul>
    </html>

    """


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of precipitations from last year"""
    max_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    max_date = max_date[0]
    year_ago = dt.datetime.strptime(max_date, "%Y-%m-%d") - dt.timedelta(days=366)
    results_precipitation = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_ago).all()
    precipitation_dict = dict(results_precipitation)

    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations(): 
    """Return a JSON list of stations from the dataset."""
    results_stations =  session.query(Measurement.station).group_by(Measurement.station).all()
    stations_list = list(np.ravel(results_stations))

    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs(): 
    """Return a JSON list of Temperature Observations (tobs) for the previous year."""
    max_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    max_date = max_date[0]
    year_ago = dt.datetime.strptime(max_date, "%Y-%m-%d") - dt.timedelta(days=366)
    results_tobs = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= year_ago).all()
    tobs_list = list(results_tobs)

    return jsonify(tobs_list)



@app.route("/api/v1.0/<start>")
def start(start=None):
    """Return a JSON list of tmin, tmax, tavg for the dates greater than or equal to the date provided"""

    from_start = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).group_by(Measurement.date).all()
    from_start_list=list(from_start)
    return jsonify(from_start_list)

    

@app.route("/api/v1.0/<start>/<end>")
def start_end(start=None, end=None):
    """Return a JSON list of tmin, tmax, tavg for the dates in range of start date and end date inclusive"""
    
    between_dates = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).group_by(Measurement.date).all()
    between_dates_list=list(between_dates)
    return jsonify(between_dates_list)



if __name__ == '__main__':
    app.run(debug=True)