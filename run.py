from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv("./spendingtracker/.env"), verbose=True)
from spendingtracker import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0")
