import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func,  inspect

from flask import Flask, jsonify




engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
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
        f"/api/v1.0/precipitation"
        f"//api/v1.0/stations"
        f"/api/v1.0/tobs"
        f"/api/v1.0/<start>"
        f"/api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of all precipitation data"""
    
    results = session.query(Measurement.date,Measurement.prcp).all()

    # Convert list of tuples into normal list
    prcp_list = []
    for data in results:
        prcp_dict={}
        prcp_dict['date']=data[0]
        prcp_dict['prcp']=data[1]
        prcp_list.append(prcp_dict)

    return jsonify(prcp_list)


@app.route("/api/v1.0/stations")
def stations():
   
    result=session.query(Measurement.station).group_by(Measurement.station).all()

    station_list = []
    for data in result:
        station_list.append(data)

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    
    results=session.query(Measurement.date,Measurement.tobs).filter('measurement.date >="2016-08-24" and measurement.date<="2017-08-23" and measurement.station="USC00519281"').all()
    
    tobs_list=[]
    
    for data in results:
        tobs_dict={}
        tobs_dict['date']=data[0]
        tobs_dict['tobs']=data[1]
        tobs_list.append(tobs_dict)
        
    return jsonify(tobs_list)
        
@app.route("/api/v1.0/<start_date>")
def start(start_date):
    def calc_temps(date):
        return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()

    
    start_dict={'TMIN':calc_temps(start_date)[0][0],
                'TAVE':calc_temps(start_date)[0][1],
                'TMAX':calc_temps(start_date)[0][2]}
    return jsonify(start_dict)

@app.route("/api/v1.0/<start_date>/<end_date>")
def end(start_date,end_date):
    def calc_temps(strt_date, e_date):
        return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date<=end_date).all()
    
    trip_dict={'TMIN':calc_temps(start_date,end_date)[0][0],
                'TAVE':calc_temps(start_date,end_date)[0][1],
                'TMAX':calc_temps(start_date,end_date)[0][2]}
    return jsonify(trip_dict)

if __name__ == '__main__':
    app.run(debug=True)
