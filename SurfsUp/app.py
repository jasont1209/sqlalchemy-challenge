# Import the dependencies.

import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
#################################################
# Database Setup
#################################################
# Create engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")


# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

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

# Start at the homepage.

# List all the available routes.
@app.route("/")
def welcome():
    return(
        f"Available routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )
# /api/v1.0/precipitation

# Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value.
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    one_year = dt.date(2017,8,23) - dt.timedelta(days = 365)
    recent_one_year = dt.date(one_year.year, one_year.month, one_year.day)
    date_prcp = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= recent_one_year)\
    .order_by(Measurement.date).all()
    session.close()
# Return the JSON representation of your dictionary.
    precip_dict = dict(date_prcp)

    return jsonify(precip_dict)


# /api/v1.0/stations
# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    station_query = session.query(Station.station).all()
    session.close()

    stations_list = list(np.ravel(station_query))
    return jsonify(stations_list)


# /api/v1.0/tobs

# Query the dates and temperature observations of the most-active station for the previous year of data.
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    one_year = dt.date(2017,8,23) - dt.timedelta(days = 365)

    active_stations = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station)\
    .order_by(func.count(Measurement.station).desc()).all()

    session.close()


# Return a JSON list of temperature observations for the previous year.
    temp_list = list(np.ravel(active_stations))
    return jsonify(temp_list)
# /api/v1.0/<start> and /api/v1.0/<start>/<end>
# Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.
# For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
# For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.

@app.route("/api/v1.0/<start>")
def temp_start(start):
    session = Session(engine)
    query_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
                .filter(Measurement.date >= start).all()
    session.close()

    query_list = list(np.ravel(query_data))
    return jsonify (query_list)

@app.route("/api/v1.0/<start>/<end>")
def temp_start_end(start, end):
    session = Session(engine)
    query_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
                .filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()

    query_list = list(np.ravel(query_data))
    return jsonify(query_list)

#run
if __name__ == "__main__":
    app.run(debug=True)
    