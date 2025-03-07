import psycopg2

# local
conn = psycopg2.connect(host="localhost", port="5432", user="postgres", database="myduka", password="icloudzafar1996")

# online
# conn = psycopg2.connect(host="134.209.24.19", port="5432", user="zafar", database="zafar", password="12345")


cur = conn.cursor()

print("database connected successfully")