import uuid

from flask import Flask
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import request
from psycopg2.sql import SQL, Literal
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.json.ensure_ascii = False

connection = psycopg2.connect(
    host=os.getenv('POSTGRES_HOST') if os.getenv('DEBUG_MODE') == 'false' else 'localhost',
    port=os.getenv('POSTGRES_PORT'),
    database=os.getenv('POSTGRES_DB'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    cursor_factory=RealDictCursor
)
connection.autocommit = True


@app.get("/couriers")
def get_couries():
    query = """
with
  couries_with_deliveries as (
	select
	  c.id,
	  c.first_name,
      c.last_name,
	  c.phone,
	  c.vehicle,
      c.bag_volume,
	  coalesce(jsonb_agg(jsonb_build_object(
	    'id', d.id, 'title', d.title, 'phone', d.phone))
	      filter (where d.id is not null), '[]') as deliveries
	from delivery_crud.courier c
	left join delivery_crud.courier_delivery cd on cd.courier_id = c.id
	left join delivery_crud.delivery d on d.id = cd.delivery_id
	group by c.id
  ),
  couriers_with_orders as (
	select
	  c.id,
	  coalesce(json_agg(json_build_object(
	    'id', uo.id, 'address', uo.address, 'status', uo.status))
	      filter (where uo.id is not null), '[]')
	        as user_orders
	from delivery_crud.courier c
	left join delivery_crud.user_order uo on uo.courier_id = c.id
	group by c.id
  )
select cwd.id, cwd.first_name, cwd.last_name, cwd.phone, cwd.vehicle, cwd.bag_volume, deliveries, user_orders
from couries_with_deliveries cwd
join couriers_with_orders cwo on cwo.id = cwd.id
"""

    with connection.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()

    return result


@app.post('/couriers')
def create_courier():
    body = request.json

    first_name = body['first_name']
    last_name = body['last_name']
    phone = body['phone']
    vehicle = body['vehicle']
    bag_volume = body['bag_volume']

    query = SQL("""
insert into delivery_crud.courier(first_name, last_name, phone, vehicle, bag_volume)
values ({first_name}, {last_name}, {phone}, {vehicle}, {bag_volume})
returning id
""").format(first_name=Literal(first_name), last_name=Literal(last_name), phone=Literal(phone), vehicle=Literal(vehicle), bag_volume=Literal(bag_volume))

    with connection.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchone()

    return result


@app.put('/couriers/<uuid:id>')
def update_courier(id: uuid.UUID):
    body = request.json

    first_name = body['first_name']
    last_name = body['last_name']
    phone = body['phone']
    vehicle = body['vehicle']
    bag_volume = body['bag_volume']

    query = SQL("""
update delivery_crud.courier
set 
  first_name = {first_name}, 
  last_name = {last_name},
  phone = {phone},
  vehicle = {vehicle},
  bag_volume = {bag_volume}
where id = {id}
returning id
""").format(first_name=Literal(first_name), last_name=Literal(last_name),
            phone=Literal(phone), vehicle=Literal(vehicle), bag_volume=Literal(bag_volume), id=Literal(str(id)))

    with connection.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()

    if len(result) == 0:
        return '', 404

    return '', 204


@app.delete('/couriers/<uuid:id>')
def delete_courier(id: uuid.UUID):
    delete_courier = SQL("delete from delivery_crud.courier where id = {id} returning id").format(
        id=Literal(str(id)))

    with connection.cursor() as cursor:
        cursor.execute(delete_courier)
        result = cursor.fetchall()

    if len(result) == 0:
        return '', 404

    return '', 204


if __name__ == '__main__':
    app.run(port=os.getenv('FLASK_PORT'))