# jukebox-tnj
A work in progress. 

Current specs:
- Python 3.5.1 (Python 2 might also work but not tested)
- Django 1.9.2
- SQLite

To run locally:
- Checkout the repo.
- Install the versions of Python and Django above (SQLite comes as the default with Django 1.9)
- In the project root directory (the same folder as `manage.py`:
    - run `./manage.py migrate` to create the SQLite DB.
    - run `./manage.py collectstatic` to build the CSS/JS files.
    - create an admin account with `./manage.py create_superuser` (follow the prompts).
    - run `./manage.py runserver` to start the server
- Now go to http://127.0.0.1:8000/schedule, log in as the superuser and behold the wonder of Jukebox TNJ.
