import os

class Config:
    DEBUG = os.getenv('DEBUG', 'False') == 'True'
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key')
    DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///default.db')
    # Add more configuration variables as needed
    
# Example usage:
# config = Config()
# print(config.DEBUG)