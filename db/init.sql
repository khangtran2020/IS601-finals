CREATE DATABASE userData;
use userData;

CREATE TABLE IF NOT EXISTS userTable(
    `id` int AUTO_INCREMENT,
    `username` VARCHAR(100) CHARACTER SET utf8,
    `password` VARCHAR(100) CHARACTER SET utf8,
    `firstname` VARCHAR(100) CHARACTER SET utf8,
    `lastname` VARCHAR(100) CHARACTER SET utf8,
    `school` VARCHAR(100) CHARACTER SET utf8,
    `department` VARCHAR(100) CHARACTER SET utf8,
    `year` INT,
    `isactivate` BOOLEAN,
    PRIMARY KEY (`id`)
);

INSERT INTO userTable (username,password,firstname,lastname,school,department,year,isactivate) VALUES
    ('kt36@njit.edu','1d3d89785a0eae29c4cc3f8abc49b060', 'Khang', 'Tran', 'NJIT','Infomatics',1,TRUE),
    ('ssv47@njit.edu','6abcfbfa1a5b141663a3583f4d48a302', 'Sahaj', 'Vaidya', 'NJIT','Infomatics',2,TRUE);
