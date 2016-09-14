create database test;
create user 'user'@'localhost' identified by 'pass';
grant all on test.* to 'user' identified by 'pass';
