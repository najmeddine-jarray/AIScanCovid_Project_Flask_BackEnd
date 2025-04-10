## Flask_PostgresSQL_CRUD
This Application with a flask backend and Postgres as Database (with psycopg2)

### Requirements

* Python 3
* PostgreSQL
* Flask

### environment variables
```
* this project created in anaconda environment
```
```
for example:

DATABASE_URI = 'postgresql://your_username:your_password@your_host:your_port/your_database_name'

```
PGPASSWORD=cJDLzYKDo7RCl7ueWJvrpCdaJUfH7NZ4 psql -h dpg-cvrupa0gjchc73a3plg0-a.oregon-postgres.render.com -U ai_covid_scan_user ai_covid_scan

```

### environment variables cloud

for example:

```
DB_HOST = localhost
DB_PORT = 5432
DB_NAME = postgres
DB_USER = postgres
DB_PASSWORD = password
```
### Attention
### Attention

* take Model out of the folder covid_predictionZIP
* It must be in the same poth with main.py

### Installation

```
git clone https://github.com/JARRAY-NAJEM/AIScanCovid_Project_Flask_BackEnd.git

cd AIScanCovid_Project_Flask_BackEnd

pip install -r requirements.txt

python main.py
```