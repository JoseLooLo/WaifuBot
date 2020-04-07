import requests
import sqlite3
from random import randint
from bs4 import BeautifulSoup

class Crawler:
    def __init__(self):
        self.base_url = "https://myanimelist.net/character/"
        database = "waifuDB.db"
        self.conn = self.create_connection(database)
        # i = self.findLastCharacterMyAnimeList()
        # while (True):
        #     self.crawler(i)
        #     i+=1
        self.crawler(14)

    def create_connection(self, database):
        try:
            conn = sqlite3.connect(database)
            return conn
        except:
            print("Erro ao conectar na database")
            exit(0)
        return None

    def findLastCharacterMyAnimeList(self):
        try:
            max_value = 1
            cur = self.conn.cursor()
            cur.execute("SELECT max(myanimelist_id) FROM Anime_Waifu")
            row = cur.fetchone()
            if row[0] is not None:
                max_value = int(row[0])

            cur = self.conn.cursor()
            cur.execute("SELECT max(myanimelist_id) FROM Manga_Waifu")
            row = cur.fetchone()
            if row[0] is not None:
                temp_value = int(row[0])
                if temp_value > max_value:
                    max_value = temp_value
            return max_value
        except Exception as e:
            print("[ERROR] - {}".format(e))

    def insertAnime(self, waifu_name, waifu_nickname, gender, img, anime, myanimelist_id):
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT * FROM Anime_Waifu where myanimelist_id = ?", (myanimelist_id,))
            row = cur.fetchone()
            if row is not None:
                return
            cmd = "INSERT INTO Anime_Waifu (name, nickname, gender, img, anime, popularity, myanimelist_id) VALUES (?, ?, ?, ?, ?, ?, ?);"
            self.conn.execute(cmd, (waifu_name, waifu_nickname, gender, img, anime, 0, myanimelist_id,))
            self.conn.commit()
        except Exception as e:
            print("[ERROR] - {}".format(e))

    def insertManga(self, waifu_name, waifu_nickname, gender, img, manga, myanimelist_id):
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT * FROM Manga_Waifu where myanimelist_id = ?", (myanimelist_id,))
            row = cur.fetchone()
            if row is not None:
                return
            cmd = "INSERT INTO Manga_Waifu (name, nickname, gender, img, manga, popularity, myanimelist_id) VALUES (?, ?, ?, ?, ?, ?, ?);"
            self.conn.execute(cmd, (waifu_name, waifu_nickname, gender, img, manga, 0, myanimelist_id,))
            self.conn.commit()
        except Exception as e:
            print("[ERROR] - {}".format(e))

    def getHeaderFirefox(self):
        headers_firefox = {
            'Host': 'pergamum.ufsc.br',
            'Connection': 'keep-alive',
            'Content-Length': '106',
            'Cache-Control': 'max-age=0',
            'Origin': 'https://pergamum.ufsc.br',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Referer': 'https://pergamum.ufsc.br/pergamum/biblioteca_s/php/login_usu.php?flag=index.php',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cookie': '__utmt=1; __utma=235133312.539375779.1563394688.1563394688.1563394688.1; __utmb=235133312.1.10.1563394688; __utmc=235133312; __utmz=235133312.1563394688.1.1.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); PHPSESSID=b195ee14a8a4e575c266991ca05e5016; _ga=GA1.2.539375779.1563394688; _gid=GA1.2.1688960623.1563394708; _gat_gtag_UA_10538459_9=1'
        }
        return headers_firefox

    def crawler(self, waifu_id):
        r = requests.get(self.base_url+str(waifu_id))
        soup = BeautifulSoup(r.text, 'html.parser')
        try:
            name = soup.find_all('span', class_='h1-title')

            nickname_waifu = ""
            name_waifu = name[0].get_text()
            first = name_waifu.find("\"")
            if (first != -1):
                second = name_waifu.find("\"", (first+1) )
                nickname_waifu = name_waifu[(first+1): second]
                name_waifu = name_waifu.replace(name_waifu[first:(second+1)], "").strip()
                name_waifu = " ".join(name_waifu.split())
            else:
                name_waifu = " ".join(name_waifu.split())

            img = soup.find_all('img', {"class": "lazyload"})
            img_waifu = img[0]['data-src']

            anime_name = ""
            manga_name = ""

            search = soup.find_all('td', {"class": "borderClass"})
            for i in search:
                anime = i.find_all('a', {"title": "Quick add anime to my list"})
                if len(anime) == 1 and anime_name == "":
                    name = i.find_all('a')
                    anime_name = name[0].get_text()

                manga = i.find_all('a', {"title": "Quick add manga to my list"})
                if len(manga) == 1 and manga_name == "":
                    name = i.find_all('a')
                    manga_name = name[0].get_text()

            print("{} # {}".format(name_waifu, nickname_waifu))
            print(img_waifu)
            print("{} $ {}".format(anime_name, manga_name))

            if manga_name != "":
                self.insertManga(str(name_waifu), str(nickname_waifu), 'N', str(img_waifu), str(manga_name), int(waifu_id))
            if anime_name != "":
                self.insertAnime(str(name_waifu), str(nickname_waifu), 'N', str(img_waifu), str(anime_name), int(waifu_id))

        except Exception as e:
            print("[ERROR] - {}".format(e))
        

if __name__ == "__main__":
    Crawler()