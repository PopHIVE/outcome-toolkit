from app.factory import create_app
from db.datasets.common_imports import * 

# Initialize the App from the Factory
app = create_app()

if __name__ == '__main__':
    print(app.url_map)
    app.run(host='0.0.0.0', port=5000)
