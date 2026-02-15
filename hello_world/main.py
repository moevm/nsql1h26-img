import sys
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError


from db import get_config


def run_hello_world():
    config = get_config()
    try:
        # Подключение
        with MongoClient(config.mongo_url,
                         serverSelectionTimeoutMS=5000) as client:
            # Проверка доступности сервера
            ping_response = client.admin.command('ping')
            print(f"Подключение к MongoDB успешно: {ping_response=}")

            db = client[config.db_name]
            collection = db["test_collection"]

            # Запись данных
            data = {"version": 1, "info": "Hello World Test"}
            insert_id = collection.insert_one(data).inserted_id
            print(f"Данные записаны. ObjectId={insert_id}")

            # Чтение данных
            result = collection.find_one({"_id": insert_id})
            print(f"Данные из БД: {result}")

            # Обновление данных
            update_data = {
                "$set": {"info": "Updated Hello World Test"},
                "$inc": {"version": 1}
            }
            collection.update_one({"_id": insert_id}, update_data)

            # Проверка обновления
            updated_result = collection.find_one({"_id": insert_id})
            print(f"Данные после обновления: {updated_result}")

            # Очистка
            collection.delete_one({"_id": insert_id})
            print("Тестовые данные удалены.")

    except ConnectionFailure:
        print("Не удалось подключиться к MongoDB")
        sys.exit(1)
    except PyMongoError as db_error:
        print(f"Ошибка при выполнении операции в БД: {db_error}")
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(f"Неизвестная ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_hello_world()
