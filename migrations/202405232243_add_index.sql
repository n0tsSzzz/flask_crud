-- migrate:up


create extension pg_trgm;

insert into delivery_crud.delivery(title, phone)

select 
    md5(random()::text),
    (floor(random() * (9999999999 - 1000000000 + 1)) + 1000000000)::text
from generate_series(1, 100000);

create index delivery_phone_idx on delivery_crud.delivery using btree(phone);

create index delivery_title_trgm_idx on delivery_crud.delivery using gist(title gist_trgm_ops);


-- migrate:down