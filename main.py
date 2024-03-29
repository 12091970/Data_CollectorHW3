#Установите MongoDB на локальной машине, а также зарегистрируйтесь в онлайн-сервисе. https://www.mongodb.com/ https://www.mongodb.com/products/compass
#Загрузите данные который вы получили на предыдущем уроке путем скрейпинга сайта с помощью Buautiful Soup в MongoDB и создайте базу данных и коллекции для их хранения.
#Поэкспериментируйте с различными методами запросов.
#Зарегистрируйтесь в ClickHouse.
#Загрузите данные в ClickHouse и создайте таблицу для их хранения.

import json
from pymongo import MongoClient



# Чтение данных из JSON файла
with open("books_from_books.toscrape.com.json", "r", encoding='utf-8') as file:
    data = json.load(file)

### Проверка загрузки на примере первой записи
print(data[0])

# Соединение с MongoDB
client = MongoClient('localhost', 27017)
db = client['books_']

# Создание коллекции на основании данных из JSON файла
spisok_names = "Список книг"
for item in data:
    spisok = db[spisok_names]
    spisok.insert_one(item)

client.close()

# Установление связи с MongoDB
client = MongoClient('localhost', 27017)
db = client['books_']
spisok = db['Список книг']

#### Просмотр количества документов в коллекции
document_count = spisok.count_documents({})
print("Количество документов в коллекции:", document_count)

#Запрос количества и названий книг, дороже 50 фунтов
query = {"Цена в фунтах стерлингов": {"$gt": 59.0}}

# Получения документов, соответствующих запросу
documents = spisok.find(query)

print("Количество книг дороже 59 фунтов - ", spisok.count_documents(query), ":")

# Отображение названий книг
for document in documents:
    print("Название книги:", document['Название'])

# Создание конвеера для разбиения всех книг по стоимости на три категории: низкая стоимость (дешевле 15 фунтов), средня стоимость (от 15 до 25 фунтов) и высокая стоимость (выше 25 фунтов).
# Затем подсчет количества книг в каждой категории агрегацией по полю "Количество в наличии"
pipeline_by_group = [
    {
        "$group": {
            "_id": {
                "$cond": {
                    "if": {"$lte": ["$Цена в фунтах стерлингов", 15]},
                    "then": "Низкая стоимость",
                    "else": {
                        "$cond": {
                            "if": {"$lte": ["$Цена в фунтах стерлингов", 25]},
                            "then": "Средная стоимость",
                            "else": "Высокая стоимость"
                        }
                    }
                }
            },
            "Количество в наличии": {"$sum": "$Количество в наличии"}
        }
    }
]

# Выполнение конвеера
result_by_group = list(spisok.aggregate(pipeline_by_group))

# Печать результатов
for category in result_by_group:
    print("Категория по стоимости:", category["_id"])
    print("Количество в наличии:", category["Количество в наличии"])
    print()

# Создание конвеера для определения суммарного количества всех книг по полю "Количество в наличии"
pipeline_total_count = [
    {
        "$group": {
            "_id": None,
            "total_count": {"$sum": "$Количество в наличии"}
        }
    }
]

# Выполнение конвеера
result_total_count = list(spisok.aggregate(pipeline_total_count))

# Отображение результата
total_count = result_total_count[0]['total_count'] if result_total_count else 0
print("Общее количество книг в наличии:", total_count) #### совпадает с суммой книг в наличии по категориям стоимости






