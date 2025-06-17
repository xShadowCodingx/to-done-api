# Set up for running the app with python -m run

from app import create_app, config

app = create_app()
testing = config.Config.TESTING

if __name__ == '__main__':
    app.run(debug=testing)
