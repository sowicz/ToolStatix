import os
from dotenv import load_dotenv
import mariadb


# .env check if exist
load_dotenv()

for key in ["FIRST_LOGIN_ROOT_PASS","ROOT_PASSWORD", "DB_ADMIN_PASSWORD", "DB_USER_PASSWORD"]:
    if not os.getenv(key):
        raise ValueError(f"Brakuje zmiennych środowiskowych: {key}")


# Initialize database settings
# Create users for application 1 - user for app with full privilages / 2 - user for requesting 
# Create tables


FIRST_LOGIN_ADMIN_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password":  os.getenv("FIRST_LOGIN_ROOT_PASS"),  
}

ADMIN_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password":  os.getenv("ROOT_PASSWORD"),  
}

DB_NAME = "toolstatix_database"

users = [
    {
        "username": "appAdmin",
        "password": os.getenv("DB_ADMIN_PASSWORD"),
        "privileges": "ALL PRIVILEGES"
    },
    {
        "username": "appUser",
        "password": os.getenv("DB_USER_PASSWORD"),
        "privileges": "SELECT"
    }
]


TABLES_SQL = {
    "machines": """
        CREATE TABLE IF NOT EXISTS machines (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            description TEXT
        )
    """,
    "network_data_sources": """
        CREATE TABLE IF NOT EXISTS network_data_sources (
            id INT AUTO_INCREMENT PRIMARY KEY,
            machine_id INT NOT NULL,
            protocol VARCHAR(50) NOT NULL,
            server_url VARCHAR(255) NOT NULL,
            port INT,
            extra_config JSON,
            FOREIGN KEY (machine_id) REFERENCES machines(id) ON DELETE CASCADE
        )
    """,
    "main_tags": """
        CREATE TABLE IF NOT EXISTS main_tags (
            id INT AUTO_INCREMENT PRIMARY KEY,
            network_data_source_id INT NOT NULL,
            tag_name VARCHAR(100) NOT NULL,
            tag_address VARCHAR(255) NOT NULL,
            type VARCHAR(50),
            unit VARCHAR(50),
            threshold FLOAT,
            polls FLOAT,
            FOREIGN KEY (network_data_source_id) REFERENCES network_data_sources(id) ON DELETE CASCADE
        )
    """,
    "cleanup_tags": """
        CREATE TABLE IF NOT EXISTS cleanup_tags (
            id INT AUTO_INCREMENT PRIMARY KEY,
            main_tag_id INT UNIQUE NOT NULL,
            tag_name VARCHAR(100) NOT NULL,
            tag_address VARCHAR(255) NOT NULL,
            type VARCHAR(50),
            unit VARCHAR(50),
            polls FLOAT,
            FOREIGN KEY (main_tag_id) REFERENCES main_tags(id) ON DELETE CASCADE
        )
    """,
    "related_tags": """
        CREATE TABLE IF NOT EXISTS related_tags (
            id INT AUTO_INCREMENT PRIMARY KEY,
            main_tag_id INT NOT NULL,
            tag_name VARCHAR(100) NOT NULL,
            tag_address VARCHAR(255) NOT NULL,
            type VARCHAR(50),
            unit VARCHAR(50),
            polls FLOAT,
            FOREIGN KEY (main_tag_id) REFERENCES main_tags(id) ON DELETE CASCADE
        )
    """,
        "tags_data": """
        CREATE TABLE IF NOT EXISTS tags_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            main_tag_id INT NOT NULL,
            tag_name VARCHAR(255) NOT NULL,
            min FLOAT,
            max FLOAT,
            avg FLOAT,
            work_time INT,
            FOREIGN KEY (main_tag_id) REFERENCES main_tags(id) ON DELETE CASCADE
        )
    """

}


def connect_admin():
    return mariadb.connect(**FIRST_LOGIN_ADMIN_CONFIG)


def create_database(cursor):
    cursor.execute(f"ALTER USER 'root'@'localhost' IDENTIFIED BY '{os.getenv('ROOT_PASSWORD')}'")
    cursor.execute("FLUSH PRIVILEGES")
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    print(f"✅ database created:  '{DB_NAME}' (if not existed)")


def create_users(cursor):
    for user in users:
        cursor.execute(f"DROP USER IF EXISTS '{user['username']}'@'localhost'")
        cursor.execute(f"CREATE USER '{user['username']}'@'localhost' IDENTIFIED BY '{user['password']}'")
        cursor.execute(f"GRANT {user['privileges']} ON {DB_NAME}.* TO '{user['username']}'@'localhost'")
        print(f"✅ User '{user['username']}' with privileges: {user['privileges']}")


def create_tables():
    try:
        conn = mariadb.connect(
            host=ADMIN_CONFIG["host"],
            user=ADMIN_CONFIG["user"],
            password=ADMIN_CONFIG["password"],
            database=DB_NAME
        )
        cursor = conn.cursor()
        for name, sql in TABLES_SQL.items():
            cursor.execute(sql)
            print(f"✅ Tabela '{name}' utworzona")

        conn.commit()
        cursor.close()
        conn.close()

    except mariadb.Error as e:
        print(f"❌ Error while creating tables: {e}")


def setup():
    try:
        conn = connect_admin()
        cursor = conn.cursor()

        create_database(cursor)
        create_users(cursor)
        cursor.execute("FLUSH PRIVILEGES")
        conn.commit()

        create_tables()

        cursor.close()
        conn.close()
    except mariadb.Error as e:
        print(f"❌ Error MariaDB: {e}")


if __name__ == "__main__":
    setup()
