import os

# You can load this from environment variables or a config file
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///:memory:")
SECRET_KEY = os.getenv("SECRET_KEY", "mysecretkey")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
