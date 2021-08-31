from dotenv import load_dotenv, find_dotenv

from spendingtracker import create_app


load_dotenv(find_dotenv("./spendingtracker/.env"),verbose=True)
app=create_app()



if __name__ == '__main__':
    app.run(debug=True)
