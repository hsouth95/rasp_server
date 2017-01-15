drop table if exists users;
create table users (
	user_key integer primary key,
	nickname varchar not null,
	permissions varchar default 'r' not null,
	picture varchar
)
