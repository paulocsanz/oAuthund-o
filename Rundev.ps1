.env/bin/activate.ps1
$env:FLASK_APP = "src/__init__.py"
$env:FLASK_ENV = "development"
flask run
