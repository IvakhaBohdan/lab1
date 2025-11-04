from controller import Controller

if __name__ == "__main__":
    try:
        controller = Controller()
        controller.run()
    except Exception as e:
        print(f"Виникла критична помилка: {e}")
    finally:
        print("\nРоботу програми завершено.")