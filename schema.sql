drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  term text not null,
  url text not null
);
