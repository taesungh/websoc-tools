import WebSOC_handler
from SQLite_handler import SQLDatabase


DATABASE = 'SOC.db'

class EnrollmentHistory:
    def __init__(self):
        """docstring for %s"""
        self._db = SQLDatabase(DATABASE)
    
    def _create_table(self, name: string) -> bool:
        """docstring for create_table"""
        self._db('''CREATE TABLE IF NOT EXISTS ? (
                        dept text
                        num text
                        code int
                        type text
                        sec text
                        units text
                        instructor text
                        time text
                        place text
                        final text
                        max int
                        enr int
                        wl int
                        req int
                        nor text
                        rstr text
                        textbooks text
                        web text
                        status text
                    )''', name)



WebSOC_handler.get_course_data(query_params)