-- Table creation
CREATE TABLE dogs (
    id int not null auto_increment,
    name char 256,
    gender boolean,
    available boolean,
    desc char 4096,
    primary key (id)
);

create Table images(
    id int not null auto_increment,
    dogId int,
    photoName char 256,
    primary key (id),
    foreign key (dogId) references dogs(id)
);

-- Temp values
insert into dogs (name, gender, available, desc) values (
    "Jerry", 1, 1, "Jerry is a dog that goes beyond what is possible for all dogs. Some say Jerry isn't a dog but I say Jerry is the dog."
    "Jerrette", 1, 1, "Jerrette is Jerry, but if they were a female dog instead."
);

insert into images (dogId, photoName) values(
    1, "Jerry1.png"
    2, "Jerrette1.png"
);