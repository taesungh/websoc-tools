import sqlite3 as sqlite

class SQLDatabase:
    def __init__(self, database: 'path'):
        """docstring for %s"""
        self._database = database
        self._connection = sqlite.connect(database)
        self._cursor = self._connection.cursor()
    
    def __call__(self, *args) -> iter:
        """docstring for %s"""
        #self._cursor.execute(args)
        #return self._cursor.fetchall()
        return self._cursor.execute(args[0], args[1:])
    
    def close(self) -> None:
        """docstring for close"""
        self._connection.commit()
        self._connection.close()


def console():
    path = input('Database: ')
    db = SQLDatabase(path)
    running = True
    while running:
        command = input(f"{path}> ")
        if command == 'QUIT':
            running = False
        else:
            try:
                [print(item) for item in db(command)]
            except(sqlite.ProgrammingError) as e:
                print('An error occured, please try again.')
                print(e)
            except(sqlite.OperationalError) as e:
                print('The database could not handle the request.')
                print(e)
    db.close()
    print('Goodbye')


if __name__ == '__main__':
    console()
