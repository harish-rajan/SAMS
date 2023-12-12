from flask import Flask, render_template, request, redirect, url_for, flash
import pymysql.cursors

# Connect to the database
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='',
                             db='flight_tracking',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

app = Flask(__name__)


@app.route('/')
def login():
    return render_template("index.html")


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


@app.route('/addAirplanes')
def add_airplanes_page():
    return render_template("add_airplanes.html", success='')

@app.route('/addPersons')
def add_persons_page():
    return render_template("add_persons.html", success='')

@app.route('/addRoutes')
def add_routes_page():
    return render_template("add_routes.html", success='')

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

@app.route('/simulationCycle')
def simulationCycle_page():
    return render_template("simulation_cycle.html", success='')

@app.route('/addPassengers')
def add_passengers_page():
  return render_template("add_passengers.html", success='')

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


@app.route('/addAirports', methods=['GET'])
def getlocationinfo():
    try:
        with connection.cursor() as cursor:
            sql = "select * from location"
            cols = ['locationID']
            cursor.execute(sql)
            result = cursor.fetchall()
            cursor.close()
            return render_template("add_airports.html", items=result, cols=cols, success='')
    except Exception as e:
        return render_template("add_airports.html", items=[], cols=[], success='Can\'t get locations: ' + str(e))

@app.route('/addAirportReq', methods=['GET'])
def add_airport_req():
    airportID = request.args.get('airportID')
    airport_name = request.args.get('airport_name')
    city = request.args.get('city')
    state = request.args.get('state')
    locationID = request.args.get('option2')
    country = request.args.get('country')
    try:
        if not airportID or not airportID.strip():
            return render_template("add_airports.html", success='airportID  cannot be empty')
        if not airport_name or not airport_name.strip():
            return render_template("add_airports.html", success='airport_name cannot be empty')
        if not city or not city.strip():
            return render_template("add_airports.html", success='city  cannot be empty')
        if not state or not state.strip():
            return render_template("add_airports.html", success='state cannot be empty')
        # if not locationID or not locationID.strip():
        #     return render_template("add_airports.html", success='locationID  cannot be empty')
        if not country or not country.strip():
            return render_template("add_airports.html", success='country  cannot be empty')

        cursor = connection.cursor()

        sql_proc = "call add_airport(%s, %s, %s, %s, %s, %s)"
        args = [airportID.strip(), airport_name.strip(), city.strip(), state.strip(), country.strip(),
                locationID.strip()]
        cursor.execute(sql_proc, args)
        connection.commit()
        cursor.close()
        return render_template("add_airports.html", items=[], cols=[], success='Completed')
    except Exception as e:
        return render_template("add_airports.html", success='Can\'t add airport: ' + str(e))

@app.route('/simulationcycleReq')
def simulationcycleReq_page():
    try:
        cursor = connection.cursor()
        sql_proc = "call flight_tracking.simulation_cycle()"
        cursor.execute(sql_proc)
        connection.commit()
        cursor.close()
        return render_template("simulation_cycle.html", items=[], cols=[], success='Completed')
    except Exception as e:
        return render_template("simulation_cycle.html", items=[], cols=[], success='Can\'t Simulate: ' + str(e))
@app.route('/addpersonflightInfo', methods=['GET'])
def getpersonflightInfo():
    results1 = []
    d = {'personID': ''}
    results1.append(d)
    d = {'flightID': ''}
    results1.append(d)

    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM person"
            cursor.execute(sql)
            result1 = cursor.fetchall()
            for r in result1:
                d = {'personID': r.get('personID')}
                results1.append(d)
            cursor.close()

        with connection.cursor() as cursor:
            sql1 = "SELECT DISTINCT flightID FROM flight"
            cursor.execute(sql1)
            result2 = cursor.fetchall()
            cursor.close()

            results1.extend(result2)
            cols = ['personID', 'flightID']

            return render_template("assign_pilot.html", items=results1, cols=cols, success='')
    except Exception as e:
        return render_template("assign_pilot.html", items=[], cols=[], success='Can\'t get person flight Info: ' + str(e))

@app.route('/assignpilotReq', methods=['GET'])
def add_assignpilot_req():
    personID = request.args.get('option1')
    flightID = request.args.get('option2')

    try:
        if not personID or not personID.strip():
            return render_template("assign_pilot.html", success='personID  cannot be empty')
        if not flightID or not flightID.strip():
            return render_template("assign_pilot.html", success='flightID cannot be empty')

        cursor = connection.cursor()

        sql_proc = "call assign_pilot(%s, %s)"
        args = [personID.strip(), flightID.strip()]
        cursor.execute(sql_proc, args)
        connection.commit()
        cursor.close()
        return render_template("assign_pilot.html", items=[], cols=[], success='Completed')
    except Exception as e:
        return render_template("assign_pilot.html", success='Can\'t assign pilot: ' + str(e))


@app.route('/addPassengerReq', methods=['GET'])
def add_passengers():
    passengerID = request.args.get('passengerID')
    miles = int(request.args.get('miles'))
    funds = int(request.args.get('funds'))

    if passengerID == '':
        return render_template("add_passengers.html", success='passengerID cannot be empty')
    if miles == '':
        return render_template("add_passengers.html", success='miles cannot be empty')
    if funds == '':
        return render_template("add_passengers.html", success='funds cannot be empty')
    try:
        with connection.cursor() as cursor:
            cursor = connection.cursor()
            sql_proc = "call add_passenger(%s, %s, %s)"
            args = [passengerID, miles, funds]
            cursor.execute(sql_proc, args)
            connection.commit()
            cursor.close()


            return render_template("add_passengers.html", success='Successful')

            print(cursor.rowcount, "passenger details inserted")

            # disconnecting from server
            connection.close()

    except Exception as e:
        return render_template("add_passengers.html", success='Can\'t add Passenger: ' + str(e))

@app.route('/addRouteReq', methods=['GET'])
def add_routes():
    routeID = request.args.get('routeID').strip()
    if routeID == '':
        return render_template("add_passengers.html", success='routeID cannot be empty')

    try:
        with connection.cursor() as cursor:
            # sql = "INSERT INTO `flight_tracking`.`airline` (`airlineID`,`revenue`) VALUES (%s, %s)"
            # cursor.execute(sql, (airlineid, revenue))
            # return render_template("add_airlines.html", success='Successful')

            sql = "INSERT INTO route(routeID) VALUES (%s)"
            val = (routeID)

            cursor.execute(sql, val)
            connection.commit()
            return render_template("add_routes.html", success='Successful')

            print(cursor.rowcount, "route details inserted")

            # disconnecting from server
            connection.close()

    except Exception as e:
        return render_template("add_routes.html", success='Can\'t add Routess: ' + str(e))

@app.route('/getlicenseInfo', methods=['GET'])
def getlicensetypeinfo():
    results1 = []
    d = {'personID': ''}
    results1.append(d)
    d = {'license': ''}
    results1.append(d)

    try:
        with connection.cursor() as cursor:
            sql = "SELECT DISTINCT personID FROM person"
            cursor.execute(sql)
            result1 = cursor.fetchall()
            for r in result1:
                d = {'personID': r.get('personID')}
                results1.append(d)
            cursor.close()

        with connection.cursor() as cursor:
            sql1 = "SELECT DISTINCT license FROM pilot_licenses"
            cursor.execute(sql1)
            result2 = cursor.fetchall()
            cursor.close()

            results1.extend(result2)
            cols = ['license', 'license']

            return render_template("grantrevokelicense.html", items=results1, cols=cols, success='')
    except Exception as e:
        return render_template("grantrevokelicense.html", items=[], cols=[], success='Can\'t get person and license: ' + str(e))
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

@app.route('/grantrevokelicensereq', methods=['GET'])
def get_grantrevokelicense():
    personID = request.args.get('option1').strip()
    licenseID = request.args.get('option2').strip()
    try:
        cursor = connection.cursor()
        sql_proc = "call flight_tracking.grant_or_revoke_pilot_license(%s,%s)"
        args = [personID, licenseID]
        # args = ['am_99']
        cursor.execute(sql_proc, args)
        connection.commit()
        cursor.close()
        return render_template("grantrevokelicense.html", items=[], cols=[], success='Completed')
    except Exception as e:
        return render_template("grantrevokelicense.html", items=[], cols=[], success='Can\'t grant license: ' + str(e))

@app.route('/airflightinfo', methods=['GET'])
def getflightinfo():
    results1 = []
    d = {'flightID': ''}
    results1.append(d)

    try:

        with connection.cursor() as cursor:
            sql1 = "SELECT flightID from flight"
            cursor.execute(sql1)
            result2 = cursor.fetchall()
            cursor.close()
            results1.extend(result2)
            cols = ['flightID']

            return render_template("retire_flight.html", items=results1, cols=cols, success='')
    except Exception as e:
        return render_template("retire_flight.html", items=[], cols=[], success='Can\'t get flights: ' + str(e))


@app.route('/retireFlightReq', methods=['GET'])
def retireFlightReq_page():
    flightID = request.args.get('option2').strip()

    try:
        cursor = connection.cursor()
        sql_proc = "call flight_tracking.retire_flight(%s)"
        args = [flightID]
        # args = ['am_99']
        cursor.execute(sql_proc, args)
        connection.commit()
        cursor.close()
        return render_template("retire_flight.html", items=[], cols=[], success='Completed')
    except Exception as e:
        return render_template("retire_flight.html", items=[], cols=[], success='Can\'t retire flight: ' + str(e))

@app.route('/addairplaneReq', methods=['GET', 'POST'])
def add_airplane():
    airlineID = request.args.get('option1').strip()
    tail_num = request.args.get('tail_num').strip()
    seat_capacity = int(request.args.get('seat_capacity').strip())
    speed = int(request.args.get('speed').strip())
    locationID = request.args.get('option2').strip()
    plane_type = request.args.get('plane_type').strip()
    skids = int(request.args.get('skids').strip())
    propeller = int(request.args.get('propeller').strip())
    jetengines = int(request.args.get('jetengines').strip())

    try:
        cursor = connection.cursor()
        #sql_proc = "call add_airplane(%s, %s, %d, %d, %s, %s, %d, %d, %d )"
        sql_proc = "call add_airplane(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        args = [airlineID, tail_num, seat_capacity, speed, locationID, plane_type, skids, propeller, jetengines]
        cursor.execute(sql_proc, args)
        connection.commit()
        cursor.close()
        return render_template("add_airplanes.html", items=[], cols=[], success='Completed')
    except Exception as e:
        return render_template("add_airplanes.html", success='Can\'t add airplane: ' + str(e))


@app.route('/addPersonReq', methods=['GET'])
def add_persons():
    personID = request.args.get('personID')
    first_name = request.args.get('first_name')
    last_name = request.args.get('last_name')
    locationID = request.args.get('locationID')
    tax_ID = request.args.get('tax_ID')
    experience = request.args.get('experience')
    miles = request.args.get('miles')
    funds = request.args.get('funds')

    if not personID or not personID.strip():
        return render_template("add_persons.html", success='personID cannot be empty')
    if not first_name or not first_name.strip():
        return render_template("add_persons.html", success='first_name cannot be empty')
    if not last_name or not last_name.strip():
        return render_template("add_persons.html", success='last_name cannot be empty')
    if not locationID or not locationID.strip():
        return render_template("add_persons.html", success='locationID cannot be empty')
    # if not tax_ID or not tax_ID.strip():
    # return render_template("add_persons.html", success='tax_ID cannot be empty')
    # if not experience or not experience.strip():
    # return render_template("add_persons.html", success='experience cannot be empty')
    if not miles or not miles.strip():
        return render_template("add_persons.html", success='miles cannot be empty')
    if not funds or not funds.strip():
        return render_template("add_persons.html", success='funds cannot be empty')

    try:
        with connection.cursor() as cursor:
            args = (personID.strip(), first_name.strip(), last_name.strip(), locationID.strip(), None,
                    None, miles.strip(), funds.strip())
            cursor.callproc('add_person', args)
            connection.commit()
            return render_template("add_persons.html", success='Successful')
    except Exception as e:
        return render_template("add_persons.html", success='Can\'t add Persons: ' + str(e))

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

@app.route('/viewPassengers')
def view_passengers_page():
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM `passenger`"
            cols = ['passengerID', 'miles', 'funds']
            cursor.execute(sql)
            result = cursor.fetchall()
            return render_template("view_passengers.html", items=result, cols=cols, success='')
    except Exception as e:
        return render_template("view_passengers.html", items=[], cols=[], success='Can\'t view Passengers: ' + str(e))

@app.route('/viewRoutes')
def view_routes_page():
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM `route`"
            cols = ['routeID']
            cursor.execute(sql)
            result = cursor.fetchall()
            return render_template("view_routes.html", items=result, cols=cols, success='')
    except Exception as e:
        return render_template("view_routes.html", items=[], cols=[], success='Can\'t view Routes: ' + str(e))

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


@app.route('/viewflightsInair')
def view_flightsinair_page():
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM flights_in_the_air"
            cols = ['departing_from', 'arriving_at', 'num_flights', 'flight_list', 'earliest_arrival',
                    'latest_arrival', 'airplane_list']
            cursor.execute(sql)
            result = cursor.fetchall()
            return render_template("view_flightsinair.html", items=result, cols=cols, success='')
    except Exception as e:
        return render_template("view_flightsinair.html", items=[], cols=[], success='Can\'t view Flights In air: ' + str(e))


@app.route('/viewflightsonGround')
def view_flightsonground_page():
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM flights_on_the_ground"
            cols = ['departing_from', 'num_flights', 'flight_list', 'earliest_arrival',
                    'latest_arrival', 'airplane_list']
            cursor.execute(sql)
            result = cursor.fetchall()
            return render_template("view_flightsonground.html", items=result, cols=cols, success='')
    except Exception as e:
        return render_template("view_flightsonground.html", items=[], cols=[], success='Can\'t view Flights: ' + str(e))


@app.route('/viewpassengersonGround')
def view_passengersonground_page():
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM people_on_the_ground"
            cols = ['departing_from', 'airport', 'airport_name', 'city',
                    'state', 'country', 'num_pilots', 'num_passengers', 'joint_pilots_passengers', 'person_list']
            cursor.execute(sql)
            result = cursor.fetchall()
            return render_template("view_passengersonground.html", items=result, cols=cols, success='')
    except Exception as e:
        return render_template("view_passengersonground.html", items=[], cols=[], success='Can\'t view Passengers on Ground: ' + str(e))


@app.route('/viewpassengersinair')
def view_passengersinair_page():
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM people_in_the_air"
            cols = ['departing_from', 'arriving_at', 'num_airplanes', 'airplane_list',
                    'flight_list', 'earliest_arrival', 'latest_arrival', 'num_pilots', 'num_passengers', 'joint_pilots_passengers', 'person_list']
            cursor.execute(sql)
            result = cursor.fetchall()
            return render_template("view_passengersinair.html", items=result, cols=cols, success='')
    except Exception as e:
        return render_template("view_passengersinair.html", items=[], cols=[], success='Can\'t view Passengers on Ground: ' + str(e))

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

if __name__ == '__main__':
    app.run()
