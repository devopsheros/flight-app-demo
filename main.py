import random
import psycopg2, secrets, string, os
from flask import Flask,  render_template, request, session
from  datetime import datetime
from kubernetes import client, config
conn = psycopg2.connect(database=f"{os.environ['POSTGRES_DB']}", user=f"{os.environ['POSTGRES_USER']}", password=f"{os.environ['POSTGRES_PASSWORD']}", host=f"{os.environ['POSTGRES_HOST']}",port='5432')

cursor = conn.cursor()

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)


def create_tables():
  cursor.execute("""
                 CREATE TABLE states (
                   id SERIAL PRIMARY KEY,
                   state_code VARCHAR(2) NOT NULL,
                   state_name VARCHAR(50) NOT NULL
                 );
                """)
  conn.commit()

  cursor.execute("""
                   CREATE TABLE flights (
                     id SERIAL PRIMARY KEY,
                     departure_state VARCHAR(255),
                     arrival_state VARCHAR(255),
                     departure_time TIMESTAMP,
                     arrival_time TIMESTAMP,
                     price DECIMAL(10,2)
                     );
                   """)
  conn.commit()

  cursor.execute("""
                 CREATE TABLE tickets (
                   id SERIAL PRIMARY KEY,
                   ticket_number VARCHAR(10) NOT NULL,
                   departure VARCHAR(50) NOT NULL,
                   arrival VARCHAR(50) NOT NULL,
                   departure_time TIMESTAMP NOT NULL,
                   arrival_time TIMESTAMP NOT NULL,
                   ticket_price DECIMAL(10,2) NOT NULL,
                   users VARCHAR(50) NOT NULL
                   );
                 """)
  conn.commit()

  cursor.execute("""
                   CREATE TABLE users (
                     id SERIAL PRIMARY KEY,
                     name VARCHAR(50) NOT NULL,
                     password VARCHAR(50) NOT NULL,
                     email VARCHAR(50) NOT NULL
                     );
                   """)
  conn.commit()

  cursor.execute("""
                 INSERT INTO states(state_code,state_name)
                  VALUES
                  ('AL','Alabama'),
                  ('AK','Alaska'),
                  ('AZ','Arizona'),
                  ('AR','Arkansas'),
                  ('CA','California'),
                  ('CO','Colorado'),
                  ('CT','Connecticut'),
                  ('DC','District of Columbia'),
                  ('DE','Delaware'),
                  ('FL','Florida'),
                  ('GA','Georgia'),
                  ('HI','Hawaii'),
                  ('ID','Idaho'),
                  ('IL','Illinois'),
                  ('IN','Indiana'),
                  ('IA','Iowa'),
                  ('KS','Kansas'),
                  ('KY','Kentucky'),
                  ('LA','Louisiana'),
                  ('ME','Maine'),
                  ('MD','Maryland'),
                  ('MA','Massachusetts'),
                  ('MI','Michigan'),
                  ('MN','Minnesota'),
                  ('MS','Mississippi'),
                  ('MO','Missouri'),
                  ('MT','Montana'),
                  ('NE','Nebraska'),
                  ('NV','Nevada'),
                  ('NH','New Hampshire'),
                  ('NJ','New Jersey'),
                  ('NM','New Mexico'),
                  ('NY','New York'),
                  ('NC','North Carolina'),
                  ('ND','North Dakota'),
                  ('OH','Ohio'),
                  ('OK','Oklahoma'),
                  ('OR','Oregon'),
                  ('PA','Pennsylvania'),
                  ('RI','Rhode Island'),
                  ('SC','South Carolina'),
                  ('SD','South Dakota'),
                  ('TN','Tennessee'),
                  ('TX','Texas'),
                  ('UT','Utah'),
                  ('VT','Vermont'),
                  ('VA','Virginia'),
                  ('WA','Washington'),
                  ('WV','West Virginia'),
                  ('WI','Wisconsin'),
                  ('WY','Wyoming');
                  """)

  conn.commit()

  cursor.execute("""
                 INSERT INTO flights (departure_state, arrival_state, departure_time, arrival_time, price)
                  SELECT s1.state_name, s2.state_name,
                      (NOW() + INTERVAL '1 day' * FLOOR(RANDOM() * 30))::DATE + TIME '00:00:00' + INTERVAL '1 hour' * FLOOR(RANDOM() * 24),
                      (NOW() + INTERVAL '1 day' * FLOOR(RANDOM() * 30) + INTERVAL '1 day' + INTERVAL '1 hour' * FLOOR(RANDOM() * 24))::DATE + TIME '00:00:00' + INTERVAL '1 hour' * FLOOR(RANDOM() * 24),
                      CAST((RANDOM() * 500 + 50) AS NUMERIC(10,2))
                  FROM states s1
                  CROSS JOIN states s2
                  """)
  conn.commit()

  cursor.execute("""
                   UPDATE flights
                   SET arrival_time = departure_time, departure_time = arrival_time
                   WHERE arrival_time < departure_time;
                   """)
  conn.commit()


@app.route('/', methods = ['POST', 'GET'])
def sign_up_page():
  return render_template('sign-up.html')


@app.route('/sign-in', methods = ['POST', 'GET'])
def sign_in_page():
  return render_template('sign-in.html')



@app.route('/shop', methods = ['POST','GET'])
def shop_page():
  if request.method == 'POST':
    try:
      email = request.form['email']
    except:
      session['username'] = request.form['username']
      password = request.form['password']
      cursor.execute(f"SELECT password FROM users WHERE name = '{session['username']}'")
      real_password = cursor.fetchall()
      if real_password[0][0] == password:
        cursor.execute(f"SELECT departure,arrival,departure_time,arrival_time FROM tickets WHERE users = '{session['username']}'")
        user_existing_flights = cursor.fetchall()
        return render_template('shop.html', name = session['username'], flights = user_existing_flights)
      else:
        return render_template('wrong.html')
    else:
      session['username'] = request.form['username']
      password = request.form['password']
      cursor.execute(f"INSERT INTO users (name,password,email) VALUES ('{session['username']}','{password}','{email}')")
      conn.commit()
      return render_template('shop.html',name = session['username'])

@app.route('/ticket', methods = ['POST', 'GET'])
def ticket_page():
  if request.method == 'POST':
    try:
      departure = request.form['buy-departure']
      destination = request.form['buy-destination']
      cursor.execute(f"SELECT * FROM flights  WHERE  arrival_state = '{destination}' AND departure_state = '{departure}'")
      flight_match = cursor.fetchall()
      flight_array = []
      for i in range(len(flight_match)):
        flight_object =  {"departure": flight_match[i][1], "destination": flight_match[i][2], "departure_time": flight_match[i][3].strftime("%Y-%m-%d %H:%M"), "arrival_time": flight_match[i][4].strftime("%Y-%m-%d %H:%M"),"price" : f'{flight_match[i][5]}' }
        flight_array.append(flight_object)
      return render_template('ticket.html', available_flights = flight_array, action = 'buy')
    except:
      session['delete-departure'] = request.form['delete-departure']
      session['delete-destination'] = request.form['delete-destination']
      cursor.execute(f"SELECT * FROM tickets WHERE arrival = '{session['delete-destination']}' AND departure = '{session['delete-departure']}' AND users = '{session['username']}'")
      flight_match = cursor.fetchall()
      print(flight_match)
      return render_template('ticket.html', flight = flight_match, action = 'delete')

@app.route('/payment', methods = ['POST', 'GET'])
def purchase_page():
  if request.method == 'POST':
    session['global_user_departure'] = request.form['departure']
    session['global_user_destination'] = request.form['destination']
    session['global_user_departure_time'] = request.form['departure_time']
    session['global_user_arrival_time'] = request.form['arrival_time']
    session['global_price'] = request.form['price']
    return render_template('payment.html')


def generate_ticket_id():
  length = 10
  chars = string.ascii_lowercase + string.digits
  return ''.join(random.choice(chars) for _ in range(length))

@app.route('/success', methods = ['POST','GET'])
def success_page():
  if request.method == 'POST':
    ticket_id = generate_ticket_id()
    cursor.execute(f"INSERT INTO tickets (ticket_number,departure,arrival,departure_time,arrival_time,ticket_price,users) VALUES ('{ticket_id}','{session['global_user_departure']}','{session['global_user_destination']}','{session['global_user_departure_time']}','{session['global_user_arrival_time']}','{session['global_price']}','{session['username']}')" )
    conn.commit()
    return  render_template('success.html', ticket_id = ticket_id)

@app.route('/delete', methods = ['POST', 'GET'])
def delete_page():
  if request.method == 'POST':
    cursor.execute(f"SELECT ticket_number FROM tickets WHERE arrival = '{session['delete-destination']}' AND departure = '{session['delete-departure']}' AND users = '{session['username']}'")
    correct_ticket_id = cursor.fetchall()
    ticket_id = request.form['delete-ticket-id']
    if correct_ticket_id[0][0] == ticket_id:
      cursor.execute(f"DELETE FROM tickets WHERE ticket_number = '{ticket_id}'")
      conn.commit()
      return render_template('delete.html')
    else:
      return render_template('worng.html')

def check_configmap_exists(namespace, configmap_name):
  try:
    config.load_incluster_config()
    v1 = client.CoreV1Api()
    configmap = v1.read_namespaced_config_map(configmap_name, namespace)
    return True
  except:
    return False


def create_configmap(namespace, configmap_name, data):
  try:
    config.load_incluster_config()
    v1 = client.CoreV1Api()

    metadata = client.V1ObjectMeta(name=configmap_name)
    configmap = client.V1ConfigMap(data=data, metadata=metadata)

    v1.create_namespaced_config_map(namespace, configmap)
    print(f"ConfigMap '{configmap_name}' in namespace '{namespace}' created.")
  except client.rest.ApiException as e:
    raise RuntimeError(f"Failed to create ConfigMap: {e}")



namespace = "default"
configmap_name = "stop-table-creation"
data = { "key1": "value1" }
exists = check_configmap_exists(namespace, configmap_name)
if exists == False:
  create_configmap(namespace, configmap_name, data)
  create_tables()
else:
  print(f"ConfigMap '{configmap_name}' in namespace '{namespace}' already exists.")

app.run(host="0.0.0.0")
conn.close()
