-- Database initalization.
CREATE DATABASE SouthernROC;
USE SouthernROC;
-- Table creation
CREATE TABLE dogs (
    id int not null auto_increment,
    dogName char (255),
    gender boolean,
    available boolean,
    registration boolean,
    dob DateTime,
    mainPhoto text(1024),
    dogDesc text(4096),
    purchase boolean,
    
    primary key (id)
);

create Table photos(
    id int not null auto_increment,
    dogId int,
    photoName char(255),
    primary key (id)
);

create Table Puppies(
    id int not null auto_increment,
    photoName char(255),
    dateTaken DateTime,
    visible boolean,
    photo boolean,
    primary key (id)
);


create Table Users(
    id int not null auto_increment,
    username char(255) not null,
    password text(4096),
    primary key (id)
);
