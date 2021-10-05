from spendingtracker import create_app, ConfigProd

app=create_app(config_class=ConfigProd)

if __name__ == '__main__':
    app.run()