#CLIMATE APP

from datetime import datetime
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


# Database Setup

engine = engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement=Base.classes.measurement
Station=Base.classes.station

session = Session(engine)

# Flask
app = Flask(__name__)

# Routes

@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Welcome to the CLIMATE APP!!<br/>"
        f"<br/>"
        f"<br/>"
        f"Available Routes:<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"The dates and precipitation from last year<br/>"
        f"<br/>"
        f"/api/v1.0/stations<br/>"
        f"List of stations<br/>"
        f"<br/>"
        f"/api/v1.0/tobs<br/>"
        f"Temperature Observations from last year<br/>"
        f"<br/>"
        f"/api/v1.0/<start><br/>"
        f"List of `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date (dates between 2010-01-01 and 2017-08-23)<br/>"
        f"/api/v1.0/<start>/<end><br/>"
        f"The `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive (dates between 2010-01-01 and 2017-08-23)<br/>"
    )

@app.route("/api/v1.0/precipitation")
# Convert the query results to a Dictionary using date as the key and prcp as the value
def precipitation():
    
    last_12months = session.query(Measurement.date, Measurement.prcp).\
                   filter(Measurement.date.between('2016-08-23', '2017-08-23')).all()

    precipitation_data = []
    for result in last_12months:
        row = {"date":"precipitation"}
        row["date"] = result[0]
        row["precipitation"] = result[1]
        precipitation_data.append(row)

    #Return the JSON representation of your dictionary
    return jsonify(precipitation_data)


@app.route("/api/v1.0/stations")
def stations():

    station_results = session.query(Station.station).group_by(Station.station).all()
    station_list = list(np.ravel(station_results))
    # Return a JSON list of stations from the dataset
    return jsonify(station_list)


@app.route("/api/v1.0/tobs")
def tobs():

	# Query for the dates and temperature observations from a year from the last data point.
    tobs_results = session.query(Measurement.station, Measurement.tobs).\
                filter(Measurement.date.between('2016-08-23', '2017-08-23'))
    
    tobs_list=[]
    for tobs in tobs_results:
        tobs_dict = {}
        tobs_dict["station"] = tobs[0]
        tobs_dict["temperature"] = tobs[1]
       
        tobs_list.append(tobs_dict)
    # Return a JSON list of Temperature Observations (tobs) for the previous year.
    return jsonify(tobs_list)


@app.route("/api/v1.0/<start>")

def calc_temps(start='start_date'):
    # initial_date = start

    start_date = datetime.strptime(str(start), '%Y-%m-%d').date()
    start_results = session.query(func.min(Measurement.tobs), \
                            func.avg(Measurement.tobs),\
                            func.max(Measurement.tobs)).\
                            filter(Measurement.date >= start_date) 
    
    start_tobs = []
    for tobs in start_results:
        tobs_dict = {}
        tobs_dict["TMIN"] = tobs[0]
        tobs_dict["TAVG"] = tobs[1]
        tobs_dict["TMAX"] = tobs[2]
        
        start_tobs.append(tobs_dict)

    return jsonify(start_tobs)


@app.route("/api/v1.0/<start>/<end>")

def calc_temps_2(start='start_date', end='end_date'):  
    #initial_date = start
    #final_date = end

    start_date = datetime.strptime(str(start), '%Y-%m-%d').date()
    end_date = datetime.strptime(str(end), '%Y-%m-%d').date()

    start_end_results=session.query(func.min(Measurement.tobs), \
                      func.avg(Measurement.tobs),\
                      func.max(Measurement.tobs)).\
                      filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()   

    start_end_tobs = []
    for tobs in start_end_results:
        tobs_dict = {}
        tobs_dict["TMIN"] = tobs[0]
        tobs_dict["TAVG"] = tobs[1]
        tobs_dict["TMAX"] = tobs[2]
        
        start_end_tobs.append(tobs_dict)
   
    return jsonify(start_end_tobs)


if __name__ == "__main__":
    app.run(debug=True)
