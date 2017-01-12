drop table if exists users;
create table users (
	user_key varchar primary key,
	nickname varchar not null
)
