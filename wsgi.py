from spendingtracker import create_app, ConfigProd

app = create_app()

if __name__ == '__main__':
    app.run()
