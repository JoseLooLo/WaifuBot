import sqlite3
import abc
from random import randint

class DB:
    def __init__(self):
        self.database = "waifuDB.db"
        self.qnt_waifus = -1
        #times
        self.time_min_spawn = 180
        self.time_max_spawn = 300
        self.time_min_run = 30
        self.time_max_run = 60

        self.conn = self.create_connection(self.database)
        self.getQntWaifus()

    def create_connection(self, database):
        try:
            conn = sqlite3.connect(database)
            print("[DataBase] - Conectado com a database {}".format(self.database))
            return conn
        except:
            raise Exception("Erro ao conectar na database")

    def getQntWaifus(self):
        cur = self.conn.cursor()
        cur.execute("SELECT id FROM Anime_Waifu")
        rows = cur.fetchall()
        self.qnt_waifus = len(rows)
        print("[QntAnimeWaifus] - {}".format(self.qnt_waifus))

    def newGroup(self, group_id, group_name):
        with sqlite3.connect(self.database) as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM Groups where id = ?", (group_id,))
            row = cur.fetchone()
            if row is None:
                conn.execute("INSERT INTO Groups (id, name, time_min_spawn_waifu, time_max_spawn_waifu, time_min_run_waifu, time_max_run_waifu, spawn_time) VALUES (?, ?, ?, ?, ?, ?, ?);", (group_id, group_name, -1, -1, -1, -1, 60))
                conn.commit()
                print("[New Group #{}] - {}".format(group_id, group_name))
                return True
            return False

    @abc.abstractmethod
    def getCurrentWaifu(self, group_id):
        with sqlite3.connect(self.database) as conn:
            cur = conn.cursor()
            cur.execute("SELECT waifu_id FROM Current_Waifus where group_id = ?", (group_id,))
            row = cur.fetchone()
            if row is None:
                return []
            waifu_id = row[0]
            cur.execute("SELECT * FROM Anime_Waifu where id = ?", (waifu_id,))
            row = cur.fetchone()
            return row

    @abc.abstractmethod
    def getMarried(self, group_id, user_id, waifu_id, waifu_name):
        with sqlite3.connect(self.database) as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM Current_Waifus where group_id = ?", (group_id,))
            row = cur.fetchone()
            if row is None:
                return 1 
            
            conn.execute("DELETE FROM Current_Waifus WHERE group_id = ?", (group_id,))
            conn.commit()

            cur.execute("SELECT * FROM Harem where group_id = ? and waifu_id = ?", (group_id, waifu_id))
            row = cur.fetchone()
            if row is not None:
                conn.execute("UPDATE Groups SET spawn_time = ? WHERE id = ?", (30, group_id,))
                conn.commit()
                return 2

            conn.execute("INSERT INTO Harem (group_id, user_id, waifu_id) VALUES (?, ?, ?);", (group_id, user_id, waifu_id,))
            conn.commit()
            print("[Marriage #{}] - User {} - Waifu {} #{}".format(group_id, user_id, waifu_name, waifu_id))
            return 0

    @abc.abstractmethod
    def getCurrentHarem(self, group_id, user_id, page_size, page):
        waifus = []
        with sqlite3.connect(self.database) as conn:
            print("[Search Harem #{}] - User {}".format(group_id, user_id))
            cur = conn.cursor()
            cur.execute("SELECT waifu_id FROM Harem where group_id = ? and user_id = ?", (group_id, user_id,))
            rows = cur.fetchall()
            for row in rows:
                waifu_id = int(row[0])
                cur.execute("SELECT * FROM Anime_Waifu where id = ?", (waifu_id,))
                waifus.append(cur.fetchone())
            return waifus

    @abc.abstractmethod
    def removeGroupWaifus(self, inverval):
        list_groups = []
        with sqlite3.connect(self.database) as conn:
            cur = conn.cursor()
            cur.execute("SELECT group_id, time_waifu FROM Current_Waifus")
            rows = cur.fetchall()
            for row in rows:
                time = int(row[1])
                new_time = time - inverval
                if new_time < 0:
                    new_time = 0
                group_id = int(row[0])
                if new_time == 0:
                    conn.execute("DELETE FROM Current_Waifus WHERE group_id = ?", (group_id,))
                    conn.commit()
                    print("[Get Away #{}]".format(group_id))
                    list_groups.append(group_id)
                else:
                    conn.execute("UPDATE Current_Waifus SET time_waifu = ? WHERE group_id = ?", (new_time, group_id,))
            conn.commit()
            return list_groups

    @abc.abstractmethod
    def getRandomAnimeWaifu(self, group_id):
        #Necessário fazer verificação de waifus já noivadas
        with sqlite3.connect(self.database) as conn:
            waifu_id = randint(1, self.qnt_waifus)
            cur = conn.cursor()
            cur.execute("SELECT * FROM Current_Waifus where group_id = ?", (group_id,))
            row = cur.fetchone()
            if row is not None:
                return None  #Já existe uma waifu

            time_waifu = randint(self.time_min_run, self.time_max_run) #Tempo vivo da waifu (seg)
            conn.execute("INSERT INTO Current_Waifus (group_id, waifu_id, time_waifu) VALUES (?, ?, ?);", (group_id, waifu_id, time_waifu,))
            cur.execute("SELECT * FROM Anime_Waifu where id = ?", (waifu_id,))
            row = cur.fetchone()
            print("[SearchAnimeWaifu #{}] - {}".format(group_id, row[1]))
            conn.commit()
            return row
        
    @abc.abstractmethod
    def getReadyGroups(self, inverval):
        groups_id = []
        with sqlite3.connect(self.database) as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM Groups where spawn_time <= ?", (inverval,))
            rows = cur.fetchall()
            for row in rows:
                group_id = int(row[0])
                groups_id.append(group_id)
                #Fazer a verificação se existe uma waifu viva no momento!! << importante fazer depois
            self.reduceSpawnTime(inverval)
            print("[SpawnTime] - Inverval {}".format(inverval))
            return groups_id
    
    @abc.abstractmethod
    def reduceSpawnTime(self, interval):
        with sqlite3.connect(self.database) as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM Groups")
            rows = cur.fetchall()
            for row in rows:
                group_id = int(row[0])
                spawn_time = int(row[6])
                spawn_time -= interval
                if spawn_time <= 0:
                    spawn_time = randint(self.time_min_spawn, self.time_max_spawn)
                conn.execute("UPDATE Groups SET spawn_time = ? WHERE id = ?", (spawn_time, group_id,))
            conn.commit()

    @abc.abstractmethod
    def newInterval(self):
        with sqlite3.connect(self.database) as conn:
            cur = conn.cursor()
            cur.execute("SELECT min(spawn_time) FROM Groups")
            row = cur.fetchone()
            if row is None:
                print("[NewSpawnTime] - Nenhuma Waifu próxima ")
                return -1
            new_interval = int(row[0])
            print("[NewSpawnTime] - Interval {}".format(new_interval))
            return new_interval

    @abc.abstractmethod
    def getAnimeWaifusByName(self, name):
        with sqlite3.connect(self.database) as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM Anime_Waifu WHERE name LIKE ?", (name+'%',))
            rows = cur.fetchmany(6)
            if rows is None:
                print("[SearchWaifu] - {} # Found {}".format(name, 0))
                return []
            print("[SearchWaifu] - {} # Found {}".format(name, len(rows)))
            return rows

    @abc.abstractmethod
    def getAnimeWaifuByID(self, waifu_id):
        pass

    @abc.abstractmethod
    def getAnimeWaifuMarriedByID(self, group_id, waifu_id):
        pass

    @abc.abstractmethod
    def haveAnimeWaifuMarried(self, group_id, waifu_id):
        with sqlite3.connect(self.database) as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM Harem WHERE group_id = ? and waifu_id = ?", (group_id, waifu_id,))
            row = cur.fetchone()
            if row is None:
                return False
            return True

"""
CREATE TABLE Groups (
    id                   INTEGER PRIMARY KEY,
    name                 STRING,
    time_min_spawn_waifu INTEGER,
    time_max_spawn_waifu INTEGER,
    time_min_run_waifu   INTEGER,
    time_max_run_waifu   INTEGER,
    spawn_time           INTEGER
);

CREATE TABLE Manga_Waifu (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    name           STRING,
    nickname       STRING,
    gender         CHAR,
    img            STRING,
    manga          STRING,
    popularity     INTEGER,
    myanimelist_id INTEGER
);

CREATE TABLE Harem (
    group_id INTEGER,
    user_id  INTEGER,
    waifu_id INTEGER
);

CREATE TABLE Current_Waifus (
    group_id   INTEGER PRIMARY KEY,
    waifu_id   INTEGER,
    time_waifu INTEGER
);

CREATE TABLE Anime_Waifu (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    name           STRING,
    nickname       STRING,
    gender         CHAR,
    img            STRING,
    anime          STRING,
    popularity     INTEGER,
    myanimelist_id INTEGER
);

"""