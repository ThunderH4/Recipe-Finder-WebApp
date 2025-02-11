import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///recipeapp.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SPOONACULAR_API_KEY=os.getenv('SPOONACULAR_API_KEY')
    IMAGGA_API_KEY=os.getenv('IMAGGA_API_KEY')
    IMAGGA_API_SECRET=os.getenv('IMAGGA_API_SECRET')
    EDAMAM_API_USER_ID=os.getenv('EDAMAM_API_USER_ID')
    EDAMAM_API_APP_KEY=os.getenv('EDAMAM_API_APP_KEY')
    EDAMAM_API_APP_ID=os.getenv('EDAMAM_API_APP_ID')