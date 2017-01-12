drop table if exists users;
create table users (
	user_key integer primary key,
	nickname varchar not null
)
