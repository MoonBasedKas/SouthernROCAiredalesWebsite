-- Table creation
CREATE TABLE dogs (
    id int not null auto_increment,
    dogName char (255),
    gender boolean,
    available boolean,
    dogDesc text(4096),
    dob DateTime,
    primary key (id)
);

create Table images(
    id int not null auto_increment,
    dogId int,
    photoName char(255),
    primary key (id),
    foreign key (dogId) references dogs(id)
);

-- Temp values
insert into dogs (dogName, gender, available, dogDesc) values 
    ("Jerry", 1, 1, "Jerry is a dog that goes beyond what is possible for all dogs. Some say Jerry isn't a dog but I say Jerry is the dog."),
    ("Jerrette", 1, 1, "Jerrette is Jerry, but if they were a female dog instead.");

insert into images (dogId, photoName) values
    (1, "Jerry1.png"),
    (2, "Jerrette1.png");