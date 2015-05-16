from bs4 import BeautifulSoup
import requests
from datetime import datetime
import calendar


def scrape():
    base_req = "http://www.wunderground.com/history/airport/KNYC/2013/{1}/{0}/DailyHistory.html?req_city=NA&req_state=NA&req_statename=NA&MR=1"

    #helper functions to obtain cell contents
    raw = lambda cTag: str(cTag.getText().strip())
    null_check = lambda cTag: None if cTag in ['N/A','N/A%', '-', ''] else cTag
    float_conv = lambda cTag: None if not null_check(cTag) else float(cTag)
    perc_conv = lambda cTag: None if not null_check(raw(cTag)) else int(raw(cTag).replace('%', ''))

    time_cell = lambda cTag: datetime.strptime(date_str+raw(cTag), '%Y-%m-%d %I:%M %p') 
    value_cell = lambda cTag: None if len(cTag.findAll('span', {"class","wx-value"}))==0 else float_conv(raw(cTag.findAll('span', {"class","wx-value"})[0])) #float value contained in the cell
    perc_cell = lambda cTag: None if not null_check(raw(cTag)) else perc_conv(cTag) #percentage value 
    str_cell = lambda cTag: None if null_check(raw(cTag)) is None else raw(cTag).replace('\n', '').replace('\t', '_').replace(',', '')

    header_str = ["time(est)","temp_C","dew_point","humidity_%", "pressure_hPa", "visibility_km", "wind_dir", "wind_speed_kmh", "gust_speed_kmh", "precipitation_mm", "events", "conditions"]
    for month in range(1, 13):
        for day in range(1, calendar.monthrange(2013, month)[1]+1):

            print day, month

            date_str = "2013-"+str(month)+"-"+str(day)+" "
            req_str = base_req.format(day,month)
            r = requests.get(req_str)  #obtain html page

            data = [header_str]

            if r.status_code == 200: #no pagination on this site
                content = r.text
                soup = BeautifulSoup(content)
                rows = soup.findAll("div", { "id" : "observations_details" })[0].findAll("tbody")[0].findAll("tr")

                for i, row in enumerate(rows):
                    cells = row.findAll("td")

                    assert len(cells)== 12 or len(cells)== 13
                    
                    time = time_cell(cells[0])
                    temp = value_cell(cells[1]) #in celsius
                    dew = value_cell(cells[-10])
                    humidity = perc_cell(cells[-9])
                    pressure = value_cell(cells[-8]) #in hPa
                    visibility = value_cell(cells[-7])
                    wind_dir = str_cell(cells[-6])
                    wind_speed = value_cell(cells[-5]) #in kmh
                    gust_speed = value_cell(cells[-4])
                    precip = value_cell(cells[-3])
                    events = str_cell(cells[-2])
                    conditions = str_cell(cells[-1])


                    data.append([time, temp, dew, humidity, pressure, visibility, wind_dir, wind_speed, gust_speed, precip, events, conditions])
                
                f = open("/Users/bubica/Development/CODE/PROJECTS/InsightDataScience2014/Project/data/weather_2013/weather_nyc_KNYC_2013_"+str(month)+"_"+str(day)+".csv", "w")
                #NOTE: I had some problems with the csv module when loading data into sql db, so I resorted to manually writing records into the csv file
                for record in data:
                    for i in record:
                        f.write(str(i)+",")
                    f.write("\n")
                f.close()
                    

