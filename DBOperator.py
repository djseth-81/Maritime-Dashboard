from pprint import pprint
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
"""
    # TODO:
    # - push multiple entries to DB
    # - effectively "rollback" updates to db
    # - export table(?)
    #     - To CSV/SQL
    # - export database(?)
    #     - To CSV/SQL
    # - import to DB(?)
    #     - From CSV/SQL?
    # - remove fetching table attributes(?)
    # - remove fetching tables in DB(?)
    # - Parsing (Geo)JSON to enter as SQL commands
    #     - Package as JSON

    # - PostGIS related stuff
    #     - Take advantage of geometric functions in PostGIS (See postGIS_notes.txt)
    #         - There's also the geography/projection stuff, definitely gonna use those
    #     - Retrieved data should already be primed for geospatial/projection
    #         - Look @ the projection/geography modules
    #         - refer to geospatial conversion/modify functions!

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

    def add(self, entity: dict) -> None:
        """
        Add entry
        Expects a dict = {key: value} to enter as `attribute` and value
        """
        # TODO: Handlel multiple entities for bulk additions
        # I might want to track relations, and organize entity values based off of it.
        # An entity might be added by a source, but then the entity will be immediately updated. It might be worth tracking what the values are so everything is up to date as fast as possible
        #       - Linked List? RoundRobin Queue? Hash table?
        # IDK how I want this to handle a bulk add, but I know it will include cursor.executemany()
        #   - Prolly have entity become entities = [dict]
        #   - Pretty sure this will replicate for modify() and delete() too
        
        # Wonder if this can be restricted to expect all values to be added to DB
        #   i.e. JSON is provided, with all values, and data that is unkown/un-needed is given default or NULL value
        #   - This doesn't solve my agnostic key/value-datatype problem though!
        pprint("attributes: ")
        pprint(",".join(entity.keys()))
        pprint()

        pprint("values: ")
        pprint(','.join(entity.values()))
        pprint()
        self.__cursor.execute(f"INSERT INTO {self.table} ({','.join(entity.keys())}) VALUES (%s)", (','.join(entity.values()),))

    def modify(self, entity: dict, data: dict) -> None:
        """
        Modifying exisitng entity
        """
        # Wonder if I can restrict what's expected to be provided for entity
        #   Not going to solve my problem even if restricted to higher components in Dashboard!
        pprint("Entity targetted:")
        pprint(entity)
        pprint("")

        pprint("Attributes to update:")
        pprint(data)
        pprint("")

        # TODO: I need to figure out how to make this ubiquitous to different datatypes
        old = [i for i in entity.values()]
        new = [i for i in data.values()]

        pprint(f"UPDATE {self.table} SET {''.join(data.keys())} = {new[0]} WHERE {''.join(entity.keys())} = {old[0]}")

        # self.__cursor.execute(f"UPDATE {self.table} SET {data.keys()} = {data.values()} WHERE {entity.keys()} = {entity.values()}")

    def delete(self, entity: dict) -> None:
        """
        deletes entry that has matching attribute
        ONLY deletes from connected table, tables inheriting from connected are NOT processed
            - I'm highly tempted to have it wipe inherited entries as well, but that defeats the purpose of this class
        """
        # TODO: Might need to check if attr value type is string, so it can be wrapped in single quotes
        pprint("ID to delete:")
        pprint(id)
        # self.__cursor.execute(f"DELETE FROM ONLY {self.table} WHERE `attribute` = {attr}")

    def clear(self) -> None:
        """
        Clears all entries from table
        """
        self.__cursor.execute(f"DELETE FROM {self.table}")

    def custom_cmd(self, cmd: str, call: str) -> None:
        """
        This is here in case you wanna submit custom SQL commands that are not currently supported
        Specify if the command is to read (r) or write (w) from database, so command is committed properly
        """
        # NOTE: WILL IMPLICITLY COMMIT COMMAND
        self.__cursor.execute(cmd)
        if call == 'w':
            pprint(self.__db.commit())
        else:
            pprint(self.__cursor.fetchall())

    # commit command
    def commit(self) -> None:
        # NOTE: Currently just want this to be manually executed rn, so changes are user-aware
        self.__db.commit()
        pprint("### DBOperator: Commands submitted.")

    # rollback command
    def rollback(self) -> None:
        self.__db.rollback()
        pprint("### DBOperator: Command queue cleared.")

    def close(self) -> None:
        """
        Closes table connection
        """
        self.__cursor.close()
        self.__db.close()
        pprint("### DBOperator: Connection closed.")


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
        Fetches table attributes
        """
        self.__cursor.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{self.table}'")
        return self.__cursor.fetchall()

    # Fetching tables in DB --> Dev option!
    def get_tables(self) -> None:
        """
        Fetching tables in DB
        """
        pprint("getting tables in db:")
        self.__cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        attr = self.__cursor.fetchall()
        for table in attr:
            pprint(table)

    def check_privileges(self) -> list:
        """
        Lists the privileges assigned to user per a given operation
        """
        operations = ['SELECT', 'INSERT', 'UPDATE', 'DELETE']

        for op in operations:
            self.__cursor.execute(f"SELECT has_table_privilege('{self.table}', '{op}')") 
        return self.__cursor.fetchall()

    # pull data from DB
    def query(self, attr: str) -> list:
        """
        Querys all of an attr (possibly add constraints and user defined limits?)
        """
        # Might be good to conform this to geospatial functions
        # ... or maybe add additional methods to do so
        self.__cursor.execute(f"SELECT {attr} FROM {self.table}")
        # NOTE: I wonder if it would be better for asynchronous calls to use the 
        # fetchone() command, and just have FAST script call DBOperator.query()
        # n times
        return self.__cursor.fetchone()

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
        # FIXME: DOES NOT return int, returns list
        # Idea is for this to be faster and more efficeint than pulling the whole table and counting it
        self.__cursor.execute(f"SELECT Count(*) FROM {self.table}")
        return self.__cursor.fetchall()

    # These are ideally supposed to take advantage of the PostGIS stuff
    def get_within(self, geom):
        """
        Gets data within region
        """
        pass

    def get_surrounding(self, geom):
        """
        Gets data within region
        """
        pass

if __name__ == "__main__":
    # db = DBOperator(db=input("Enter db: "),table=input("Enter table: "))
    db = DBOperator(db='nyc', table='fruits')

    # pprint()
    # db.get_tables()
    # pprint()

    pprint("Table Attributes:")
    pprint(db.get_attributes())
    print()

    # pprint("Number of entries in table:")
    # pprint(db.get_count())
    # pprint("Type: ", type(db.get_count()))
    # pprint()

    # pprint("SELECT privileges on table:")
    # pprint(db.check_privileges())
    # pprint("Type: ", type(db.check_privileges()))
    # pprint()

    # pprint("Entry from table:")
    # pprint(db.query("name"))
    # pprint("Type of fetchone()", type(db.query("name")))
    # pprint()

    # pprint("Adding value to table...")
    # db.add({'name':'papaya'})
    # db.commit()
    # pprint("New value:")
    # ppprint(db.get_table()) # Table should have new entity

    # TODO
    pprint("Modifying existing value...")
    db.modify({'id':9},{'id':8})
    db.commit()
    pprint("Modified value:")
    pprint(db.query("name")) # Entity should now be modified

    # TODO
    # db.delete()
    # db.commit()
    # pprint("New table:")
    # pprint(db.get_table()) # Entity should now be gone

    # TODO
    # pprint("Rolling back clear table...")
    # db.clear()
    # db.rollback()
    # pprint(db.get_table()) # should still have full table

    # TODO
    # pprint("Clearing table...")
    # db.clear()
    # db.commit()
    # pprint(db.get_table()) # table should have no entries

    db.close()
