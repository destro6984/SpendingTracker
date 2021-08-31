from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv("./spendingtracker/.env"),verbose=True)
from spendingtracker import create_app, ConfigProd


app=create_app()



if __name__ == '__main__':
    app.run()
