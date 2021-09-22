DROP TABLE IF EXISTS recipes;
DROP TABLE IF EXISTS favorites;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS product_entity;
DROP TABLE IF EXISTS product_category_entity;
DROP TABLE IF EXISTS dish_entity;
DROP TABLE IF EXISTS dish_category_entity;
DROP TABLE IF EXISTS hibernate_sequence;


create table hibernate_sequence (
    next_val bigint
);

insert into hibernate_sequence values ( 1 );
insert into hibernate_sequence values ( 1 );

CREATE TABLE dish_category_entity (
    id BIGSERIAL,
    title varchar(255) not null,
	PRIMARY KEY (id)
);

CREATE TABLE product_category_entity (
    id BIGSERIAL,
    title varchar(255) not null,
	PRIMARY KEY (id)
);

CREATE TABLE product_entity (
    id BIGSERIAL,
    title varchar(255) not null,
	product_cat_id int REFERENCES product_category_entity(id),
	PRIMARY KEY (id)
);

CREATE TABLE dish_entity (
    id BIGSERIAL,
    title varchar(255) not null,
	description TEXT,
	ingredients_list TEXT,
	img_path TEXT,
    dish_cat_id int REFERENCES dish_category_entity(id),
	PRIMARY KEY (id)
);

CREATE TABLE recipes
(
    id BIGSERIAL,
    product_id bigint NOT NULL,
    dish_id bigint NOT NULL,
	quantity character varying,
    CONSTRAINT produck_id_fk FOREIGN KEY (product_id)
        REFERENCES product_entity (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT dish_id_fk FOREIGN KEY (dish_id)
        REFERENCES dish_entity (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE,
	PRIMARY KEY(id)

);

CREATE TABLE users
(
    id       uuid not null,
    name     varchar(64) not null,
    login    varchar(64) not null,
    password varchar(64) not null,
    PRIMARY KEY (id)
);

CREATE TABLE favorites
(
    id BIGSERIAL,
    product_id bigint NOT NULL,
    user_id uuid NOT NULL,
    CONSTRAINT produck_id_fk FOREIGN KEY (product_id)
        REFERENCES product_entity (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT user_id_fk FOREIGN KEY (user_id)
        REFERENCES users (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE,
	PRIMARY KEY(id)

);