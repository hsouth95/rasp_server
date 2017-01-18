insert into home (name, password) values ('test','password123');
insert into users (nickname, home) values('TestUser', 1);
insert into users (nickname, home) values('TestUser2', 1);
insert into rotation (name, next) values('TestRotation', 1);
insert into rotationuser(rotation, user, sort_order) values(1, 1, 1);
insert into rotationuser(rotation, user, sort_order) values(1, 2, 2); 