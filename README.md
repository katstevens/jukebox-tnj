# jukebox-tnj
A work in progress. 

Current specs:
- Python 3.5.1 (Python 2 might also work but not tested)
- Django 1.9.2
- SQLite

To run locally:
- Checkout the repo.
- Create a Python3 venv if desired.
- Install requirements.txt (SQLite comes with Django)
- In the project root directory (the same folder as `manage.py`:
    - run `./manage.py migrate` to create the SQLite DB.
    - run `./manage.py collectstatic` to build the CSS/JS files.
    - create an admin account with `./manage.py create_superuser` (follow the prompts).
    - run `./manage.py runserver` to start the server
- Now go to http://127.0.0.1:8000/schedule, log in as the superuser and behold the wonder of Jukebox TNJ.

To run with MySQL:
- Create database and user in MySQL
- Change settings-prod.py DATABASE OPTIONS to point to the MySQL config file
- In the config file, include

    [client]
    database = NAME
    user = USER
    password = PASSWORD
    default-character-set = utf8

To create backups:
- Run `./manage.py dumpdata --output /path/to/dumps`
- TODO: configure and save backups to an S3 bucket
