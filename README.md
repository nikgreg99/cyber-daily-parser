# Cyber Daily Neswletter Parser

## Description

Cyber Threat Intelligence is the basis for preventing a large number of cyber attacks. This small project is aims to collect all the information that come from a powerful intelligence source: Cyber Daily Newsletter. This newsletter contains different information about new threats focusing on: vulnerability exploits, malware and suspicious IP address. The project access to your mail inbox, download all the newsletter and save the data inside a PostgreSQL database.

## How install the project

### Install PostgreSQL
  
The project requires a PostgreSQL Database used to store all data retrieved from the newsletter. First of all you have to create the database using the following command on Postgres console:
```SQL
CREATE USER cyber_daily WITH PASSWORD cyber_daily;
CREATE DATABASE cyber_daily_newsletter;
GRANT ALL PRIVILEGES ON DATABASE cyber_daily_newsletter TO cyber_daily;
```
Database and user's name can be customed with your own taste

### Dependencies

The project requires the following dependencies:

* imap-tools
* pyscopg2
* bs4 - Beautiful Soap
* html2text

Use the following command to install the necessary dependencies in your **venv**:
```python
pip3 install imapt-tools psycopg2 bs4 html2text
```

## How run the project

Type the following command to run the project:
```python
    python3 client.exe imap_server mail password
```
This sample helps you how and in which order customize the parameters according to your needs.

## References
[Recorder Future](https://www.recordedfuture.com/)

## License
MIT © License