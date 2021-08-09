import requests
from bs4 import BeautifulSoup
import concurrent.futures

from DatabaseManager import DatabaseManager

MAX_THREADS = 100


class BBCGoodFoods:

    def __init__(self):
        self.database_manager = DatabaseManager('recipe.db')

    def create_base_table(self):
        """
        Creates the base BBC table
        :return:
        """
        bbc_table = ('''CREATE TABLE IF NOT EXISTS BBCRECIPE(
            recipeName text NOT NULL,
            ingredients text NOT NULL,
            method text NOT NULL);''')
        self.database_manager.db_execute_commit(bbc_table)

    def create_possible_urls(self):
        """
        Iterates through the letters of the alphabet to generate URLs from
        :return: A total list of valid URLs
        """
        url_list = []
        for i in range(97, 123):
            url_list.append(self.make_urls_for_letter(chr(i)))
        return url_list

    def make_urls_for_letter(self, letter):
        """
        Checks all possible pages of recipes for a given letter and returns a list of valid URLs.
        :param letter: The letter that is to be tests for valid URLs
        :return: A list of URLs that don't error when called.
        """
        urls = []
        for j in range(1, 100):
            new_url = "https://www.bbc.co.uk/food/recipes/a-z/" + str(letter) + "/" + str(j) + "#featured-content"
            urls.append(new_url)
            request = requests.head(new_url)
            if request.status_code == 200:
                urls.append(new_url)
            else:
                break
        return urls

    def get_recipe_url(self, urls):
        """
        Goes through each page of recipes to pick out the URLs of the actual recipe pages.
        :param urls: A list of valid URLs previous gotten.
        :return: A list of valid URLs for the actual recipe pages.
        """
        recipe_url = []
        for i in urls:
            page = requests.get(i)
            soup = BeautifulSoup(page.content, "html.parser")
            thing = soup.findAll(class_="promo")
            for j in thing:
                recipe_url.append(j.get("href"))
        return list(set(recipe_url))

    def get_data_from_urls(self, urls):
        """
        Creates multiple threads to save data taken from the recipe page URL
        :param urls: A list of valid URLs for the actual recipe pages.
        :return:
        """
        threads = min(MAX_THREADS, len(urls))

        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
            executor.map(self.commit_data_from_url, urls)

    def commit_data_from_url(self, url):
        """
        Gets the recipe name, ingredient list and method list from the page and then commits to the database.
        :param url: URL of the recipe page.
        :return:
        """
        recipe_url = "https://www.bbc.co.uk/" + str(url)
        page = requests.get(recipe_url)

        soup = BeautifulSoup(page.content, "html.parser")

        name_first = soup.find(class_="gel-trafalgar content-title__text")
        if name_first is None:
            return
        else:
            name = name_first.text

        ingredient_soup_results = soup.findAll(class_="recipe-ingredients__list-item")
        ingredients = []
        for ingredient in ingredient_soup_results:
            ingredients.append(ingredient.text)

        method_soup_results = soup.findAll(class_="recipe-method__list-item-text")
        method = []
        for method_step in method_soup_results:
            method.append(method_step.text)

        self.put_recipe_in_db(name, '|'.join(ingredients), '|'.join(method))

    def put_recipe_in_db(self, name, ingredients, method):
        """
        Commits the recipe to the database when given the name, ingredient list and method list.
        :param name: Name of the recipe
        :param ingredients: List of ingredients separated by |
        :param method: Method list, separated by |
        :return:
        """
        self.database_manager.db_execute_commit(
            """INSERT INTO BBCRECIPE (recipeName, ingredients, method) VALUES (?, ?, ?);""",
            args=[name, ingredients, method]
        )

    def execute(self):
        print("Starting")
        urls = self.get_recipe_url(self.create_possible_urls())
        print("HERE")
        self.get_data_from_urls(urls)


if __name__ == "__main__":
    fill_database = BBCGoodFoods()
    fill_database.execute()
