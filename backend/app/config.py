class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///calculator.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False
    MAX_EXPRESSION_LENGTH = 512
    CORS_ORIGINS = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
