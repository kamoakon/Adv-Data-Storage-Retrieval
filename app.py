import datetime as dt
import numpy as np
import pandas as pd
import datetime as dt

#SQL Alchemy imports
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#Creation of Flask routes & connecting database

engine = create_engine("sqlite:///Hawaii.sqlite")

Base = automap_base()

Base.prepare(engine, reflect=True)

# Saving into stations and measurements tables
Stations = Base.classes.stations
Measurements = Base.classes.measurements

# Creation of Session
session = Session(engine)


# Flask Setup

app = Flask(__name__)


# Flask Routes

@app.route("/")
def welcome():
    """Available api routes."""
    return (
        f"Available Routes:<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"Query for the dates and temperature observations from the last year<br/>"
        f"Convert the query results to a Dictionary using date as the key and tobs as the value<br/>"
        f"Return the json representation of your dictionary <br/>"
        f"<br/>"
        f"/api/v1.0/stations<br/>"
        f"Return a json list of stations from the dataset<br/>"
        f"<br/>"
        f"/api/v1.0/tobs<br/>"
        f"Return a json list of Temperature Observations (tobs) for the previous year<br/>"
        f"<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
        f"Return a json list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.<br/>"
        f"When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.<br/>"
        f"When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.<br/>"
    )

#    Query for the dates and temperature observations from the last year.
#   Convert the query results to a Dictionary using date as the key and tobs as the value.
#   Return the json representation of your dictionary.

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of rain fall for prior year"""

    last = session.query(Measurements.date).order_by(Measurements.date.desc()).first()
    year = dt.date(2016, 8, 23)
    prec = session.query(Measurements.date, Measurements.prcp).\
        filter(Measurements.date > year).\
        order_by(Measurements.date).all()

# creation dictionary for output
    prec_tot = []
    for p in prec:
        row = {}
        row["date"] = prec[0]
        row["prcp"] = prec[1]
        prec_tot.append(row)

    return jsonify(prec)

#Return a json list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    stations_query = session.query(Stations.name, Stations.station)
    stations = pd.read_sql(stations_query.statement, stations_query.session.bind)
    return jsonify(stations.to_dict())


#Return a json list of Temperature Observations (tobs) for the previous year
@app.route("/api/v1.0/tobs")
def tobs():
    """Return a list of temperatures for prior year"""
#    * Query for the dates and temperature observations from the last year.
#           * Convert the query results to a Dictionary using `date` as the key and `tobs` as the value.
#           * Return the json representation of your dictionary.
    last = session.query(Measurements.date).order_by(Measurements.date.desc()).first()
    year = dt.date(2016, 8, 23)
    temp = session.query(Measurements.date, Measurements.tobs).\
        filter(Measurements.date > year).\
        order_by(Measurements.date).all()

# Creating dictionary to store output
    temp_tot = []
    for t in temp:
        row = {}
        row["date"] = temp[0]
        row["tobs"] = temp[1]
        temp_tot.append(row)

    return jsonify(temp_tot)


#Return a json list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
#When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
#When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.



@app.route("/api/v1.0/<start>")
def temperatures_start(start):
    """ Given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than 
        and equal to the start date. 
    """

    start = dt.date(2016, 8, 23)

    results = session.query(func.min(Measurements.tobs), func.avg(Measurements.tobs), func.max(Measurements.tobs)).\
                filter(Measurements.date >= start).all()
    
    # Convert list of tuples into normal list
    temperatures_start = list(np.ravel(results))

    return jsonify(temperatures_start)


@app.route("/api/v1.0/<start>/<end>")
def temperatures_start_end(start, end):
    start = dt.date(2016, 8, 23)

    results = session.query(func.min(Measurements.tobs), func.avg(Measurements.tobs), func.max(Measurements.tobs)).\
                filter(Measurements.date >= start).\
                filter(Measurements.date <= end).all()
    
    # Convert list of tuples into normal list
    temperatures_start_end = list(np.ravel(results))

    return jsonify(temperatures_start_end)


#Necessary

if __name__ == "__main__":
    app.run(debug=True)