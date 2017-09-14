CREATE DATABASE IF NOT EXISTS sigalogado CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE sigalogado;

CREATE TABLE IF NOT EXISTS sigalogado.applications
(
    id               INT       NOT NULL AUTO_INCREMENT,
    creator_username CHAR(255) NOT NULL,
    name             CHAR(255) NOT NULL,
    description      CHAR(255) NOT NULL,
    redirect_uri     CHAR(255) NOT NULL,
    client_id        CHAR(255) NOT NULL,
    client_secret    CHAR(255) NOT NULL,
    CONSTRAINT       id        PRIMARY KEY(id)
);

CREATE TABLE IF NOT EXISTS sigalogado.authorizations
(
    id            INT       NOT NULL AUTO_INCREMENT,
    client_id     CHAR(255) NOT NULL,
    username      CHAR(255) NOT NULL,
    CONSTRAINT    id        PRIMARY KEY(id)
);

CREATE TABLE IF NOT EXISTS sigalogado.granted_accesses
(
    id            INT       NOT NULL AUTO_INCREMENT,
    client_id     CHAR(255) NOT NULL,
    code_hash     CHAR(255) NOT NULL,
    access_token  CHAR(255) NOT NULL,
    refresh_token CHAR(255) NOT NULL,
    valid         TINYINT   NOT NULL,
    CONSTRAINT  PRIMARY KEY(id)
);

CREATE TABLE IF NOT EXISTS sigalogado.authentications
(
    id                 INT  NOT NULL AUTO_INCREMENT,
    username           CHAR(255) NOT NULL,
    access_token_hash  CHAR(255) NOT NULL,
    encrypted_cookie   CHAR(255) NOT NULL,
    refresh_token_hash CHAR(255) NOT NULL,
    encrypted_password CHAR(255) NOT NULL,
    CONSTRAINT id      PRIMARY KEY(id)
);
