from mysql.connector import Error as MysqlError


class Table:
    def __init__(self, cursor, id):
        self.cursor = cursor
        self.__table_name__ = ""
        self.id = None

class Museum(Table):
    def __init__(self,cursor=None, id=None, name=None, adress=None, **kwargs):
        super().__init__(cursor, id)
        self.__table_name__ = "Museum"
        self.adress = adress
        self.name = name
        self.cursor = cursor

    def insert(self):
        query = (
            "INSERT INTO Museum (museumName) "
            "VALUES (%s)"
        )
        values = (self.name,)
        self.cursor.execute(query, values)
        self.id = self.cursor.lastrowid
        self.results = self.cursor.fetchall()
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
                id = None
                self.museums.append(Museum(cursor, id, **data).insert())
                self.connection.commit()
                self.emitter.museumsChanged.emit(self.museums)
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
                self.museums.append(Museum(cursor, *result))
        self.emitter.museumsChanged.emit(self.museums)