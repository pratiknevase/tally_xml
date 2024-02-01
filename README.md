## Steps

1. Clone the project

2. Create python virtual environment inside code folder

    `python3.10 -m venv env`
    
    `source env/bin/activate`


3. Install all dependancies

    `pip install -r requirements.txt`


4. Run the Flask app

    `python app.py`


5. Run the curl command

    `curl --location 'http://localhost:5000/convert'`

6. Output file will be generated on specified path in API response.