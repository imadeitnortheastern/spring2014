create table if not exists users (
  user_id integer primary key autoincrement,
  username text not null,
  password text not null,
  port integer not null,
  email text not null,
  college text not null,
  marketing text not null
);
