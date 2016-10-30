# MinTransfer

simple version of WeTransfer alternative

# How to Install

1. Download the source code

```bash
$ git clone https://github.com/soundlake/min-transfer.git; cd min-transfer
```

2. Install the dependency

    * [Flask](http://flask.pocoo.org/docs/0.11/)
    * [Flask-Assets](https://flask-assets.readthedocs.io/en/latest/)
    * [pyScss](https://pyscss.readthedocs.io/en/latest/)

```bash
$ pip install Flask Flask-Assets pyScss
```

3. Edit `secret.key` file

4. Make some directories

```bash
$ mkdir build var
```

5. Initialize the database

```bash
$ export FLASK_APP=flaskr.py; export FLASK_DEBUG=1; flask initdb
```

6. Run Flask

```bash
$ export FLASK_APP=flaskr.py; export FLASK_DEBUG=1; flask run
```

# Current Feature

* Upload file

# Future Plans

* Limit the life time of the uploaded file
* Send e-mail directly
* Aesthetical improvement
