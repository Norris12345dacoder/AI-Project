from bs4 import BeautifulSoup
import requests
from selenium import webdriver
import time
import json
driver = webdriver.Chrome()
driver.implicitly_wait(60)
date = input("Date (e.g. 2026-04-29): ")
with open("code.txt") as file:
    code = file.read()
codeSoup = BeautifulSoup(code, "html.parser")
countries = codeSoup.find_all("span", class_ = "")
for i in range(len(countries)):
    countries[i] = countries[i].text
    if countries[i] == "Worldwide":
        countries[i] = "world"
        continue
    countries[i] = countries[i].replace(" ", "-")
    countries[i] = countries[i].lower()
print(countries)
def getDataByCountry(country):
    driver.get(f"https://flixpatrol.com/top10/netflix/{country}/{date}/")
    soup = BeautifulSoup(driver.page_source, "html.parser")
    moviesList = soup.find_all("tr", "table-group")
    for i in range(2):
        if len(moviesList) > 0:
            moviesList.pop()
    movies = [[], [], [], []]
    moviesCategories = soup.find_all("h3", class_ = "font-semibold text-sm text-gray-100")
    for i in range(len(moviesCategories)):
        if i <= 3:
            moviesCategories[i] = moviesCategories[i].text
        else:
            moviesCategories.pop()
    listNo = 0
    fullDictionary = {}
    for i in range(len(moviesList)):
        movies[listNo].append(moviesList[i].find("a", class_ = "hover:underline").text)
        if (i + 1) % 10 == 0 and i != 0:
            listNo += 1
        if moviesList[i].find("a", class_ = "hover:underline").text == "50":
            break
    for i in range(len(moviesCategories)):
        fullDictionary[moviesCategories[i]] = movies[i]
    return fullDictionary
allDictionary = {}
for i in range(len(countries)):
    print(getDataByCountry(countries[i]))
    allDictionary[countries[i]] = getDataByCountry(countries[i])
with open("data2.json", "w") as file:
    json.dump(allDictionary, file)