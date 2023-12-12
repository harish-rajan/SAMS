from flask import Flask, render_template, request, redirect, url_for, flash
import pymysql.cursors

# Connect to the database
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='Kyjslja5',
                             db='flight_tracking',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

app = Flask(__name__)



@app.route('/home')
def home():
    return render_template("home.html")

@app.route('/airplanes')
def airplanes():
    try:
        with connection.cursor() as cursor:
            sql = "SELECT airlineid, tail_num, seat_capacity, speed, locationID, plane_type" \
                  ", skids, propellers, jet_engines FROM airplane"

            cols = ['airlineid', 'tail_num', 'seat_capacity', 'speed', 'locationID', 'plane_type', 'skids',
                    'propellers', 'jet_engines']
            cursor.execute(sql)
            items = cursor.fetchall()

            sql2 = "SELECT DISTINCT airlineID FROM airline"

            cursor.execute(sql2)
            airlines = cursor.fetchall()
            return render_template("airplanes.html", items=items, cols=cols, airlines=airlines, success='')
    except Exception as e:
        return render_template("airplanes.html", items=[], cols=[], success='Error: ' + str(e))

@app.route('/addairplaneReq', methods=['GET', 'POST'])
def add_airplane():
    airlineID = request.args.get('airlineID').strip()
    tail_num = request.args.get('tail_num').strip()
    seat_capacity = int(request.args.get('seat_capacity'))
    speed = int(request.args.get('speed'))
    locationID = request.args.get('locationID').strip()
    plane_type = request.args.get('plane_type').strip()
    skids = request.args.get('skids')
    if skids is not None: skids = 1
    propellers = request.args.get('propellers')
    if propellers is not None: propellers = int(propellers)
    jet_engines = request.args.get('jet_engines')
    if jet_engines is not None: jet_engines = int(jet_engines)

    try:
        cursor = connection.cursor()
        sql_proc = "call add_airplane(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        args = [airlineID, tail_num, seat_capacity, speed, locationID, plane_type, skids, propellers, jet_engines]
        cursor.execute(sql_proc, args)
        connection.commit()
        cursor.close()
        return redirect("/airplanes")
    except Exception as e:
        return redirect("/airplanes")
    
@app.route('/airports')
def airports():
    try:
        with connection.cursor() as cursor:
            sql = "SELECT airportID, airport_name, city, state, country, locationID FROM airport"

            cols = ['airportID', 'airport_name', 'city', 'state', 'country', 'locationID']
            cursor.execute(sql)
            items = cursor.fetchall()

            return render_template("airports.html", items=items, cols=cols, success='')
    except Exception as e:
        return render_template("airports.html", items=[], cols=[], success='Error: ' + str(e))

@app.route('/addAirportReq', methods=['GET', 'POST'])
def add_airport():
    airportID = request.args.get('airportID').strip()
    airport_name = request.args.get('airport_name').strip()
    city = request.args.get('city').strip()
    state = request.args.get('state').strip()
    country = request.args.get('country').strip()
    locationID = request.args.get('locationID').strip()

    try:
        cursor = connection.cursor()
        sql_proc = "call add_airport(%s, %s, %s, %s, %s, %s)"
        args = [airportID, airport_name, city, state, country, locationID]
        cursor.execute(sql_proc, args)
        connection.commit()
        cursor.close()
        return redirect("/airports")
    except Exception as e:
        return redirect("/airports")
    
@app.route('/people')
def people():
    try:
        with connection.cursor() as cursor:
            sql = "select t1.personID, t1.first_name, t1.last_name, case " \
                    "when t1.personID in (select personID from passenger) then 'passenger' " \
                    "when t1.personID in (select personID from pilot) then 'pilot' else null " \
                "end as role, t1.locationID, case " \
                    "when t2.airportID is not null then concat(t2.airport_name, ' (', t2.airportID, ')') " \
                    "when t3.tail_num is not null then concat(t3.airlineID, ' flight ', regexp_substr(t4.flightID,'[0-9]+')) " \
                    "else null end as location_name " \
            "from person t1 left join airport t2 on t1.locationID = t2.locationID " \
                "left join airplane t3 on t1.locationID = t3.locationID " \
                "left join flight t4 on t3.airlineID = t4.support_airline and t3.tail_num = t4.support_tail " \
            "order by convert(right(t1.personID, length(t1.personID) - 1), decimal)"

            cols = ['personID', 'first_name', 'last_name', 'role', 'locationID', 'location_name']
            cursor.execute(sql)
            items = cursor.fetchall()

            sql2 = "select locationID from location"
            cursor.execute(sql2)
            locations = cursor.fetchall()

            return render_template("people.html", items=items, cols=cols, locations=locations, success='')
    except Exception as e:
        return render_template("people.html", items=[], cols=[], success='Error: ' + str(e))
    
@app.route('/addPersonReq', methods=['GET'])
def add_persons():
    personID = request.args.get('personID').strip()
    first_name = request.args.get('first_name').strip()
    last_name = request.args.get('last_name').strip()
    locationID = request.args.get('locationID').strip()
    tax_ID = request.args.get('tax_ID')
    experience = request.args.get('experience')
    miles = request.args.get('miles')
    funds = request.args.get('funds')

    if request.args.get('passengerRole') == True:
        miles = int(miles)
        funds = int(funds)

    if request.args.get('pilotRole') == True:
        tax_ID = tax_ID.strip()
        experience = int(experience)
    

    try:
        with connection.cursor() as cursor:
            args = (personID, first_name, last_name, locationID, tax_ID,
                    experience, miles, funds)
            cursor.callproc('add_person', args)
            connection.commit()
            return redirect("/people")
    except Exception as e:
        return redirect("/people")
    
@app.route('/pilots')
def pilots():
    try:
        with connection.cursor() as cursor:
            sql = "select t1.personID, t2.first_name, t2.last_name, t1.taxID, t1.experience, concat(t3.support_airline, ' flight ', regexp_substr(t1.commanding_flight,'[0-9]+')) as commanding_flight " \
                "from pilot t1 join person t2 on t1.personID = t2.personID " \
                "left join flight t3 on t1.commanding_flight = t3.flightID " \
                "order by convert(right(t1.personID, length(t1.personID) - 1), decimal)"

            cols = ['personID', 'first_name', 'last_name', 'taxID', 'experience', 'commanding_flight']
            cursor.execute(sql)
            items = cursor.fetchall()
            return render_template("pilots.html", items=items, cols=cols, success='')
    except Exception as e:
        return render_template("pilots.html", items=[], cols=[], success='Error: ' + str(e))
    
@app.route('/pilots/<personID>/licenses')
def lisences(personID):
    try:
        with connection.cursor() as cursor:
            sql = f"select license from pilot_licenses where personID = '{personID}'"

            cols = ['license']
            cursor.execute(sql)
            items = cursor.fetchall()

            sql2 = f"select concat(first_name, ' ', last_name) as name from person where personID = '{personID}'"
            cursor.execute(sql2)
            name = list(cursor.fetchone().values())[0]

            return render_template("licenses.html", items=items, cols=cols, name=name, personID=personID, success='')
    except Exception as e:
        return render_template("licenses.html", items=[], cols=[], name="", personID="", success='Error: ' + str(e))
    
@app.route('/licenseReq', methods=['GET'])
def license():
    personID = request.args.get('personID').strip()
    license = request.args.get('license').strip()

    try:
        with connection.cursor() as cursor:
            args = (personID, license)
            cursor.callproc('grant_or_revoke_pilot_license', args)
            connection.commit()
            return redirect(f"/pilots/{personID}/licenses")
    except Exception as e:
        return redirect(f"/pilots/{personID}/licenses")
    
@app.route('/flights')
def flights():
    try:
        with connection.cursor() as cursor:
            sql = "select t1.support_airline, t1.flightID, t1.support_tail, t1.airplane_status, t1.routeID, t1.progress, " \
                "t3.departure, t3.arrival, t1.next_time, t1.cost " \
                "from flight t1 join route_path t2 on t1.routeID = t2.routeID and t1.progress = t2.sequence " \
                "join leg t3 on t2.legID = t3.legID"

            cols = ['support_airline', 'flightID', 'support_tail', 'airplane_status', 'routeID', 'progress', 'departure', 'arrival', 'next_time', 'cost']
            cursor.execute(sql)
            items = cursor.fetchall()
            return render_template("flights.html", items=items, cols=cols, success='')
    except Exception as e:
        return render_template("flights.html", items=[], cols=[], success='Error: ' + str(e))
    
## Harish Functions
    
@app.route('/')
def login():
    return render_template("index.html")

@app.route('/addAirplanes')
def add_airplanes_page():
    return render_template("add_airplanes.html", success='')



@app.route('/viewAirplanes')
def view_airplanes_page():
    try:
        with connection.cursor() as cursor:
            sql = "Select airplane.airlineid, tail_num, seat_capacity, speed,locationID,plane_type, " \
                  "skids,propellers,jet_engines FROM airplane " \
                  "JOIN airline  ON airplane.airlineid = airline.airlineid"

            cols = ['airlineid', 'tail_num', 'seat_capacity', 'speed', 'locationID', 'plane_type', 'skids',
                    'propellers', 'jet_engines']
            cursor.execute(sql)
            result = cursor.fetchall()
            return render_template("view_airplanes.html", items=result, cols=cols, success='')
    except Exception as e:
        return render_template("view_airplanes.html", items=[], cols=[], success='Can\'t view Airplane: ' + str(e))

@app.route('/airlineInfo', methods=['GET'])
def getairlineInfo():
    results1 = []
    d = {'airlineID': ''}
    results1.append(d)
    d = {'locationID': ''}
    results1.append(d)

    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM airline"
            cursor.execute(sql)
            result1 = cursor.fetchall()
            for r in result1:
                d = {'airlineID': r.get('airlineID')}
                results1.append(d)
            cursor.close()

        with connection.cursor() as cursor:
            sql1 = "SELECT l.locationID FROM location l LEFT JOIN airplane a ON l.locationID = a.locationID where a.locationID IS NOT NULL"
            cursor.execute(sql1)
            result2 = cursor.fetchall()
            cursor.close()

            results1.extend(result2)
            cols = ['airlineID', 'locationID']

            return render_template("add_airplanes.html", items=results1, cols=cols, success='')
    except Exception as e:
        return render_template("add_airplanes.html", items=[], cols=[], success='Can\'t get airlines: ' + str(e))


# @app.route('/')
# def index():
#     try:
#         with connection.cursor() as cursor:
#             sql = "SELECT DISTINCT airlineID,revenue FROM airline"
#             cols = ['airlineID', 'revenue']
#             cursor.execute(sql)
#             airplanelist = cursor.fetchall()
#             return render_template('add_airplanes.html', airplanelist=airplanelist,content_type='application/json')
#     except Exception as e:
#         return render_template('add_airplanes.html', items=[], cols=[], success='Can\'t view Airplane: ' + str(e))

@app.route('/homeAdmin')
def home_admin():
    return render_template("home_admin.html")


@app.route('/homeUser')
def home_user():
    return render_template("home_user.html")



@app.route('/addPersons')
def add_persons_page():
    return render_template("add_persons.html", success='')

@app.route('/addAirlines')
def add_airlines_page():
    return render_template("add_airlines.html", success='')


@app.route('/addLocations')
def add_locations_page():
    return render_template("add_locations.html", success='')


@app.route('/addFlights')
def add_flights_page():
    return render_template("add_flights.html", success='')


@app.route('/addTopics')
def add_topics_page():
    return render_template("add_topics.html", success='')


@app.route('/addLocationReq', methods=['GET'])
def add_location():
    locationID = request.args.get('locationID').strip()
    if locationID == '':
        return render_template("add_location.html", success='locationID cannot be empty')
    try:
        with connection.cursor() as cursor:
            # sql = "INSERT INTO `flight_tracking`.`airline` (`airlineID`,`revenue`) VALUES (%s, %s)"
            # cursor.execute(sql, (airlineid, revenue))
            # return render_template("add_airlines.html", success='Successful')

            sql = "INSERT INTO location(locationID) VALUES (%s)"
            val = (locationID)

            cursor.execute(sql, val)
            connection.commit()
            return render_template("add_locations.html", success='Successful')

            print(cursor.rowcount, "location details inserted")

            # disconnecting from server
            connection.close()

    except Exception as e:
        return render_template("add_locations.html", success='Can\'t add Location: ' + str(e))


@app.route('/addFlightReq', methods=['GET'])
def add_flights():
    flightID = request.args.get('flightID').strip()
    routeID = request.args.get('routeID').strip()
    support_airline = request.args.get('support_airline').strip()
    support_tail = request.args.get('support_tail').strip()
    progress = request.args.get('progress').strip()
    airplane_status = request.args.get('airplane_status').strip()
    next_time = request.args.get('next_time').strip()
    cost = request.args.get('cost').strip()
    if flightID == '':
        return render_template("add_flights.html", success='flightID cannot be empty')
    try:
        with connection.cursor() as cursor:
            # sql = "INSERT INTO `flight_tracking`.`airline` (`airlineID`,`revenue`) VALUES (%s, %s)"
            # cursor.execute(sql, (airlineid, revenue))
            # return render_template("add_airlines.html", success='Successful')

            sql = "INSERT INTO flight (flightID, routeID, support_airline, support_tail, progress, " \
                  " airplane_status, next_time,cost) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"

            val = (flightID, routeID, support_airline, support_tail, progress, airplane_status, next_time, cost)

            cursor.execute(sql, val)
            connection.commit()
            return render_template("add_flights.html", success='Successful')

            print(cursor.rowcount, "flight details inserted")

            # disconnecting from server
            connection.close()

    except Exception as e:
        return render_template("add_flights.html", success='Can\'t add flight: ' + str(e))


@app.route('/addAirlineReq', methods=['GET'])
def add_airline():
    airlineid = request.args.get('airlineid').strip()
    revenue = request.args.get('revenue').strip()
    if airlineid == '' or revenue == '':
        return render_template("add_airlines.html", success='AirlineID or Revenue cannot be empty')
    try:
        with connection.cursor() as cursor:
            # sql = "INSERT INTO `flight_tracking`.`airline` (`airlineID`,`revenue`) VALUES (%s, %s)"
            # cursor.execute(sql, (airlineid, revenue))
            # return render_template("add_airlines.html", success='Successful')

            sql = "INSERT INTO airline (airlineID, revenue) VALUES (%s, %s)"
            val = (airlineid, revenue)

            cursor.execute(sql, val)
            connection.commit()
            return render_template("add_airlines.html", success='Successful')

            print(cursor.rowcount, "airline details inserted")

            # disconnecting from server
            connection.close()

    except Exception as e:
        return render_template("add_airlines.html", success='Can\'t add Airline: ' + str(e))





@app.route('/updateAirlines')
def update_airlines_page():
    return render_template("update_airlines.html", success='')


@app.route('/updateAirlineReq', methods=['GET'])
def update_airline():
    airlineid = request.args.get('airlineid').strip()
    # old_revenue = request.args.get('old_revenue').strip()
    # new_airlineid = request.args.get('new_airlineid').strip()
    new_revenue = request.args.get('new_revenue').strip()
    if airlineid == '' or new_revenue == '':
        return render_template("update_airlines.html", success='Fields cannot be empty')
    try:
        with connection.cursor() as cursor:
            sql = "UPDATE airline SET revenue = %s WHERE airlineid =%s"
            val = (new_revenue, airlineid)
            cursor.execute(sql, val)
            connection.commit()
            return render_template("update_airlines.html", success='Successful')
    except Exception as e:
        return render_template("update_airlines.html", success='Can\'t update Airline: ' + str(e))


@app.route('/recycleCrew')
def recycle_crew_1_page():
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM flight"
            cols = ['airplane_status', 'flightID', 'next_time', 'progress', 'routeID', 'support_airline',
                    'support_tail']
            cursor.execute(sql)
            result = cursor.fetchall()
            cursor.close()
            return render_template("recycle_crew.html", items=result, cols=cols, success='')
    except Exception as e:
        return render_template("recycle_crew.html", items=[], cols=[], success='Can\'t view Recycle Crew: ' + str(e))


@app.route('/recycleCrew2', methods=['GET'])
def recycle_crew_2_page():
    flightID = request.args.get('option').strip()

    try:
        cursor = connection.cursor()
        sql_proc = "call flight_tracking.recycle_crew(%s)"
        args = [flightID]
        # args = ['am_99']
        cursor.execute(sql_proc, args)
        connection.commit()
        cursor.close()
        return render_template("confirmation.html", items=[], cols=[], success='Completed')
    except Exception as e:
        return render_template("confirmation.html", items=[], cols=[], success='Can\'t view Recycle Crew: ' + str(e))


@app.route('/viewLocations')
def view_locations_page():
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM `location`"
            cols = ['locationID']
            cursor.execute(sql)
            result = cursor.fetchall()
            return render_template("view_locations.html", items=result, cols=cols, success='')
    except Exception as e:
        return render_template("view_locations.html", items=[], cols=[], success='Can\'t view Locations: ' + str(e))


@app.route('/viewFlights')
def view_flights_page():
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM flight"
            cols = ['flightID', 'routeID', 'support_airline', 'support_trail', 'progress', 'airplane_status',
                    'next_time', 'cost']
            cursor.execute(sql)
            result = cursor.fetchall()
            return render_template("view_flights.html", items=result, cols=cols, success='')
    except Exception as e:
        return render_template("view_flights.html", items=[], cols=[], success='Can\'t view Flights: ' + str(e))


@app.route('/viewAirline')
def view_airline_page():
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM `airline`"
            cols = ['airlineID', 'revenue']
            cursor.execute(sql)
            result = cursor.fetchall()
            return render_template("view_airline.html", items=result, cols=cols, success='')
    except Exception as e:
        return render_template("view_airline.html", items=[], cols=[], success='Can\'t view Airline: ' + str(e))

@app.route('/viewPersons')
def view_persons_page():
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM person"
            cols = ['personID', 'first_name', 'last_name', 'locationID']
            cursor.execute(sql)
            result = cursor.fetchall()
            return render_template("view_persons.html", items=result, cols=cols, success='')
    except Exception as e:
        return render_template("view_persons.html", items=[], cols=[], success='Can\'t view Persons: ' + str(e))
    
@app.route('/viewPilots')
def view_pilots_page():
    try:
        with connection.cursor() as cursor:
            sql = "SELECT t2.first_name, t2.last_name, t1.taxID, t1.experience, t1.commanding_flight FROM pilot t1 JOIN person t2 ON t1.personID = t2.personID"
            cols = ['first_name', 'last_name', 'taxID', 'experience', 'commanding_flight']
            cursor.execute(sql)
            result = cursor.fetchall()
            return render_template("view_pilots.html", items=result, cols=cols, success='')
    except Exception as e:
        return render_template("view_pilots.html", items=[], cols=[], success='Can\'t view Pilots: ' + str(e))
    


if __name__ == '__main__':
    app.run()
