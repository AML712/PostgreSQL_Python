import psycopg2

def drop_table(cur):
    cur.execute("""
        DROP TABLE client, clientphone CASCADE;
        """)


def create_db(cur):
    cur.execute("""
    CREATE TABLE IF NOT EXISTS client(
        id SERIAL PRIMARY KEY,
        first_name VARCHAR(30) NOT NULL,
        last_name VARCHAR(30) NOT NULL,
        email VARCHAR(254)
        );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS clientphone(
        id SERIAL PRIMARY KEY,
        client_id INTEGER NOT NULL REFERENCES client(id),
        phone VARCHAR(20) 
        );
    """)


def add_client(cur, first_name, last_name, email, phone=None):
    cur.execute("""
                INSERT INTO client(first_name, last_name, email)
                VALUES (%s, %s, %s)
                RETURNING id;
                """, (first_name, last_name, email))
    client_id = cur.fetchone()
    if phone:
        cur.execute("""
                INSERT INTO clientphone(client_id, phone)
                VALUES (%s, %s)
                """, (client_id, phone))


def add_phone(cur, client_id, phone):
    cur.execute("""
                INSERT INTO clientphone(client_id, phone)
                VALUES (%s, %s)
                """, (client_id, phone))


def change_client(cur, client_id, first_name=None, last_name=None, email=None, phone=None):
    if phone != None:
        cur.execute("""
            UPDATE clientphone
            SET phone = %s
            WHERE client_id = %s
            """, (phone, client_id))

    if email != None:
        cur.execute("""
            UPDATE client
            SET email = %s
            WHERE id = %s
            """, (email, client_id))

    if first_name != None:
        cur.execute("""
            UPDATE client
            SET first_name = %s
            WHERE id = %s
            """, (first_name, client_id))

    if last_name != None:
        cur.execute("""
            UPDATE client
            SET last_name = %s
            WHERE id = %s
            """, (last_name, client_id))


def delete_phone(cur, phone=None):
    cur.execute("""
        DELETE FROM clientphone
        WHERE phone=%s;
        """, (phone, ))
    return phone


def delete_client(cur, client_id):
    cur.execute("""
        DELETE FROM clientphone WHERE id=%s;
        """, (client_id))
    delete_phone(cur, None, client_id)


def find_client(cur, first_name=None, last_name=None, email=None, phone=None):
    info = {}
    if first_name:
        info['first_name'] = first_name
    if last_name:
        info['last_name'] = last_name
    if email:
        info['email'] = email
    if phone:
        info['phone'] = phone

    query = """SELECT first_name, last_name, email, clientphone.phone FROM client
        JOIN clientphone ON client.id = clientphone.client_id
        WHERE """ + ' and '.join(f"{k} like '{v}'" for k, v in info.items())
    cur.execute(query)
    return cur.fetchall()

if __name__== '__main__':
    with psycopg2.connect(database="clients_data", user="postgres", password="aml712") as conn:
        with conn.cursor() as cur:
            drop_table(cur)
            create_db(cur)
            add_client(cur, 'Anna', 'Karenina', 'akarenina@gmail.com', '71111111111')
            add_client(cur, 'Peter', 'Pen', 'ppen@yandex.ru', '79261111111')
            add_phone(cur, '1', '71261111111')
            change_client(cur, 1)
            delete_phone(cur, '71111111111')
            #find_client(cur, first_name='Anna')
            client = find_client(cur, first_name='Anna', phone='71261111111')
            print(client)
            conn.commit()


conn.close()