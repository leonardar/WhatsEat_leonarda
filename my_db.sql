DROP TABLE if EXISTS recipe;
DROP TABLE if EXISTS product;
DROP TABLE if EXISTS dish;
DROP TABLE IF EXISTS dishcat;
DROP TABLE IF EXISTS hibernate_sequence;
DROP TABLE IF EXISTS Users;

CREATE TABLE DishCat (
    id SERIAL PRIMARY KEY,
    title varchar(255) not null
);

CREATE TABLE Dish (
    id SERIAL PRIMARY KEY,
    title varchar(255) not null,
    description TEXT,
    dishcat_id int REFERENCES DishCat(id)
);

CREATE TABLE Product (
    id SERIAL PRIMARY KEY,
    title varchar(255) not null,
    dish_id int REFERENCES Dish
);

CREATE TABLE Recipe (
    id SERIAL primary key,
    dish_id int references dish,
    product_id int references product
);

create table hibernate_sequence (
    next_val bigint
);


CREATE TABLE Users (
    id INT,
    username varchar(255) not null,
    password varchar(255) not null

);
