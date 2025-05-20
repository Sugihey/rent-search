"""
Configuration settings for the application.
"""

USE_SQLITE = False

MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'rentuser',
    'password': 'rentpassword',
    'database': 'rent_search',
    'charset': 'utf8mb4',
    'port': 3306
}
