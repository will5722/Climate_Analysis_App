import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
measurement = Base.classes.measurement
station = Base.classes.station

app = Flask(__name__)

@app.route("/")
def home():
    return ("Welcome to the Hawaii Climate App</br>"
            "Below are the available routes:</br>"
            "/api/v1.0/precipitation</br>"
            "/api/v1.0/stations</br>"
            "/api/v1.0/tobs</br>"
            "/api/v1.0/start. Enter date as (YYYY-MM-DD)</br>"
            "/api/v1.0/start/end. Enter dates as (YYYY-MM-DD)</br>")
            
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    
    prior_year = dt.date(2017,8,23) - dt.timedelta(days=365)
    
    precip_data = session.query(measurement.date, measurement.prcp).filter(measurement.date >= prior_year).\
        order_by(measurement.date).all()
    
    session.close()
    
    prcp_data = []
    for data in precip_data:
        prcp_dict = {}
        prcp_dict["date"] = data.date
        prcp_dict["prcp"] = data.prcp
        prcp_data.append(prcp_dict)   
        
    return jsonify(prcp_data)



@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    
    names = session.query(station.name).all()
    
    stations = list(np.ravel(names))
    
    session.close()
    
    return jsonify(stations)



@app.route("/api/v1.0/tobs")
def tobs():
    prior_year = dt.date(2017,8,23) - dt.timedelta(days=365)
    
    session = Session(engine)
    
    temp_data = session.query(measurement.tobs, measurement.date).filter(measurement.date >= prior_year).\
        filter(measurement.station == "USC00519281").order_by(measurement.date).all()
    
    temp_list = list(np.ravel(temp_data))
    
    return jsonify(temp_list)


@app.route("/api/v1.0/<startdate>")
def start(startdate):
    session = Session(engine)
    
    sel = [measurement.date, func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]
    
    query = (session.query(*sel).filter(func.strftime("%Y-%m-%d", measurement.date) >= startdate).group_by(measurement.date).all())
    
    data = []
    session.close()
    
    for item in query:
        data_dict = {}
        data_dict["Date"] = item[0]
        data_dict["Min Temp"] = item[1]
        data_dict["Avg Temp"] = item[2]
        data_dict["Max Temp"] = item[3]
        data.append(data_dict)
        
    return jsonify(data)



@app.route("/api/v1.0/<startdate>/<enddate>")
def startend(startdate, enddate):
    session = Session(engine)
    
    sel = [measurement.date, func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]
    
    query = (session.query(*sel).filter(func.strftime("%Y-%m-%d", measurement.date) >= startdate).\
             filter(func.strftime("%Y-%m-%d", measurement.date) <= enddate).group_by(measurement.date).all())
    
    data = []
    session.close()
    
    for item in query:
        data_dict = {}
        data_dict["Date"] = item[0]
        data_dict["Min Temp"] = item[1]
        data_dict["Avg Temp"] = item[2]
        data_dict["Max Temp"] = item[3]
        data.append(data_dict)
        
    return jsonify(data)




if __name__ == "__main__":
    app.run(debug=True)            