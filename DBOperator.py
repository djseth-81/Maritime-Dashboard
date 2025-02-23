from pgdb import connect # https://www.pygresql.org/contents/pgdb/index.html

class DBOperator():
    """
    A basic Class that will directly interface with a PostGIS database on
    behalf of the Maritime Dashboard

    pgdb is DB-API 2.0 Compliant, so, *theoretically*, this could interface
    with different geospatial DBs (https://peps.python.org/pep-0249/)
    - Enables things like threadsafety too???

    DBOperator will implicitly connect to a 'demo' database unless specified
    otherwise

    //TODO:
    - push one entry to DB
    - push multiple entries to DB
    - effectively "rollback" updates to db
    - export table(?)
        - To CSV/SQL
    - export database(?)
        - To CSV/SQL
    - import to DB(?)
        - From CSV/SQL?
    - remove fetching table attributes(?)
    - remove fetching tables in DB(?)
    - Parsing (Geo)JSON to enter as SQL commands
        - Package as JSON
        - Do we want additional structures?
    - PostGIS related stuff
        - Take advantage of geometric functions in PostGIS (See postGIS_notes.txt)
            - There's also the geography/projection stuff, definitely gonna use those
    """
    def __init__(self, table: str, host='localhost', port='5432', user='',
                 passwd='', schema='public', db='demo') -> None:
        self.table = table
        self.__host = host # Pretty sure this defines private var
        self.__port = port
        self.__user = user
        self.__passwd = passwd
        self.__db = connect(database = db)
        self.__cursor = self.__db.cursor()

    ### Mutators ###

    def add(self, entry: dict) -> None:
        """
        Add entry
        Expects a dict = {key: value} to enter as `attribute` and value
        """
        # TODO: TEST ME!
        # FIXME: Replace these OBVIOUSLY syntactically bad dictionary calls before someone sees!
        self.__cursor.execute(f"INSERT INTO {self.table} {entry.key} {entry.value}")

    def modify(self, entry: dict) -> None:
        """
        Add entry
        """
        # TODO: TEST ME!
        self.__cursor.execute(f"UPDATE {self.table} SET `attribute` {entry}")

    def delete(self, attr) -> None:
        """
        deletes entry that has matching attribute
        ONLY deletes from connected table, tables inheriting from connected are NOT processed
            - I'm highly tempted to have it wipe inherited entries as well, but that defeats the purpose of this class
        """
        # TODO: TEST ME!
        # TODO: Might need to check if attr value type is string, so it can be wrapped in single quotes
        self.__cursor.execute(f"DELETE FROM ONLY {self.table} WHERE `attribute` = {attr}")

    def clear(self) -> None:
        """
        Clears all entries from table
        """
        # TODO: TEST ME!
        self.__cursor.execute(f"DELETE FROM {self.table}")

    def custom_cmd(self, cmd: str, call: str) -> None:
        """
        This is here in case you wanna submit custom SQL commands that are not currently supported
        Specify if the command is to read (r) or write (w) from database, so command is committed properly
        """
        # NOTE: WILL IMPLICITLY COMMIT COMMAND
        self.__cursor.execute(cmd)
        self.__db.commit() if call == 'w' else self.__db.fetchall()

    # commit command
    def commit(self) -> None:
        # NOTE: Currently just want this to be manually executed rn, so changes are user-aware
        # TODO: TEST ME!
        self.__db.commit()

    # rollback command
    def rollback(self) -> None:
        # TODO: TEST ME!
        self.__db.rollback()

    def import_db(self) -> None:
        """
        Import db
        """
        # TODO
        pass

    def importCSV(self) -> None:
        """
        Imports data from CSV file. Assume that the headers match the attributes 1-1
        """
        # TODO
        pass

    def export_db(self) -> None:
        """
        Export db
        """
        # TODO
        pass

    def exportCSV(self) -> None:
        """
        Exports data from table to CSV file.
        """
        # TODO
        pass

    ### Accessors ###
    def get_attributes(self) -> None:
        """
        Fetching table attributes
        """
        print("getting table attributes of:", self.table)
        self.__cursor.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{self.table}'")
        return self.__cursor.fetchall()

    # Fetching tables in DB --> Dev option!
    def get_tables(self) -> None:
        """
        Fetching tables in DB
        """
        print("getting tables in db:")
        self.__cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        attr = self.__cursor.fetchall()
        for table in attr:
            print(table)

    def check_privileges(self, operation: str) -> None:
        """
        Lists the privileges assigned to user per a given operation
        """
        # Maybe have it pull all possible operations and store them as metadata for object?
        self.__cursor.execute(f"SELECT has_table_privilege('{self.table}', '{operation}')")
        return self.__cursor.fetchall()

    # pull data from DB
    def query(self, attr: str) -> None:
        """
        Querys all of an attr (possibly add constraints and user defined limits?)
        """
        # Might be good to conform this to geospatial functions
        # ... or maybe add additional methods to do so
        self.__cursor.execute(f"SELECT {attr} FROM {self.table}")
        # NOTE: I wonder if it would be better for asynchronous calls to use the 
        # fetchone() command, and just have FAST script call DBOperator.query()
        # n times
        return self.__cursor.fetchall()

    def get_table(self) -> list:
        """
        querys the whole table
        """
        self.__cursor.execute(f"SELECT * FROM {self.table}")
        return self.__cursor.fetchall()

    def get_count(self) -> int:
        """
        Returns count of entries in table
        """
        # Idea is for this to be faster and more efficeint than pulling the whole table and counting it
        self.__cursor.execute(f"SELECT Count(*) FROM {self.table}")
        return self.__cursor.fetchall()

if __name__ == "__main__":
    db = DBOperator(db=input("Enter db: "),table=input("Enter table:"))

    db.get_tables()
    print()

    db.get_attributes()
    print()

    print("Number of entries in table:")
    print(db.get_count())
    print()

    print("INSERT privileges on table:")
    print(db.check_privileges('insert'))
    print()

    print("SELECT privileges on table:")
    db.check_privileges('select')
    print()

