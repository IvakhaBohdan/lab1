import time
from datetime import datetime, date

from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey, CheckConstraint, text
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import IntegrityError, DataError, ProgrammingError, OperationalError
from sqlalchemy.orm import class_mapper


DATABASE_URL = "postgresql+psycopg2://postgres:1111@localhost:5432/postgres?options=-c search_path=auth,public"
Base = declarative_base()

class Author(Base):
    __tablename__ = 'author'
    author_id = Column(Integer, primary_key=True)
    last_name = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    email = Column(String, unique=True)
    
    books = relationship("Book", backref="author", passive_deletes=True) 

    def to_dict_for_view(self):
        return {
            'author_id': self.author_id,
            'last_name': self.last_name,
            'first_name': self.first_name,
            'email': self.email
        }

class Reader(Base):
    __tablename__ = 'reader'
    reader_id = Column(Integer, primary_key=True)
    last_name = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    email = Column(String, unique=True)
    
    loans = relationship("LoanJournal", backref="reader", passive_deletes=True)
    
    def to_dict_for_view(self):
        return {
            'reader_id': self.reader_id,
            'last_name': self.last_name,
            'first_name': self.first_name,
            'email': self.email
        }

class Book(Base):
    __tablename__ = 'book'
    book_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    year_published = Column(Integer)
    pages = Column(Integer)
    id_author = Column(Integer, ForeignKey('author.author_id', ondelete='RESTRICT')) 
    
    loans = relationship("LoanJournal", backref="book", passive_deletes=True)

    def get_validation_details(self):
        return {
            'year_published': self.year_published,
            'name': self.name
        }

class LoanJournal(Base):
    __tablename__ = 'LoanJournal'
    loan_id = Column(Integer, primary_key=True)
    
    id_book = Column(Integer, ForeignKey('book.book_id', ondelete='RESTRICT'), nullable=False)
    id_reader = Column(Integer, ForeignKey('reader.reader_id', ondelete='RESTRICT'), nullable=False)
    
    loan_date = Column(Date, nullable=False)
    return_date = Column(Date, default=None)
    
    __table_args__ = (
        CheckConstraint('return_date IS NULL OR return_date >= loan_date', name='check_return_date_valid'),
    )


class Model:
    def __init__(self):
        try:
            self.engine = create_engine(DATABASE_URL)
            self.Session = sessionmaker(bind=self.engine)
            
            self.create_tables()
            print("З'єднання з БД успішно встановлено.")
        except OperationalError as e:
            print(f"Помилка підключення до БД. Перевірте: {self.engine.url.render_as_string()} та налаштування сервера. Деталі: {e}")
            exit(1)
        except Exception as e:
            print(f"Критична помилка ініціалізації: {e}")
            exit(1)

    def create_tables(self):
        try:
            Base.metadata.create_all(self.engine) 
            print("Таблиці успішно перевірені/створені.")
        except Exception as e:
            print(f"Помилка при створенні таблиць: {e}")

    # Допоміжні методи DML 
    def _execute_dml_orm(self, session, entity_instance=None, commit_on_success=True):
        try:
            if entity_instance is not None:
                session.add(entity_instance)
            
            if commit_on_success:
                session.commit() 
            return (True, None)
        
        except IntegrityError as e:
            session.rollback()
            error_msg = str(e)
            if 'unique constraint' in error_msg or 'UniqueViolation' in error_msg:
                return (False, "Порушення унікальності. Можливо, такий email вже існує.")
            if 'foreign key constraint' in error_msg or 'ForeignKeyViolation' in error_msg:
                return (False, "Порушення зв'язності даних. (Наприклад, не можна видалити сутність, на яку посилається журнал).")
            if 'not null constraint' in error_msg or 'NotNullViolation' in error_msg:
                return (False, "Не заповнене обов'язкове поле.")
            if 'check constraint' in error_msg or 'check_return_date_valid' in error_msg:
                return (False, "Порушення умови: дата повернення не може бути раніше дати видачі.")
            
            return (False, f"Загальна помилка цілісності даних: {e}")

        except DataError as e:
            session.rollback()
            return (False, f"Помилка даних (наприклад, некоректний тип): {e}")
        
        except Exception as e:
            session.rollback() 
            return (False, f"Загальна помилка SQL: {e}")
        
    # Перегляд даних (SELECT) 
    
    def get_authors(self):
        session = self.Session()
        try:
            authors = session.query(Author).order_by(Author.author_id).all()
            return [a.to_dict_for_view() for a in authors]
        finally:
            session.close()

    def get_readers(self):
        session = self.Session()
        try:
            readers = session.query(Reader).order_by(Reader.reader_id).all()
            return [r.to_dict_for_view() for r in readers]
        finally:
            session.close()
    
    def get_books(self):
        session = self.Session()
        try:
            books_data = session.query(
                Book.book_id,
                Book.name,
                Book.year_published,
                Book.pages,
                (Author.last_name + ' ' + Author.first_name).label('author_name')
            ).join(Author, Book.id_author == Author.author_id, isouter=True)\
             .order_by(Book.book_id).all()
        
            return [row._asdict() for row in books_data]
        finally:
            session.close()

    def get_loans(self):
        session = self.Session()
        try:
            loans_data = session.query(
                LoanJournal.loan_id, 
                Book.name.label('book_title'), 
                (Reader.last_name + ' ' + Reader.first_name).label('reader_name'),
                LoanJournal.loan_date,
                LoanJournal.return_date
            ).join(Book, LoanJournal.id_book == Book.book_id)\
             .join(Reader, LoanJournal.id_reader == Reader.reader_id)\
             .order_by(LoanJournal.loan_id.asc()).all()
            
            
            return [row._asdict() for row in loans_data]
        finally:
            session.close()

    # Методи для валідації 
    
    def get_entity_by_id(self, entity_name, entity_id):
        session = self.Session()
        
        entity_map = {
            'author': Author,
            'book': Book,
            'reader': Reader,
            'LoanJournal': LoanJournal
        }
        
        if entity_name not in entity_map:
            session.close()
            return None 

        EntityClass = entity_map[entity_name]
        try:
            pk_column = class_mapper(EntityClass).primary_key[0]
            
            result = session.query(pk_column).filter(pk_column == entity_id).first()
            
            return [1] if result else None 
        
        finally:
            session.close()
    
    def get_book_validation_details(self, book_id):
        session = self.Session()
        try:
            book = session.query(Book).filter(Book.book_id == book_id).first()
            
            if book:
                return book.get_validation_details()
            return None
        finally:
            session.close()
    
    # Додавання запису (INSERT)
    
    def add_author(self, last_name, first_name, email):
        session = self.Session()
        new_author = Author(last_name=last_name, first_name=first_name, email=email)
        response = self._execute_dml_orm(session, new_author)
        session.close()
        return response

    def add_reader(self, last_name, first_name, email):
        session = self.Session()
        new_reader = Reader(last_name=last_name, first_name=first_name, email=email)
        response = self._execute_dml_orm(session, new_reader)
        session.close()
        return response

    def add_book(self, name, year_published, pages, id_author):
        session = self.Session()
        new_book = Book(name=name, year_published=year_published, pages=pages, id_author=id_author)
        response = self._execute_dml_orm(session, new_book)
        session.close()
        return response

    def add_loan(self, id_book, id_reader, loan_date, return_date):
        session = self.Session()
        new_loan = LoanJournal(id_book=id_book, id_reader=id_reader, loan_date=loan_date, return_date=return_date)
        response = self._execute_dml_orm(session, new_loan)
        session.close()
        return response

    # Редагування запису (UPDATE)
    
    def update_author(self, author_id, last_name, first_name, email):
        session = self.Session()
        try:
            author_to_update = session.query(Author).filter(Author.author_id == author_id).first()
            if not author_to_update:
                session.close()
                return (False, f"Автора з ID {author_id} не знайдено.")
            
            author_to_update.last_name = last_name
            author_to_update.first_name = first_name
            author_to_update.email = email
            
            response = self._execute_dml_orm(session)
            return response
        finally:
            session.close()

    def update_reader(self, reader_id, last_name, first_name, email):
        session = self.Session()
        try:
            reader_to_update = session.query(Reader).filter(Reader.reader_id == reader_id).first()
            if not reader_to_update:
                session.close()
                return (False, f"Читача з ID {reader_id} не знайдено.")
            
            reader_to_update.last_name = last_name
            reader_to_update.first_name = first_name
            reader_to_update.email = email
            
            response = self._execute_dml_orm(session)
            return response
        finally:
            session.close()

    def update_book(self, book_id, name, year_published, pages, id_author):
        session = self.Session()
        try:
            book_to_update = session.query(Book).filter(Book.book_id == book_id).first()
            if not book_to_update:
                session.close()
                return (False, f"Книги з ID {book_id} не знайдено.")
            
            book_to_update.name = name
            book_to_update.year_published = year_published
            book_to_update.pages = pages
            book_to_update.id_author = id_author
            
            response = self._execute_dml_orm(session)
            return response
        finally:
            session.close()

    def update_loan(self, loan_id, id_book, id_reader, loan_date, return_date):
        session = self.Session()
        try:
            loan_to_update = session.query(LoanJournal).filter(LoanJournal.loan_id == loan_id).first()
            if not loan_to_update:
                session.close()
                return (False, f"Запису журналу з ID {loan_id} не знайдено.")
            
            loan_to_update.id_book = id_book
            loan_to_update.id_reader = id_reader
            loan_to_update.loan_date = loan_date
            loan_to_update.return_date = return_date
            
            response = self._execute_dml_orm(session)
            return response
        finally:
            session.close()

    # Видалення запису (DELETE)
    
    def delete_author(self, author_id):
        session = self.Session()
        try:
            author_to_delete = session.query(Author).filter(Author.author_id == author_id).first()
            if not author_to_delete:
                session.close()
                return (False, f"Автора з ID {author_id} не знайдено.")
            
            session.delete(author_to_delete)
            response = self._execute_dml_orm(session)
            return response
        finally:
            session.close()
    
    def delete_book(self, book_id):
        session = self.Session()
        try:
            book_to_delete = session.query(Book).filter(Book.book_id == book_id).first()
            if not book_to_delete:
                session.close()
                return (False, f"Книги з ID {book_id} не знайдено.")
            
            session.delete(book_to_delete)
            response = self._execute_dml_orm(session)
            return response
        finally:
            session.close()
    
    def delete_reader(self, reader_id):
        session = self.Session()
        try:
            reader_to_delete = session.query(Reader).filter(Reader.reader_id == reader_id).first()
            if not reader_to_delete:
                session.close()
                return (False, f"Читача з ID {reader_id} не знайдено.")
            
            session.delete(reader_to_delete)
            response = self._execute_dml_orm(session)
            return response
        finally:
            session.close()

    def delete_loan(self, loan_id):
        session = self.Session()
        try:
            loan_to_delete = session.query(LoanJournal).filter(LoanJournal.loan_id == loan_id).first()
            if not loan_to_delete:
                session.close()
                return (False, f"Запису журналу з ID {loan_id} не знайдено.")
            
            session.delete(loan_to_delete)
            response = self._execute_dml_orm(session)
            return response
        finally:
            session.close()

    # Генерація
    
    def generate_authors(self, count):
        session = self.Session()
        
        query = text(f"""
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
                generate_series(1, {count}) AS s(i)
            ON CONFLICT (email) DO NOTHING;
        """)
        try:
            session.execute(query)
            response = self._execute_dml_orm(session)
            return response
        except Exception as e:
            session.rollback()
            return (False, f"Помилка генерації авторів: {e}")
        finally:
            session.close()
            
    def generate_readers(self, count):
        session = self.Session()
        
        query = text(f"""
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
                generate_series(1, {count}) AS s(i)
            ON CONFLICT (email) DO NOTHING;
        """)
        try:
            session.execute(query)
            response = self._execute_dml_orm(session)
            return response
        except Exception as e:
            session.rollback()
            return (False, f"Помилка генерації читачів: {e}")
        finally:
            session.close()

    def generate_books(self, count):
        session = self.Session()
        
        query = text(f"""
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
                generate_series(1, {count}) AS s(id), 
                authors a
            WHERE 
                a.ids IS NOT NULL;
        """)
        try:
            session.execute(query)
            response = self._execute_dml_orm(session)
            return response
        except Exception as e:
            session.rollback()
            return (False, f"Помилка генерації книг: {e}")
        finally:
            session.close()

    def generate_loans(self, count):
        session = self.Session()
        
        query = text(f"""
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
                        generate_series(1, {count}) s(id), 
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
        """)
        try:
            session.execute(query)
            response = self._execute_dml_orm(session)
            return response
        except Exception as e:
            session.rollback()
            return (False, f"Помилка генерації записів журналу: {e}")
        finally:
            session.close()


    # Пошук (SELECT)
    
    def search_books_by_author_year(self, author_last_name, start_year, end_year):
        session = self.Session()
        try:
            results = session.query(
                Book.book_id,
                Book.name,
                Book.year_published,
                (Author.last_name + ' ' + Author.first_name).label('author_name')
            ).join(Author, Book.id_author == Author.author_id)\
             .filter(
                Author.last_name.ilike(f"%{author_last_name}%"),
                Book.year_published.between(start_year, end_year)
            ).all()
            
            
            return [row._asdict() for row in results]
        finally:
            session.close()

    def search_readers_by_book_title(self, book_name_pattern):
        session = self.Session()
        try:
            results = session.query(
                Reader.reader_id,
                Reader.last_name,
                Reader.first_name,
                Reader.email,
                Book.name.label('book_name')
            ).join(LoanJournal, Reader.reader_id == LoanJournal.id_reader)\
             .join(Book, LoanJournal.id_book == Book.book_id)\
             .filter(
                Book.name.ilike(book_name_pattern)
            ).order_by(Reader.last_name, Reader.first_name, Book.name).all()
            
            
            return [row._asdict() for row in results]
        finally:
            session.close()

    def search_loans_by_date_range(self, start_date, end_date):
        session = self.Session()
        try:
            results = session.query(
                LoanJournal.loan_id, 
                Book.name, 
                (Reader.last_name + ' ' + Reader.first_name).label('reader'), 
                LoanJournal.loan_date, 
                LoanJournal.return_date
            ).join(Book, LoanJournal.id_book == Book.book_id)\
             .join(Reader, LoanJournal.id_reader == Reader.reader_id)\
             .filter(
                LoanJournal.loan_date.between(start_date, end_date)
            ).order_by(LoanJournal.loan_date).all()
            
            
            return [row._asdict() for row in results]
        finally:
            session.close()

    # Аналітика (SELECT)

    def get_books_per_author(self, last_name_pattern):
        session = self.Session()
        try:
            from sqlalchemy import func
            
            results = session.query(
                Author.author_id,  
                Author.last_name,
                Author.first_name,
                func.count(Book.book_id).label('book_count')
            ).outerjoin(Book, Author.author_id == Book.id_author)\
             .filter(Author.last_name.ilike(last_name_pattern))\
             .group_by(Author.author_id, Author.last_name, Author.first_name)\
             .order_by(func.count(Book.book_id).desc(), Author.last_name)\
             .all()
            
            
            return [row._asdict() for row in results]
        finally:
            session.close()

    def get_top_10_readers(self):
        session = self.Session()
        try:
            from sqlalchemy import func
            
            results = session.query(
                Reader.reader_id,
                Reader.last_name,
                Reader.first_name,
                func.count(LoanJournal.loan_id).label('loan_count')
            ).join(LoanJournal, Reader.reader_id == LoanJournal.id_reader)\
             .group_by(Reader.reader_id, Reader.last_name, Reader.first_name)\
             .order_by(func.count(LoanJournal.loan_id).desc())\
             .limit(10)\
             .all()
            
            
            return [row._asdict() for row in results]
        finally:
            session.close()

    def get_avg_loan_duration(self):
        session = self.Session()
        try:
            from sqlalchemy import func
            
            avg_duration_query = func.avg(LoanJournal.return_date - LoanJournal.loan_date).label('avg_duration_days')
            
            results = session.query(avg_duration_query)\
                             .filter(LoanJournal.return_date.isnot(None), LoanJournal.return_date >= LoanJournal.loan_date)\
                             .all()
            
            return [{'avg_duration_days': results[0][0]}] if results else []
        finally:
            session.close()

    def close(self):
        print("З'єднання з БД закрито.")
