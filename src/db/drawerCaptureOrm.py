from mysql.connector import Error as MysqlError


class Table:
    def __init__(self, name, cursor):
        self.cursor = cursor
        self.name = name
        self.__table_name__ = ""
        self.id = None

class Museum(Table):
    def __init__(self,id=None,name=None,adress=None,cursor=None):
        super().__init__(name, cursor)
        self.__table_name__ = "Museum"
        self.adress = adress
        self.id = id
        self.name = name
        self.cursor = cursor

    def insert(self):
        query = (
            "INSERT INTO Museum (museumName) "
            "VALUES (%s)"
        )
        values = (self.name,)
        self.cursor.execute(query, values)
        self.connection.commit()
        self.id = self.cursor.lastrowid
        self.results = self.cursor.fetchall()
        self.cursor.close()
        return self
    
class Collection(Table):
    def __init__(self, name, cursor, museum_id):
        super().__init__(name, cursor)
        self.__table_name__ = "Collection"
        self.museum_id = museum_id
    
    def insert(self):
        query = (
            "INSERT INTO Collection (collectionName, museumID) " 
            "VALUES (%s, %s)"
        )
        values = (self.name, self.museum_id)
        cursor = self.connection.cursor()
        cursor.execute(query, values)
        self.connection.commit()
        self.id = cursor.lastrowid
        self.results = cursor.fetchall()
        cursor.close()
        return self

class Engine:
    def __init__(self, connection, emitter=None) -> None:
        self.connection = connection
        self.emitter = emitter
        self.getMuseums()
        self.collections = []
        emitter.museumAdded.connect(self.insertMuseum)

    def insertMuseum(self, data):
        try:
            with self.connection.cursor() as cursor:
                self.museums.append(Museum(id=None,*data, cursor=cursor).insert())
        except MysqlError as err:
            print("Error: ", err)

    def insertCollection(self, name, museum_id):
        self.collections.append(Collection(name, self.connection, museum_id).insert())

    def getMuseums(self):
        self.museums = []
        query = (
            "SELECT * FROM Museum"
        )
        with self.connection.cursor() as cursor:
            cursor.execute(query)
            for result in cursor:
                self.museums.append(Museum(*result, cursor=cursor))
        self.emitter.museumsChanged.emit(self.museums)