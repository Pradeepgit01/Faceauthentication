CREATE DATABASE face_authentication;

USE face_authentication;

CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255),
    face_encoding BLOB
);
