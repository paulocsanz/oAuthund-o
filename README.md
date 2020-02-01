# Sigalogado

oAuth system for SIGA's (UFRJ) database

## Dependencies

- python3
- mysql

For ubuntu users run:

```
sudo apt install mysql-server libmysqlclient-dev
```

## Installing

Create a MySQL account for this server to use

Linux:

Don't forget to change the password in `{YOUR-PASSWORD-HERE}`

```
sudo mysql
CREATE USER 'sigalogado'@'localhost' IDENTIFIED BY '{YOUR-PASSWORD-HERE}';
GRANT ALL PRIVILEGES ON *.* TO 'sigalogado'@'localhost';
```

This is not the best sysadmin move, be careful with all those permissions. TODO: improve this.

Run:

`python3 install.py`

If it fails while installing Flask-MySQL because `mysql_config` mysql client library is missing on your system (libmysqlclient-dev on Ubuntu).

## Running

To run it locally on linux execute:

`./rundev`

On windows join the virtualenv and execute:

```
set FLASK_APP=src/__init__.py
flask run
```
