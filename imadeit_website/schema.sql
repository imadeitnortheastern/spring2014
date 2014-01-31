
create table if not exists users (
  user_id integer primary key autoincrement,
  username text not null,
  password text not null,
  salt text not null,
  port integer not null,
  partner_port integer not null,
  email text not null,
  college text not null,
  prog_expr integer not null,
  marketing text not null
 );


