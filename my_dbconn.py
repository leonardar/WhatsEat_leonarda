import psycopg2
# from psycopg2 import Error
from bs4 import BeautifulSoup
import requests
import re


url_1 = 'https://retsepty.online.ua/bliny-oladi/'

def parse(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    category = soup.find('h1', class_='c-article__title c-article__title--retsepty').get_text(strip=True)
    items = soup.findAll('div', class_='recipe clear')

    titles = []
    urls = []
    for item in items:
        selector = item.find('div', class_='title')
        titles.append(selector.get_text(strip=True))
        urls.append(
            {
             'url': selector.find('a')
            }
        )

    recipes_urls = []
    for u in urls:
        link = u['url']['href']
        u['url']['href'] = f'https://retsepty.online.ua{link}'
        u = u['url']['href']
        recipes_urls.append(u)
    dic = dict(zip(titles, recipes_urls))

    return (category, dic)


parse(url_1)
url_2 = 'https://retsepty.online.ua/vtorye-blyuda/'
parse(url_2)
url_3 = 'https://retsepty.online.ua/deserty/'
parse(url_3)
url_4 = 'https://retsepty.online.ua/deserty/'
parse(url_4)
url_5 = 'https://retsepty.online.ua/domashnie-zagotovki/'
parse(url_5)
url_6 = 'https://retsepty.online.ua/zakuski/'
parse(url_6)
url_7 = 'https://retsepty.online.ua/zasol-ryby/'
parse(url_7)
url_8 = 'https://retsepty.online.ua/napitki/'
parse(url_8)
url_9 = 'https://retsepty.online.ua/natsionalnye-kuhni/'
parse(url_9)
url_10 = 'https://retsepty.online.ua/pervye-blyuda/'
parse(url_10)
url_11 = 'https://retsepty.online.ua/postnye-blyuda/'
parse(url_11)
url_12 = 'https://retsepty.online.ua/salaty/'
parse(url_12)
url_13 = 'https://retsepty.online.ua/sousy-podlivy/'
parse(url_13)


def parse_recipes(url):
    category, dic = parse(url)
    final_result = []
    for key, value in dic.items():
            result = []
            url = value
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            items = soup.find('div', class_='text')
            # print(f'тест приготовления {items}')
            it = str(items)
            start = it.find('Ингредиенты')
            start = it.find('</b>', start+1)
            end = it.find('<b>Способ', start+1)
            if start < 0 or end < 0:
                continue
            it = it[start + 4:end].replace(u'\xa0', u' ')
            it = re.sub('<div>|<p>|</p>|<b>|</b>', '', it)
            ing = re.split('<br/>|</div>', it)
            product_dish = []
            for st in ing:
                st = st.strip()
                if len(st) > 0:
                    if st.find('—') > 0:
                        st = st.split('—')[0]
                    else:
                        m = re.search(r'\d', st)
                        if m:
                            st = st[:m.start()]
                    st = st.strip()
                    if len(st):
                        product_dish.append(st)
            # print(f'продукт - блюдо {product_dish}')
            if len(product_dish):
                result.append(key)
                result.append(product_dish)
                result.append(items)
                final_result.append(result)
    # print(category, final_result)
    return category, tuple(final_result)


def db_fill(url):
    try:
        # Подключиться к существующей базе данных
        connection = psycopg2.connect(user="postgres",
                                       # пароль, который указан при установке PostgreSQL
                                       password="qwerty",
                                       host="127.0.0.1",
                                       port="5432",
                                       database="whatseat")

        cursor = connection.cursor()
        category, finalresult = parse_recipes(url)

        cursor.execute(f"""SELECT id FROM DishCat WHERE title = '{category}'""")
        if cursor.rowcount <= 0:
            cursor.execute(f"""INSERT INTO DishCat (TITLE) VALUES ('{category}') RETURNING id""")
        category_id = cursor.fetchone()[0]
        print('category_id =', category_id)

        for recipe in finalresult:
            dish_title = recipe[0]
            dish_description = recipe[2]
            insert_dish_query = f"""INSERT INTO Dish (TITLE, DESCRIPTION, DISHCAT_ID) VALUES ('{dish_title}', '{dish_description}', '{category_id}') RETURNING id"""
            print('insert_dish_query =', insert_dish_query)
            cursor.execute(insert_dish_query)

            dish_id = cursor.fetchone()[0]
            for product in recipe[1]:
                insert_product_query = f"""INSERT INTO Product (TITLE, dish_id) VALUES ('{product}', '{dish_id}') RETURNING id"""  # поменять связь на Блюда
                print('insert_product_query =', insert_product_query)
                cursor.execute(insert_product_query)

                product_id = cursor.fetchone()[0]
                insert_recipe_query = f""" INSERT INTO Recipe (dish_id, product_id) VALUES ('{dish_id}', '{product_id}')"""
                cursor.execute(insert_recipe_query)
        connection.commit()
        # print("1 запись успешно вставлена")
        # # Получить результат
        # cursor.execute("SELECT * dish_category_entity")
        # record = cursor.fetchall()
        # print("Результат", record)

    except (Exception) as error:
        print("Ошибка при работе с PostgreSQL", error)
    finally:
        if connection:
            cursor.close()
            connection.close()


db_fill(url_1)
db_fill(url_2)
db_fill(url_3)
db_fill(url_4)
db_fill(url_5)
db_fill(url_6)
db_fill(url_7)
db_fill(url_8)
db_fill(url_9)
db_fill(url_10)
db_fill(url_11)
db_fill(url_12)
db_fill(url_13)
