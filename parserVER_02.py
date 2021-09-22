import psycopg2
# from psycopg2 import Error
from bs4 import BeautifulSoup
import requests
import re
import urllib.request
import urllib.request
import os


chicken_url = 'https://worldrecipes.eu/ru/category/bliuda-iz-kuricy'
dinner_url = 'https://worldrecipes.eu/ru/category/bliuda-na-uzhin'
dessert_url = 'https://worldrecipes.eu/ru/category/deserty'
meatdishes_url = 'https://worldrecipes.eu/ru/category/miasnyje-bliuda'

dir = 'src/main/resources/static/sample/img'

def get_image(image_url):
    img_data = requests.get(image_url).content
    filename = os.path.basename(image_url)
    path = os.path.join(dir, filename)
    with open(path, 'wb') as handler:
        handler.write(img_data)
    return path

def parse_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    items = soup.findAll('a', class_='tile is-child with-hover')
    recipes_urls = []
    for elem in items:
        link = elem['href']
        recipes_urls.append(link)
    # print(recipes_urls)
    return recipes_urls

chilen_list = parse_url(chicken_url)
dinner_list = parse_url(dinner_url)
dessert_list = parse_url(dessert_url)
meatdishes_list = parse_url(meatdishes_url)

def print_dict(d):
    for title, inner_d in d.items():
        print(title)
        k = 'Изображение'
        print(f'\t{k}')
        print(f'\t\t{inner_d[k]}')
        k = 'Путь к изображению'
        print(f'\t{k}')
        print(f'\t\t{inner_d[k]}')
        k = 'Список ингредиентов'
        print(f'\t{k}')
        for i in inner_d[k]:
            print(f'\t\t{i}')
        k = 'Способ приготовления'
        print(f'\t{k}')
        for i in inner_d[k]:
            print(f'\t\t{i}')
        print('\n')


def parse_recipes(urls):
    dct = {}
    for url in urls:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.find('h1', class_ = 'has-text-weight-bold breadcrumb-title').get_text(strip=True)
        # timer = soup.find('div', class_ = 'has-text-centered').get_text(strip=True)
        # print(timer)
        image = soup.find('picture', class_ = 'recipe-cover-img')
        image = image.find('img')['src']
        path = get_image(image)
        ingredients = soup.find('div', 'card-content recipe')
        final_list = ingredients.find('ul')
        final_list = final_list.findAll('li')
        lst = []
        for item in final_list:
            item = str(item)
            item = item[4:len(item)-5]
            # item.capitalize()
            lst.append(item)

        value_dict = {}
        value_dict['Список ингредиентов'] = lst
        value_dict['Изображение'] = image
        value_dict['Путь к изображению'] = path

        text = soup.find('ol', class_ = 'p-t-2')
        text_list = text.findAll('li')
        new_list = text_list [:-1]

        new_list2 = []
        for i in new_list:
            i = str(i)
            num, step = i.split('</span>')
            num = num[num.rfind('>')+1:].strip()
            step = step.strip()
            new_list2.append(f'<li>{step}')
        value_dict['Способ приготовления'] = new_list2
        dct[title] = value_dict
    print_dict(dct)
    return dct

dct_chilen_list= parse_recipes(chilen_list)
dct_dinner_list = parse_recipes(dinner_list)
dct_dessert_list = parse_recipes(dessert_list)
dct_meatdishes_list = parse_recipes(meatdishes_list)

def db_fill(lst, name):
    try:
        # Подключиться к существующей базе данных
        connection = psycopg2.connect(user="postgres",
                                       # пароль, который указан при установке PostgreSQL
                                       password="qwerty",
                                       host="127.0.0.1",
                                       port="5432",
                                       database="whatseat")

        cursor = connection.cursor()

        cursor.execute(f"""SELECT id FROM dish_category_entity WHERE title = '{name}'""")
        if cursor.rowcount <= 0:
            cursor.execute(f"""INSERT INTO dish_category_entity (TITLE) VALUES ('{name}') RETURNING id""")

        category_id = cursor.fetchone()[0]
        print('category_id =', category_id)
#
        for key, value in lst.items():
            dish_title = key
            dish_ingredients= '\n'.join(value['Список ингредиентов'])
            dish_cooking_method = '\n'.join(value['Способ приготовления'])
            dish_img_link = value['Изображение']
            dish_img_path = value['Путь к изображению']
            insert_dish_query = f"""INSERT INTO dish_entity (TITLE, DESCRIPTION, ingredients_list, img_path, DISH_CAT_ID) VALUES ('{dish_title}', '{dish_cooking_method}', '{dish_ingredients}','{dish_img_path}', '{category_id}') RETURNING id"""
            print('insert_dish_query =', insert_dish_query)
            cursor.execute(insert_dish_query)
#
            dish_id = cursor.fetchone()[0]

            dish_ingredients = value['Список ингредиентов']
            for ing in dish_ingredients:
                print(ing)
                num = ing.count(':')
                if num == 1:
                    product, quantity = ing.split(':')
                    insert_product_query = f"""INSERT INTO product_entity (TITLE) VALUES ('{product}') RETURNING id"""
                else:
                    product = ing
                    insert_product_query = f"""INSERT INTO product_entity (TITLE) VALUES ('{product}') RETURNING id"""

                cursor.execute(insert_product_query)
                product_id = cursor.fetchone()[0]
                insert_recipes_query = f"""INSERT INTO recipes (QUANTITY, dish_id, product_id) VALUES ('{quantity}','{dish_id}','{product_id}') RETURNING id"""
#                 print('insert_product_query =', insert_product_query)

                cursor.execute(insert_recipes_query)
        connection.commit()
        # print("1 запись успешно вставлена")
        # # Получить результат
        # cursor.execute("SELECT * dish_category_entity")
        # record = cursor.fetchall()
        # print("Результат", record)
#
    except (Exception) as error:
        print("Ошибка при работе с PostgreSQL", error)
    finally:
        if connection:
            cursor.close()
            connection.close()

db_fill(dct_chilen_list, 'Блюда из курицы')
db_fill(dct_dinner_list, 'Блюда на ужин' )
db_fill(dct_dessert_list, 'Десерты')
db_fill(dct_meatdishes_list, 'Мясные блюда')

