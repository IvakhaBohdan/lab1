import psycopg2
import psycopg2.extras
import psycopg2.errors 

class Model:
    def __init__(self):
        try:
            self.conn = psycopg2.connect(
                dbname='postgres', 
                user='postgres',    
                password='1111',  
                host='localhost',
                options='-c search_path=auth,public',
                port=5432 
            )
            self.conn.autocommit = False 
            self.cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            print("З'єднання з БД успішно встановлено.")
            self.create_tables()
        except psycopg2.Error as e:
            print(f"Помилка підключення до БД: {e}")
            exit(1)

    def create_tables(self):
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS author (
                    author_id SERIAL PRIMARY KEY,
                    last_name TEXT NOT NULL,
                    first_name TEXT NOT NULL,
                    email TEXT UNIQUE
                );
            """)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS reader (
                    reader_id SERIAL PRIMARY KEY,
                    last_name TEXT NOT NULL,
                    first_name TEXT NOT NULL,
                    email TEXT UNIQUE
                );
            """)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS book (
                    book_id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    year_published INT,
                    pages INT,
                    id_author INT,
                    CONSTRAINT fk_author
                        FOREIGN KEY(id_author) 
                        REFERENCES author(author_id)
                        ON DELETE RESTRICT
                );
            """)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS "LoanJournal" (
                    loan_id SERIAL PRIMARY KEY,
                    id_book INT NOT NULL,
                    id_reader INT NOT NULL,
                    loan_date DATE NOT NULL DEFAULT CURRENT_DATE,
                    return_date DATE,
                    CONSTRAINT fk_book
                        FOREIGN KEY(id_book) 
                        REFERENCES book(book_id)
                        ON DELETE RESTRICT, 
                    CONSTRAINT fk_reader
                        FOREIGN KEY(id_reader) 
                        REFERENCES reader(reader_id)
                        ON DELETE RESTRICT, 
                    CHECK (return_date IS NULL OR return_date >= loan_date)
                );
            """)
            self.conn.commit() 
            print("Таблиці успішно перевірені/створені.")
        except psycopg2.Error as e:
            print(f"Помилка при створенні таблиць: {e}")
            self.conn.rollback()


    def _execute_query(self, query, params=None, fetch=True):
        try:
            self.cursor.execute(query, params)
            self.conn.commit() 
            if fetch:
                return self.cursor.fetchall()
            return None
        except (psycopg2.Error, psycopg2.DataError) as e:
            print(f"Помилка читання (SELECT): {e}")
            self.conn.rollback()
            return None

    def _execute_dml(self, query, params=None):
        try:
            self.cursor.execute(query, params)
            self.conn.commit() 
            return (True, None)
        
        except psycopg2.errors.UniqueViolation as e:
            self.conn.rollback()
            return (False, "Порушення унікальності. Можливо, такий email вже існує.")
        
        except psycopg2.errors.ForeignKeyViolation as e:
            self.conn.rollback()
            return (False, "Порушення зв'язності даних. (Наприклад, не можна видалити сутність, на яку посилається журнал).")
        
        except psycopg2.errors.NotNullViolation as e:
            self.conn.rollback()
            return (False, f"Не заповнене обов'язкове поле.")
        
        except (psycopg2.Error, psycopg2.DataError) as e:
            self.conn.rollback() 
            return (False, f"Загальна помилка SQL: {e}")

    # Перегляд даних 
    def get_authors(self):
        return self._execute_query("SELECT * FROM author ORDER BY author_id", fetch=True)
    
    def get_books(self):
        query = """
            SELECT b.book_id, b.name, b.year_published, b.pages, a.last_name || ' ' || a.first_name AS author_name
            FROM book b LEFT JOIN author a ON b.id_author = a.author_id
            ORDER BY b.book_id
        """
        return self._execute_query(query, fetch=True)

    def get_readers(self):
        return self._execute_query("SELECT * FROM reader ORDER BY reader_id", fetch=True)

    def get_loans(self):
        query = """
            SELECT l.loan_id, b.name AS book_title, r.last_name || ' ' || r.first_name AS reader_name, l.loan_date, l.return_date
            FROM "LoanJournal" l
            JOIN book b ON l.id_book = b.book_id
            JOIN reader r ON l.id_reader = r.reader_id
            ORDER BY l.loan_id ASC
        """
        return self._execute_query(query, fetch=True)

    # Методи для валідації
    def get_entity_by_id(self, entity_name, entity_id):
        allowed_entities = {
            'author': ('author', 'author_id'),
            'book': ('book', 'book_id'),
            'reader': ('reader', 'reader_id'),
            'LoanJournal': ('"LoanJournal"', 'loan_id') 
        }
        
        if entity_name not in allowed_entities:
            return None 
        
        table_name, id_column = allowed_entities[entity_name]
        query = f"SELECT 1 FROM {table_name} WHERE {id_column} = %s"
        
        result = self._execute_query(query, (entity_id,), fetch=True)
        return result 
    
    def get_book_validation_details(self, book_id):
        query = "SELECT year_published, name FROM book WHERE book_id = %s"
        result = self._execute_query(query, (book_id,), fetch=True)
        
        if result:
            return result[0] 
        return None
    
    # Додавання запису 
    def add_author(self, last_name, first_name, email):
        query = "INSERT INTO author (last_name, first_name, email) VALUES (%s, %s, %s)"
        return self._execute_dml(query, (last_name, first_name, email))

    def add_reader(self, last_name, first_name, email):
        query = "INSERT INTO reader (last_name, first_name, email) VALUES (%s, %s, %s)"
        return self._execute_dml(query, (last_name, first_name, email))

    def add_book(self, name, year_published, pages, id_author):
        query = "INSERT INTO book (name, year_published, pages, id_author) VALUES (%s, %s, %s, %s)"
        return self._execute_dml(query, (name, year_published, pages, id_author))

    def add_loan(self, id_book, id_reader, loan_date, return_date):
        query = 'INSERT INTO "LoanJournal" (id_book, id_reader, loan_date, return_date) VALUES (%s, %s, %s, %s)'
        return self._execute_dml(query, (id_book, id_reader, loan_date, return_date))

    # Редагування запису 
    def update_author(self, author_id, last_name, first_name, email):
        query = "UPDATE author SET last_name = %s, first_name = %s, email = %s WHERE author_id = %s"
        return self._execute_dml(query, (last_name, first_name, email, author_id))

    def update_reader(self, reader_id, last_name, first_name, email):
        query = "UPDATE reader SET last_name = %s, first_name = %s, email = %s WHERE reader_id = %s"
        return self._execute_dml(query, (last_name, first_name, email, reader_id))

    def update_book(self, book_id, name, year_published, pages, id_author):
        query = "UPDATE book SET name = %s, year_published = %s, pages = %s, id_author = %s WHERE book_id = %s"
        return self._execute_dml(query, (name, year_published, pages, id_author, book_id))

    def update_loan(self, loan_id, id_book, id_reader, loan_date, return_date):
        query = 'UPDATE "LoanJournal" SET id_book = %s, id_reader = %s, loan_date = %s, return_date = %s WHERE loan_id = %s'
        return self._execute_dml(query, (id_book, id_reader, loan_date, return_date, loan_id))

    # Видалення запису 
    def delete_author(self, author_id):
        query = "DELETE FROM author WHERE author_id = %s"
        return self._execute_dml(query, (author_id,))
    
    def delete_book(self, book_id):
        query = "DELETE FROM book WHERE book_id = %s"
        return self._execute_dml(query, (book_id,))
    
    def delete_reader(self, reader_id):
        query = "DELETE FROM reader WHERE reader_id = %s"
        return self._execute_dml(query, (reader_id,))

    def delete_loan(self, loan_id):
        query = 'DELETE FROM "LoanJournal" WHERE loan_id = %s'
        return self._execute_dml(query, (loan_id,))

    # Генерація 
    def generate_authors(self, count):
        query = """
            INSERT INTO author (first_name, last_name, email)
            SELECT
                (array[
                    'Stephen', 'George', 'Jane', 'Haruki', 'Agatha', 'Ernest', 
                    'Virginia', 'Oscar', 'Leo', 'Margaret', 'J.K.', 'Gabriel'
                ])[floor(random() * 12 + 1)] AS first_name,
                
                (array[
                    'King', 'Orwell', 'Austen', 'Murakami', 'Christie', 'Hemingway', 
                    'Woolf', 'Wilde', 'Tolstoy', 'Atwood', 'Rowling', 'Garcia Marquez'
                ])[floor(random() * 12 + 1)] AS last_name,
                
                'author.' || i::text || '@authors.com' AS email
            FROM
                generate_series(1, %s) AS s(i);
        """
        return self._execute_dml(query, (count,))
    def generate_readers(self, count):
        query = """
            INSERT INTO reader (first_name, last_name, email)
            SELECT
                (array[
                    'John', 'Ann', 'Bob', 'Alice', 'Peter', 'Mary', 'David', 
                    'Michael', 'Sarah', 'Chris', 'Emily', 'James', 'Jennifer', 'Daniel', 'Tom'
                ])[floor(random() * 15 + 1)] AS first_name,
                
                (array[
                    'Smith', 'Nelson', 'Wilson', 'Brown', 'Davis', 'Miller', 'Johnson', 
                    'Williams', 'Jones', 'Garcia', 'Rodriguez', 'Lee', 'Walker', 'Hall', 'White'
                ])[floor(random() * 15 + 1)] AS last_name,
                
                'reader.' || i::text || '@library.ua' AS email
            FROM
                generate_series(1, %s) AS s(i);
        """
        return self._execute_dml(query, (count,))
    
    def generate_books(self, count):
        query = """
            INSERT INTO book (name, year_published, pages, id_author)
            WITH authors AS (
                SELECT array_agg(author_id) AS ids FROM author
            )
            SELECT
                'Згенерована Книга №' || s.id,
                floor(random() * (2024 - 1950 + 1) + 1950)::int,
                floor(random() * (800 - 100 + 1) + 100)::int,
                a.ids[floor(random() * array_length(a.ids, 1) + 1 + (s.id * 0))]
            FROM 
                generate_series(1, %s) AS s(id), 
                authors a
            WHERE 
                a.ids IS NOT NULL;
        """
        return self._execute_dml(query, (count,))

    def generate_loans(self, count):
        query = """
            INSERT INTO "LoanJournal" (id_book, id_reader, loan_date, return_date)
            WITH 
                books AS (
                    SELECT array_agg(book_id) AS ids FROM book
                ),
                readers AS (
                    SELECT array_agg(reader_id) AS ids FROM reader
                ),
                GeneratedData AS (
                    SELECT
                        b.ids[floor(random() * array_length(b.ids, 1) + 1 + (s.id * 0))] AS b_id,
                        r.ids[floor(random() * array_length(r.ids, 1) + 1 + (s.id * 0))] AS r_id,
                        (timestamp '2020-01-01' + random() * (timestamp '2023-11-01' - timestamp '2020-01-01')) AS i_date
                    FROM 
                        generate_series(1, %s) s(id), 
                        books b, 
                        readers r
                    WHERE
                        b.ids IS NOT NULL AND r.ids IS NOT NULL
                )
            SELECT
                b_id,
                r_id,
                i_date::date,
                CASE WHEN random() > 0.2
                     THEN (i_date + (floor(random() * 85 + 5) || ' days')::interval)::date
                     ELSE NULL
                END
            FROM GeneratedData;
        """
        return self._execute_dml(query, (count,))

    # Пошук 
    def search_books_by_author_year(self, author_last_name, start_year, end_year):
        query = """
            SELECT b.book_id, b.name, b.year_published, a.last_name || ' ' || a.first_name AS author_name
            FROM book b
            JOIN author a ON b.id_author = a.author_id
            WHERE a.last_name LIKE %s AND b.year_published BETWEEN %s AND %s
        """
        return self._execute_query(query, (f"%{author_last_name}%", start_year, end_year), fetch=True)

    def search_readers_by_book_title(self, book_name_pattern):
        query = """
            SELECT
                r.reader_id,
                r.last_name,
                r.first_name,
                r.email,
                b.name AS book_name  
                
            FROM reader r
            JOIN "LoanJournal" l ON r.reader_id = l.id_reader
            JOIN book b ON l.id_book = b.book_id
            WHERE
                b.name ILIKE %s
            ORDER BY
                r.last_name, r.first_name, b.name;
        """
        return self._execute_query(query, (book_name_pattern,))

    def search_loans_by_date_range(self, start_date, end_date):
        query = """
            SELECT l.loan_id, b.name, r.last_name || ' ' || r.first_name AS reader, l.loan_date, l.return_date
            FROM "LoanJournal" l
            JOIN book b ON l.id_book = b.book_id
            JOIN reader r ON l.id_reader = r.reader_id
            WHERE l.loan_date BETWEEN %s AND %s
            ORDER BY l.loan_date
        """
        return self._execute_query(query, (start_date, end_date), fetch=True)

    def get_books_per_author(self, last_name_pattern):
        query = """
            SELECT
                a.author_id,  
                a.last_name,
                a.first_name,
                COUNT(b.book_id) AS book_count
            FROM author a
            LEFT JOIN book b ON a.author_id = b.id_author
            WHERE a.last_name ILIKE %s
            GROUP BY a.author_id, a.last_name, a.first_name
            ORDER BY book_count DESC, a.last_name;
        """
        return self._execute_query(query, (last_name_pattern,))

    def get_top_10_readers(self):
        query = """
            SELECT
                r.reader_id,
                r.last_name,
                r.first_name,
                COUNT(l.loan_id) AS loan_count
            FROM reader r
            JOIN "LoanJournal" l ON r.reader_id = l.id_reader
            GROUP BY r.reader_id, r.last_name, r.first_name
            ORDER BY loan_count DESC
            LIMIT 10;
        """
        return self._execute_query(query, fetch=True)

    def get_avg_loan_duration(self):
        query = """
            SELECT AVG(return_date - loan_date) AS avg_duration_days
            FROM "LoanJournal"
            WHERE return_date IS NOT NULL AND return_date >= loan_date
        """
        return self._execute_query(query, fetch=True)

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
            print("З'єднання з БД закрито.")