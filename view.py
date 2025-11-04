from datetime import datetime

class View:
    
    def show_message(self, message, is_error=False):
        if is_error:
            print(f"Помилка: {message}")
        else:
            print(f"{message}")

    def get_input(self, prompt, required_type=str, allow_empty=False):
        while True:
            val = input(f"{prompt}: ").strip()
            if not val and allow_empty:
                return None
            if not val and not allow_empty:
                print("Ввід не може бути порожнім.")
                continue
            
            try:
                if required_type == int:
                    return int(val)
                if required_type == "date":
                    return datetime.strptime(val, "%Y-%m-%d").date()
                return str(val)
            except ValueError:
                if required_type == int:
                    print("Введіть коректне число.")
                elif required_type == "date":
                    print("Введіть дату у форматі РРРР-ММ-ДД (наприклад, 2023-10-25).")
                else:
                    print("Некоректний ввід.")

    def show_main_menu(self):
        print("\n=== ГОЛОВНЕ МЕНЮ БІБЛІОТЕКИ ===\n")
        print("1. Перегляд даних")
        print("2. Додавання запису")
        print("3. Редагування запису")
        print("4. Видалення запису")
        print("5. Генерація випадкових даних")
        print("6. Пошук за параметрами")
        print("7. Аналітичні запити")
        print("0. Вихід із програми")
        return self.get_input("Виберіть опцію", required_type=str)

    def show_submenu(self, menu_type):
        menus = {
            'view': [
                "1.1. Переглянути таблицю 'Автори'",
                "1.2. Переглянути таблицю 'Книги'",
                "1.3. Переглянути таблицю 'Читачі'",
                "1.4. Переглянути таблицю 'Журнал видачі'",
                "1.5. Повернутися до головного меню"
            ],
            'add': [
                "2.1. Додати нового автора",
                "2.2. Додати нову книгу",
                "2.3. Додати нового читача",
                "2.4. Зареєструвати видачу книги",
                "2.5. Повернутися до головного меню"
            ],
            'edit': [
                "3.1. Редагувати дані автора",
                "3.2. Редагувати дані книги",
                "3.3. Редагувати дані читача",
                "3.4. Редагувати запис журналу видачі",
                "3.5. Повернутися до головного меню"
            ],
            'delete': [
                "4.1. Видалити автора",
                "4.2. Видалити книгу",
                "4.3. Видалити читача",
                "4.4. Видалити запис журналу видачі",
                "4.5. Повернутися до головного меню"
            ],
            'generate': [
                "5.1. Згенерувати випадкових авторів",
                "5.2. Згенерувати випадкові книги",
                "5.3. Згенерувати випадкових читачів",
                "5.4. Згенерувати випадкові записи журналу",
                "5.5. Повернутися до головного меню"
            ],
            'search': [
                "6.1. Пошук книг за автором і роком видання",
                "6.2. Пошук читачів, які отримували певну книгу",
                "6.3. Пошук видач у певному періоді",
                "6.4. Повернутися до головного меню"
            ],
            'analytics': [
                "7.1. Кількість виданих книг по кожному автору",
                "7.2. Топ-10 найактивніших читачів",
                "7.3. Середній час користування книгою",
                "7.4. Повернутися до головного меню"
            ]
        }
        
        if menu_type not in menus:
            print("Помилка: невідомий тип меню.")
            return None
        
        print(f"\n--- {menu_type.upper()} MENU ---")
        for item in menus[menu_type]:
            print(item)
        return self.get_input("Ваш вибір", required_type=str)

    def show_data(self, data):
        if not data:
            print("- Немає даних для відображення")
            return

        try:
            headers = data[0].keys()
            print("\n" + " | ".join(headers))
            print("-" * 80) 

            for row in data:
                values = [str(value) for value in row.values()]
                
                print(" | ".join(values))
                
            print("-" * 80)

        except Exception as e:
            print(f"Помилка у show_data: {e}")

    def get_confirmation(self, action):

        while True:
            choice = input(f"Ви впевнені, що хочете {action}? (y/n): ").lower()
            if choice == 'y':
                return True
            if choice == 'n':
                return False

    def show_execution_time(self, time_ms):
        print(f"Запит виконано за {time_ms:.3f} мс.")

    # Методи для отримання даних для сутностей 

    def get_author_details(self):
        print("\n--- Введіть дані автора ---")
        last_name = self.get_input("Прізвище (last_name)")
        first_name = self.get_input("Ім'я (first_name)")
        email = self.get_input("Email (приклад: test@mail.com)")
        return {'last_name': last_name, 'first_name': first_name, 'email': email}

    def get_reader_details(self):
        print("\n--- Введіть дані читача ---")
        last_name = self.get_input("Прізвище (last_name)")
        first_name = self.get_input("Ім'я (first_name)")
        email = self.get_input("Email (приклад: reader@mail.com)")
        return {'last_name': last_name, 'first_name': first_name, 'email': email}

    def get_book_details(self):
        print("\n--- Введіть дані книги ---")
        name = self.get_input("Назва (name)")
        year_published = self.get_input("Рік видання (year_published)", required_type=int)
        pages = self.get_input("Кількість сторінок (pages)", required_type=int)
        id_author = self.get_input("ID Автора (id_author)", required_type=int)
        return {'name': name, 'year_published': year_published, 'pages': pages, 'id_author': id_author}

    def get_loan_details(self):
        print("\n--- Введіть дані про видачу ---")
        id_book = self.get_input("ID Книги (id_book)", required_type=int)
        id_reader = self.get_input("ID Читача (id_reader)", required_type=int)
        loan_date = self.get_input("Дата видачі (loan_date, РРРР-ММ-ДД)", required_type="date")
        return_date = self.get_input("Дата повернення (return_date, РРРР-ММ-ДД або Enter)", required_type="date", allow_empty=True)
        return {'id_book': id_book, 'id_reader': id_reader, 'loan_date': loan_date, 'return_date': return_date}

    def get_id(self, entity_name):
        return self.get_input(f"Введіть ID для {entity_name}", required_type=int)

    def get_generation_count(self):
        return self.get_input("Введіть кількість записів для генерації", required_type=int)

    # Методи для отримання параметрів пошуку

    def get_search_params_6_1(self):
        print("\n--- Пошук книг за автором і роком ---")
        author_last_name = self.get_input("Прізвище автора (last_name)")
        start_year = self.get_input("Рік видання (ВІД, year_published)", required_type=int)
        end_year = self.get_input("Рік видання (ДО, year_published)", required_type=int)
        return author_last_name, start_year, end_year

    def get_search_params_6_2(self):
        print("\n--- Пошук читачів за назвою книги ---")
        book_name = self.get_input("Назва книги (name, можна частину)")
        return book_name

    def get_search_params_6_3(self):
        print("\n--- Пошук видач за періодом ---")
        start_date = self.get_input("Дата (ВІД, loan_date), РРРР-ММ-ДД", required_type="date")
        end_date = self.get_input("Дата (ДО, loan_date), РРРР-ММ-ДД", required_type="date")
        return start_date, end_date
    
    def get_analytics_params_7_1(self):
        self.show_message(
            "Порада: Введіть прізвище (або його частину) для фільтрації.\n"
            "       Або залиште поле порожнім, щоб побачити всіх авторів."
        )
        last_name_part = self.get_input(
            "Введіть прізвище [Enter для всіх]:",
            allow_empty=True  
        )
        return last_name_part