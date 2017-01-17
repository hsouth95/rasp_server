drop table if exists users;
drop table if exists home;
drop table if exists rotation;
drop table if exists rotationuser;
create table home (
	id integer primary key,
	name varchar not null
);
create table users (
	user_key integer primary key,
	nickname varchar unique not null,
	permissions varchar default 'r' not null,
	picture varchar,
	home references home(id) not null
);
create table rotation (
	rotation_key integer primary key,
	name varchar unique not null,
	next references users(user_key)
);
create table rotationuser (
	rotation references rotation(rotation_key) not null,
	user references users(user_key) not null,
	sort_order integer not null
);