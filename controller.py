import time
from model import Model
from view import View

class Controller:
    def __init__(self):
        self.model = Model() 
        self.view = View()

    def run(self):
        try:
            while True:
                choice = self.view.show_main_menu()
                
                if choice == '1':
                    self.handle_view_menu()
                elif choice == '2':
                    self.handle_add_menu()
                elif choice == '3':
                    self.handle_edit_menu()
                elif choice == '4':
                    self.handle_delete_menu()
                elif choice == '5':
                    self.handle_generate_menu()
                elif choice == '6':
                    self.handle_search_menu()
                elif choice == '7':
                    self.handle_analytics_menu()
                elif choice == '0':
                    if self.view.get_confirmation("завершити роботу"):
                        break
                else:
                    self.view.show_message("Невідома опція, спробуйте ще раз.", is_error=True)
        finally:
            self.model.close()

    def _handle_dml_response(self, response_tuple, success_message):
        success, error_message = response_tuple
        if success:
            self.view.show_message(success_message)
        else:
            self.view.show_message(error_message, is_error=True)

    # Обробники підменю 

    def handle_view_menu(self):
        while True:
            choice = self.view.show_submenu('view')
            data = None 
            
            if choice == '1.1':
                data = self.model.get_authors()
            elif choice == '1.2':
                data = self.model.get_books()
            elif choice == '1.3':
                data = self.model.get_readers()
            elif choice == '1.4':
                data = self.model.get_loans()
            elif choice == '1.5':
                break
            else:
                self.view.show_message("Невідома опція.", is_error=True)
            
            if data is not None:
                self.view.show_data(data)

    def handle_add_menu(self):
        while True:
            choice = self.view.show_submenu('add')
            if choice == '2.1': 
                details = self.view.get_author_details()
                response = self.model.add_author(details['last_name'], details['first_name'], details['email'])
                self._handle_dml_response(response, "Автора успішно додано.")
                        
            elif choice == '2.2': 
                self.view.show_message("Порада: перегляньте ID авторів (меню 1.1) перед додаванням книги.")
                self.view.show_data(self.model.get_authors()) 
                details = self.view.get_book_details()
                
                author_id = details['id_author']
                if not self.model.get_entity_by_id("author", author_id):
                    self.view.show_message(f"Автора з ID {author_id} не існує.", is_error=True)
                    continue 

                response = self.model.add_book(details['name'], details['year_published'], details['pages'], author_id)
                self._handle_dml_response(response, "Книгу успішно додано.")
                        
            elif choice == '2.3': 
                details = self.view.get_reader_details()
                response = self.model.add_reader(details['last_name'], details['first_name'], details['email'])
                self._handle_dml_response(response, "Читача успішно додано.")

            elif choice == '2.4': 
                self.view.show_message("Порада: перегляньте ID книг (1.2) та читачів (1.3).")
                self.view.show_data(self.model.get_books())
                self.view.show_data(self.model.get_readers())
                
                details = self.view.get_loan_details()

                book_id = details['id_book']
                reader_id = details['id_reader']

                if not self.model.get_entity_by_id("book", book_id):
                    self.view.show_message(f"Книги з ID {book_id} не існує.", is_error=True)
                    continue
                if not self.model.get_entity_by_id("reader", reader_id):
                    self.view.show_message(f"Читача з ID {reader_id} не існує.", is_error=True)
                    continue
                
                book_details = self.model.get_book_validation_details(book_id)
                loan_date = details['loan_date']
                
                if book_details and loan_date.year < book_details['year_published']:
                    self.view.show_message(
                        f"Книгу '{book_details['name']}' (видана у {book_details['year_published']}р.) "
                        f"не можна було видати у {loan_date.year}р.", 
                        is_error=True
                    )
                    continue
                
                response = self.model.add_loan(book_id, reader_id, details['loan_date'], details['return_date'])
                self._handle_dml_response(response, "Запис про видачу успішно створено.")
            
            elif choice == '2.5':
                break
            else:
                self.view.show_message("Невідома опція.", is_error=True)

    def handle_edit_menu(self):
        while True:
            choice = self.view.show_submenu('edit')
            if choice == '3.1': 
                self.view.show_data(self.model.get_authors())
                author_id = self.view.get_id("автора для редагування")
                
                if not self.model.get_entity_by_id("author", author_id):
                    self.view.show_message(f"Автора з ID {author_id} не існує.", is_error=True)
                    continue
                
                details = self.view.get_author_details()
                response = self.model.update_author(author_id, details['last_name'], details['first_name'], details['email'])
                self._handle_dml_response(response, "Дані автора оновлено.")

            elif choice == '3.2': 
                self.view.show_data(self.model.get_books())
                book_id = self.view.get_id("книги для редагування")

                if not self.model.get_entity_by_id("book", book_id):
                    self.view.show_message(f"Книги з ID {book_id} не існує.", is_error=True)
                    continue
                
                self.view.show_data(self.model.get_authors())
                details = self.view.get_book_details()
                author_id = details['id_author']

                if not self.model.get_entity_by_id("author", author_id):
                    self.view.show_message(f"Автора з ID {author_id} не існує.", is_error=True)
                    continue

                response = self.model.update_book(book_id, details['name'], details['year_published'], details['pages'], author_id)
                self._handle_dml_response(response, "Дані книги оновлено.")
            
            elif choice == '3.3': 
                self.view.show_data(self.model.get_readers())
                reader_id = self.view.get_id("читача для редагування")
                
                if not self.model.get_entity_by_id("reader", reader_id):
                    self.view.show_message(f"Читача з ID {reader_id} не існує.", is_error=True)
                    continue

                details = self.view.get_reader_details()
                response = self.model.update_reader(reader_id, details['last_name'], details['first_name'], details['email'])
                self._handle_dml_response(response, "Дані читача оновлено.")

            elif choice == '3.4': 
                self.view.show_data(self.model.get_loans())
                loan_id = self.view.get_id("запису журналу для редагування")

                if not self.model.get_entity_by_id("LoanJournal", loan_id):
                    self.view.show_message(f"Запису журналу з ID {loan_id} не існує.", is_error=True)
                    continue
                
                details = self.view.get_loan_details()
                book_id = details['id_book']
                reader_id = details['id_reader']

                if not self.model.get_entity_by_id("book", book_id):
                    self.view.show_message(f"Книги з ID {book_id} не існує.", is_error=True)
                    continue
                if not self.model.get_entity_by_id("reader", reader_id):
                    self.view.show_message(f"Читача з ID {reader_id} не існує.", is_error=True)
                    continue
                
                book_details = self.model.get_book_validation_details(book_id)
                loan_date = details['loan_date']
                
                if book_details and loan_date.year < book_details['year_published']:
                    self.view.show_message(
                        f"Книгу '{book_details['name']}' (видана у {book_details['year_published']}р.) "
                        f"не можна було видати у {loan_date.year}р.", 
                        is_error=True
                    )
                    continue
                
                response = self.model.update_loan(loan_id, book_id, reader_id, details['loan_date'], details['return_date'])
                self._handle_dml_response(response, "Запис журналу оновлено.")

            elif choice == '3.5':
                break
            else:
                self.view.show_message("Невідома опція.", is_error=True)

    def handle_delete_menu(self):
        while True:
            choice = self.view.show_submenu('delete')
            
            if choice == '4.1': 
                self.view.show_data(self.model.get_authors())
                author_id = self.view.get_id("автора для видалення")

                if not self.model.get_entity_by_id("author", author_id):
                    self.view.show_message(f"Автора з ID {author_id} не існує.", is_error=True)
                    continue

                if self.view.get_confirmation(f"видалити автора ID={author_id}"):
                    response = self.model.delete_author(author_id)
                    self._handle_dml_response(response, "Автор видалений.")

            elif choice == '4.2': 
                self.view.show_data(self.model.get_books())
                book_id = self.view.get_id("книги для видалення")

                if not self.model.get_entity_by_id("book", book_id):
                    self.view.show_message(f"Книги з ID {book_id} не існує.", is_error=True)
                    continue

                if self.view.get_confirmation(f"видалити книгу ID={book_id}"):
                    response = self.model.delete_book(book_id)
                    self._handle_dml_response(response, "Книга видалена.")
            
            elif choice == '4.3':
                self.view.show_data(self.model.get_readers())
                reader_id = self.view.get_id("читача для видалення")

                if not self.model.get_entity_by_id("reader", reader_id):
                    self.view.show_message(f"Читача з ID {reader_id} не існує.", is_error=True)
                    continue

                if self.view.get_confirmation(f"видалити читача ID={reader_id}"):
                    response = self.model.delete_reader(reader_id)
                    self._handle_dml_response(response, "Читач видалений.")

            elif choice == '4.4': 
                self.view.show_data(self.model.get_loans())
                loan_id = self.view.get_id("запису журналу для видалення")
                
                if not self.model.get_entity_by_id("LoanJournal", loan_id):
                    self.view.show_message(f"Запису журналу з ID {loan_id} не існує.", is_error=True)
                    continue

                if self.view.get_confirmation(f"видалити запис журналу ID={loan_id}"):
                    response = self.model.delete_loan(loan_id)
                    self._handle_dml_response(response, "Запис журналу видалений.")
            
            elif choice == '4.5':
                break
            else:
                self.view.show_message("Невідома опція.", is_error=True)

    def handle_generate_menu(self):
        while True:
            choice = self.view.show_submenu('generate')
            if choice in ['5.1', '5.2', '5.3', '5.4']:
                
                count = self.view.get_generation_count()
                if count <= 0:
                    self.view.show_message("Кількість має бути > 0.", is_error=True)
                    continue
                
                self.view.show_message(f"Генерація {count} записів...")
                response = (False, "Невідома помилка генерації")
                
                start_time = time.perf_counter()
                
                if choice == '5.1':
                    response = self.model.generate_authors(count)
                elif choice == '5.2':
                    response = self.model.generate_books(count)
                elif choice == '5.3':
                    response = self.model.generate_readers(count)
                elif choice == '5.4':
                    response = self.model.generate_loans(count)
                
                end_time = time.perf_counter()
                duration_sec = end_time - start_time
                
                success_message = f"Успішно згенеровано {count} записів за {duration_sec:.4f} сек."
                
                self._handle_dml_response(response, success_message)

            elif choice == '5.5':
                break
            else:
                self.view.show_message("Невідома опція.", is_error=True)

    def _measure_query(self, func, *args):
        start_time = time.perf_counter()
        results = func(*args)
        end_time = time.perf_counter()
        execution_ms = (end_time - start_time) * 1000
        return results, execution_ms

    def handle_search_menu(self):
        while True:
            choice = self.view.show_submenu('search')
            results, time_ms = (None, 0) 
            
            if choice == '6.1': 
                author_last_name, start_year, end_year = self.view.get_search_params_6_1()
                results, time_ms = self._measure_query(self.model.search_books_by_author_year, author_last_name, start_year, end_year)

            elif choice == '6.2': 
                book_name = self.view.get_search_params_6_2()
                search_pattern = f"{book_name}%"
                results, time_ms = self._measure_query(
                    self.model.search_readers_by_book_title, 
                    search_pattern  
                )

            elif choice == '6.3': 
                start_date, end_date = self.view.get_search_params_6_3()
                results, time_ms = self._measure_query(self.model.search_loans_by_date_range, start_date, end_date)
            
            elif choice == '6.4':
                break
            else:
                self.view.show_message("Невідома опція.", is_error=True)
            
            if results is not None:
                self.view.show_data(results)
                self.view.show_execution_time(time_ms)
            elif choice != '6.4':
                 self.view.show_message("Пошук не дав результатів або сталася помилка.", is_error=True)


    def handle_analytics_menu(self):
        while True:
            choice = self.view.show_submenu('analytics')
            results, time_ms = (None, 0)
            
            if choice == '7.1': 
                last_name_part = self.view.get_analytics_params_7_1()
                if last_name_part:
                    search_pattern = f"{last_name_part}%"
                else:
                    search_pattern = "%"
                results, time_ms = self._measure_query(
                    self.model.get_books_per_author, 
                    search_pattern
                )

            elif choice == '7.2': 
                results, time_ms = self._measure_query(self.model.get_top_10_readers)

            elif choice == '7.3': 
                results, time_ms = self._measure_query(self.model.get_avg_loan_duration)

            elif choice == '7.4':
                break
            else:
                self.view.show_message("Невідома опція.", is_error=True)

            if results is not None:
                self.view.show_data(results)
                self.view.show_execution_time(time_ms)
            elif choice != '7.4':
                 self.view.show_message("Аналітика не дала результатів або сталася помилка.", is_error=True)