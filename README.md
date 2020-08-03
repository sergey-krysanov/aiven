This is a test home work for Aiven.

The project consist of two parts. One part is a producer which 
checks for sites availability and send the collected data to Kafka. 
Second part is a consumer which reads data from Kafka and stores it to 
PostgreSql database.
Producers are splitted by groups which are defined in database. Current 
setup has two groups: group_01 and group_02.
To start producer run a console command:
./run_producer.sh {group_name}

Consumers are splitted by partitions whiwch are defined in Kafka topic setup.
Current setup has 3 partitions: [0, 1, 2].
To start consumer run a console command:
./run_consumer.sh {partition}

Database scema is described in file sql/create_db.sql.
Database content is described in file sql/add_sites.sql

This project is tested in next environment:

OS: macOS Catalina version 10.15.6
Python 2.7.16

pytz==2013.7
requests==2.24.0
psycopg2==2.8.5
kafka-python==2.0.1
