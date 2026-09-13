class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///calculator.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False
    MAX_EXPRESSION_LENGTH = 512
    CLIENT_COOKIE_NAME = "calculator_user_id"
    CLIENT_COOKIE_MAX_AGE_SECONDS = 30 * 24 * 60 * 60
    CLIENT_COOKIE_SECURE = False
    CORS_ORIGINS = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
