# Import the dependencies.
import numpy as np
import datetime as dt
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, desc, func

from flask import Flask, jsonify




#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Declare a Base using `automap_base()`
Base = automap_base()

# Use the Base class to reflect the database tables
Base.prepare(autoload_with=engine)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station


# Create a session
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
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/'<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculate the date one year from the last date in data set.
    one_year  = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    # Perform a query to retrieve the data and precipitation scores
    past_year = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date > one_year).all()

    # Convert the query results to a dictionary using date as the key and prcp as the value
    precipitation_dict = {date: prcp for date, prcp in past_year}

    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    # Perform a query to retrieve the station data
    results = session.query(Station.station, Station.name).all()
    
    # Convert the query results to a list of dictionaries
    station_list = [{"station": station, "name": name} for station, name in results]
    
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def temperature():
    # Perform a query to retrieve the station data
    results = session.query(
        Measurement.date, Measurement.tobs
    ).filter(Measurement.station == "USC00519281").all()

    # Convert the query results to a list of dictionaries
    station_temps = [{"date": date, "temp": temp } for date, temp in results]

    return jsonify(station_temps)


@app.route("/api/v1.0/<start>")
def temperature_range(start):
    # Perform a query to calculate TMIN, TAVG, and TMAX for all dates greater than or equal to the start date
    results = session.query(
        Measurement.date,
        func.min(Measurement.tobs).label('TMIN'),
        func.avg(Measurement.tobs).label('TAVG'),
        func.max(Measurement.tobs).label('TMAX')
    ).filter(Measurement.date <= start).group_by(Measurement.date).all()

    # Convert the query results to a dictionary
    temp_stats = [{
        "date": result.date,
        "TMIN": result.TMIN,
        "TAVG": result.TAVG,
        "TMAX": result.TMAX
    } for result in results]

    return jsonify(temp_stats)

@app.route("/api/v1.0/<start>/<end>")
def temperature_ranges(start, end):
    # Perform a query to calculate TMIN, TAVG, and TMAX for all dates greater than or equal to the start date
    results = session.query(
        Measurement.date,
        func.min(Measurement.tobs).label('TMIN'),
        func.avg(Measurement.tobs).label('TAVG'),
        func.max(Measurement.tobs).label('TMAX')
    ).filter(
        Measurement.date >= start
    ).filter(
        Measurement.date <= end
    ).group_by(
        Measurement.date
    ).all()

    # Convert the query results to a dictionary
    temp_stats = [{
        "date": result.date,
        "TMIN": result.TMIN,
        "TAVG": result.TAVG,
        "TMAX": result.TMAX
    } for result in results]

    return jsonify(temp_stats)

if __name__ == '__main__':
    app.run(debug=True)
