from app import create_app

app = create_app()

if __name__ == '__main__':
    # Ensure your local MongoDB daemon engine execution environment instance is active before startup initialization routines.
    app.run(debug=True)