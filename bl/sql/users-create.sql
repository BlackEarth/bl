-- users model

begin;
---------------------------------------------------------------------------

-- users --
--  This is the minimal users table. Add other fields that you would like.
--  	email = user id
--  	pwd is hashed (use the strongest one-way hash you can)
--  	salt is hashed and fed into pwd
--  	verification is optional

create table users (
  email       varchar primary key,
  pwd         varchar,
  salt        varchar,
  registered  timestamptz(0) default current_timestamp,
  verified    timestamptz(0)
);

---------------------------------------------------------------------------
commit;