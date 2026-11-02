import psycopg

DATABASE_URL = (
    "postgresql://mtaha_user:5a7Q8otdvFMH6Qdx43r6pQpUut1r9MHw"
    "@dpg-dbhnccoae00c73e7iglg-a.oregon-postgres.render.com/mtaha"
)

try:
    print("Connecting...")

    with psycopg.connect(
        DATABASE_URL,
        sslmode="require",
        connect_timeout=10,
        autocommit=True,
        options="-c statement_timeout=10000",
    ) as connection:
        database, user, server_time = connection.execute(
            "SELECT current_database(), current_user, NOW()"
        ).fetchone()

        print("Connection successful!")
        print("Database:", database)
        print("User:", user)
        print("Server time:", server_time)

except psycopg.Error as error:
    print("Connection failed:")
    print(error)