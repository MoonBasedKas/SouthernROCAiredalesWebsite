CREATE TABLE dogs (
    id int not null auto_increment,
    name char 256,
    gender boolean,
    desc char 4096,
    primary key (id)
);

create Table images(
    id int not null auto_increment,
    dogId int,
    photoName char 256,
    primary key (id),
    foreign key (dogId) references dogs(id)
)