from flask import render_template, flash, redirect, jsonify, request, make_response
from flask import Response
from web import flask_app as app
import math
import calendar
import pandas as pd
import json

import web_trip_predictor as predictor
from app.trends.hub import traffic



@app.route('/')
@app.route('/index')
def intro():
    #Renders initial page
    return render_template('Taxi_Intro.html', err_msg = "")   


# *************************** ANIMATION ********************************

@app.route('/data_anim/')
def data_anim():
    return render_template('Data_Animation.html')  


@app.route('/data_anim_fetch/', methods=['GET','POST'])
def data_anim_data_fetch():

    #Fetching the data to animate

    errd = {"errMsg": ""}
    
    month_str = str.lower(str(request.args.get('month'))).strip().capitalize()
    day_str = str.lower(str(request.args.get('day'))).strip().capitalize()
    hour_str = str.lower(str(request.args.get('hour'))).strip().capitalize()
    pick_drop_str = str.lower(str(request.args.get('pick_drop'))).strip()
    
    
    month = None
    hour = None
    day = None
    gr_el = None

    if hour_str:
        hour = int(hour_str)
    if day_str:
        day = list(calendar.day_name).index(day_str)
    if month_str:
        month = list(calendar.month_name).index(month_str)

    print
    print month
    print day
    print hour
    print pick_drop_str
    print 

    #load the visualisation data
    vis_dir = app.static_folder + '/visualisation_data/'
    vis_fname = vis_dir + ('hub_occupancy_pickup.csv' if pick_drop_str=='pick' else 'hub_occupancy_dropoff.csv')

    print vis_fname
    if hour is None:
        #Display hourly trends
        print "Hourly trends"
        vis_data = traffic.eventsPerHour(fname = vis_fname, month=month, dow=day)
        gr_el = "hour"

    elif day is None:
        print "Dayly trends", month, hour
        vis_data = traffic.eventsPerDay(fname = vis_fname, month=month, hour=hour)
        gr_el = "day"

    elif month is None:
        print "Monthly trends"
        vis_data = traffic.eventsPerMonth(fname = vis_fname, dow=day, hour=hour)
        gr_el = "month"


    else:
        # All params set - no animation just display static data
        vis_data = traffic.eventsPerHour(fname = vis_fname, month=month, dow=day)
        vis_data = vis_data[vis_data.hour == hour]
        gr_el = "hour"

        max_count_abs = traffic.eventsPerHour(vis_fname, month=month, dow=day)['count'].max()

    #computing the size of the circle around the each hub
    def _hub_radius(trend):
        """ Size of the circle of around the hub is proportional to the total count of pickups (with some scaling factor) """
        """ Implementing a closure function to evaluate the size of the radius around hub """
        if trend =='hour':
            mx_ratio = 1.
        else:
            tot_data = traffic.eventsPerHour(vis_fname)
            mx1 = tot_data['count'].max()
            mx2 = tot_data[tot_data.hour == hour]['count'].max()
            mx_ratio = mx2/(1.*mx1)

        max_count_abs = vis_data['count'].max() #max count in the visualisation dataset
        return lambda count: 90 * mx_ratio * math.sqrt(count / max_count_abs) #for each count, return the radius of this hub so that the are will be proportional to the count

    rad_func = _hub_radius(gr_el)

    #Convert to gjson
    hres = {}
    gr = vis_data.groupby(gr_el)
    for hi, df in gr:
        
        res = []

        for _, di in df.iterrows():

            coord = [di['long'], di['lat']]
            radius = rad_func(di['count']) 

            gjson = { "type": "Feature", 
            "properties": {"sz": radius}, 
            "geometry": {"type": "Point", "coordinates": coord}
            }

            res.append(gjson)

        hres["h%02d"%hi] = res

    output = {}
    output["trend"] = gr_el.capitalize()
    output["data"] = hres

    #Format info label
    info_str = "Displaying average number of taxi {0}s"
    info_str = info_str.format("pick up" if pick_drop_str =='pick' else "drop off")    
    info_str += (" on " + day_str) if day_str else ""
    info_str += (" in " + month_str) if month_str else "" 
    if len(hres)<=1:
        info_str +="<br/><br/>You need to set at least one paramteter to 'Show All' to animate the trend." 

    output['info'] = info_str 
    return Response(json.dumps(output),  mimetype='application/json') #dict where each element has a 

@app.route('/slides/')
def slidesPage():
    #Renders initial page
    return render_template('Slides.html')   

@app.route('/est/', methods=['GET'])
def est():

    str_start_p = request.args.get('start_p')
    str_end_p = request.args.get('end_p')
    str_time_p = request.args.get('time_p')
    str_date_p = request.args.get('date_p')

    print 
    print str_date_p
    print str_time_p
    print
    
    est = predictor.get_est(str_start_p, str_end_p, str_time_p, str_date_p)
    errMsg = est[-1]

    if errMsg is None:

        #Return the result
        time_est = int(round(est[0], 0))
        walk_est = est[2]
        fare_est = est[1]
        origin_addr = est[3]
        dest_addr = est[4]

        return render_template('Taxi_Est.html', dur_est = str(time_est), walk_est=str(walk_est), fare_est=str(fare_est), origin_addr = origin_addr, dest_addr = dest_addr, err_msg = "")
    else: 
        return render_template('Taxi_Intro.html', err_msg = str(est[-1]))

