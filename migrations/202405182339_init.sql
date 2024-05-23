-- migrate:up


create extension if not exists "uuid-ossp";

create schema delivery_crud;

create table delivery_crud.courier
(
	id         uuid primary key default uuid_generate_v4(),
	first_name text,
	last_name  text,
	phone      text,
	vehicle    text,
	bag_volume int
);

create table delivery_crud.delivery
(
	id    uuid primary key default uuid_generate_v4(),
	title text,
	phone text
);

create table delivery_crud.courier_delivery
(
	delivery_id uuid references delivery_crud.delivery,
	courier_id uuid references delivery_crud.courier on delete cascade,
	primary key (delivery_id, courier_id)
);

create table delivery_crud.user_order
(
	id         uuid primary key default uuid_generate_v4(),
	address    text,
	date       date,
	status 	   text,
	courier_id uuid references delivery_crud.courier on delete cascade
);

insert into delivery_crud.courier(first_name, last_name, phone, vehicle, bag_volume)
values ('Жак', 'Фреско', '89183027764', 'велоспиед', '10'),
	   ('Эль', 'Примо', '89184060795', 'ноги', '5'),
	   ('Оля', 'Бабуля', '+7988888888', 'машина', '30');
	  
insert into delivery_crud.delivery(title, phone)
values ('Яндекс еда', '88005553535'),
	   ('Delivery club', '+79999876543');
	  
insert into delivery_crud.courier_delivery(delivery_id, courier_id)
values ((select id from delivery_crud.delivery where title = 'Яндекс еда'),
		(select id from delivery_crud.courier where phone = '89183027764')),
	   ((select id from delivery_crud.delivery where title = 'Яндекс еда'),
		(select id from delivery_crud.courier where phone = '89184060795')),
	   ((select id from delivery_crud.delivery where title = 'Delivery club'),
		(select id from delivery_crud.courier where phone = '89183027764')),
	   ((select id from delivery_crud.delivery where title = 'Delivery club'),
		(select id from delivery_crud.courier where phone = '+7988888888'));

insert into delivery_crud.user_order(address, date, status, courier_id)
values ('Gorkogo st', '2024-02-11', 'В пути', (select id from delivery_crud.courier where phone = '89184060795')),
	   ('Lenina st', '2024-02-11', 'В пути', (select id from delivery_crud.courier where phone = '89184060795')),
	   ('Voskresenkaya st', '2023-11-23', 'Завершено', (select id from delivery_crud.courier where phone = '89183027764'));
	  
select * from delivery_crud.user_order;


-- migrate:down