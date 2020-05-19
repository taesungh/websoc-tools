import WebSOC_handler as soc
from SQLite_handler import SQLDatabase

from datetime import datetime
from datetime import timedelta
import time

def timestamp() -> datetime:
    now = datetime.now()
    return now - timedelta(microseconds=now.microsecond)

CHOPE = datetime.max
QUERY_INTERVAL = 20
T_DATA = timedelta(hours=1)
T_PING = 60
TERM = '2020-92'

#DATABASE = 'spring-2020.db'

l_headers_static = ['dept', 'num', 'title', 'code', 'type', 'sec', 'units', 'instructor', 'time', 'place', 'final']
l_headers_live = ['code', 'max', 'enr', 'wl', 'req', 'nor', 'rstr', 'status']

l_headers_default = ['dept', 'num', 'title', 'code', 'type', 'sec', 'units', 'instructor', 'time', 'place', 'final', 'max', 'enr', 'wl', 'req', 'nor', 'rstr', 'status']


class EnrollmentHistory:
    def __init__(self, database: 'path', term: str):
        """docstring for %s"""
        self._db = SQLDatabase(database)
        self._term = term
        self._initialize_tables()
    
    
    def _initialize_tables(self) -> None:
        """docstring for _initialize_tables"""
        self._db('''CREATE TABLE IF NOT EXISTS CourseInfo (
                        dept text NOT NULL,
                        num text NOT NULL,
                        title text,
                        code int NOT NULL,
                        type text,
                        sec text,
                        units text,
                        instructor text,
                        time text,
                        place text,
                        final text,
                        start_date date NOT NULL,
                        end_date date NOT NULL
                    )''')
                        #textbooks text,
                        #web text,
        self._db('''CREATE TABLE IF NOT EXISTS EnrollmentInfo (
                        code int NOT NULL,
                        max int,
                        enr int,
                        wl int,
                        req int,
                        nor int,
                        rstr text,
                        status text,
                        start_date date NOT NULL,
                        end_date date NOT NULL
                    )''')
    # end _initialize_tables
    
    
    def _get_course_data(self, department: str) -> [dict]:
        """docstring for _get_course_data"""
        query_params = {'YearTerm': self._term, 'Dept': department}
        while True:
            try:
                return soc.get_course_data(query_params)
            except soc.WebSOCError:
                time.sleep(QUERY_INTERVAL)
    
    
    def _update_static_entry(self, course: dict) -> bool:
        """docstring for _update_static_entry"""
        code = course['code']
        now = timestamp()
        try:
            entry_static = next(self._db('''SELECT * FROM CourseInfo
                                            WHERE code == ?
                                                AND start_date <= ?
                                                AND ? < end_date
                                            ''', code, now, now))[:-2]
                                            # trim start_date and end_date
        except StopIteration:
            entry_static = tuple()
        
        course_static = tuple(course.get(h, None) for h in l_headers_static)
        if entry_static != course_static:
            self._db(f'''UPDATE CourseInfo
                            SET end_date = ?
                            WHERE code == ?
                                AND start_date <= ?
                                AND ? < end_date
                            ''', now, code, now, now)
            self._db(f'''INSERT INTO CourseInfo (
                        {', '.join(l_headers_static + ['start_date', 'end_date'])})
                        VALUES ({', '.join('?' * (len(l_headers_static) + 2))}
                        )''', *course_static, now, CHOPE)
            return True
        return False
    # end _update_static_entry
    
    
    def _update_live_entry(self, course: dict) -> bool:
        """docstring for _update_live_entry"""
        code = course['code']
        now = timestamp()
        try:
            entry_live = next(self._db('''SELECT * FROM EnrollmentInfo
                                            WHERE code == ?
                                                AND start_date <= ?
                                                AND ? < end_date
                                            ''', code, now, now))[:-2]
                                            # trim start_date and end_date
        except StopIteration:
            entry_live = tuple()
        
        course_live = tuple(course.get(h, None) for h in l_headers_live)
        if entry_live != course_live:
            self._db(f'''UPDATE EnrollmentInfo
                            SET end_date = ?
                            WHERE code == ?
                                AND start_date <= ?
                                AND ? < end_date
                            ''', now, code, now, now)
            self._db(f'''INSERT INTO EnrollmentInfo (
                        {', '.join(l_headers_live + ['start_date', 'end_date'])})
                        VALUES ({', '.join('?' * (len(l_headers_live) + 2))}
                        )''', *course_live, now, CHOPE)
            return True
        return False
    # end _update_live_entry
    
    
    def update_data(self, departments: set=soc.S_DEPARTMENTS) -> None:
        """docstring for update_all_data"""
        for department in departments:
            course_data = self._get_course_data(department)
            n_update = 0
            for course in course_data:
                n_update += (self._update_static_entry(course)\
                            + self._update_live_entry(course) + 1) // 2
            print(f'[{timestamp()}] Updated {n_update} of {len(course_data)} courses in {department}')
            time.sleep(QUERY_INTERVAL)
        print(f'[{timestamp()}] All courses have been updated.')
    # end _record_all_data
    
    
    def get_data(self, params: dict, columns: [str]=l_headers_default, time: datetime=timestamp()):
        """docstring for get_data"""
        if not all(param in l_headers_default for param in params.keys()):
            raise ValueError
        if not all(col in l_headers_default for col in columns):
            raise ValueError
        
        qcolumns = list(columns)
        if 'code' in qcolumns:
            qcolumns[qcolumns.index('code')] = 'CourseInfo.code'
        qparams = dict(params)
        if 'code' in qparams:
            qparams['CourseInfo.code'] = qparams.pop('code')
        
        return self._db(f'''SELECT {', '.join(qcolumns)} FROM
                            CourseInfo INNER JOIN EnrollmentInfo
                            ON CourseInfo.code == EnrollmentInfo.code
                            WHERE {' AND '.join(f"{param} == ?" for param in qparams.keys()) + ' AND ' if len(qparams) > 0 else ''}
                            CourseInfo.start_date < ?
                            AND ? < CourseInfo.end_date
                            AND EnrollmentInfo.start_date < ?
                            AND ? < EnrollmentInfo.end_date''',
                            *(qparams.values()), *((time,) * 4))
    # end get_data
    
    def close(self) -> None:
        """docstring for close"""
        self._db.close()
    
# end EnrollmentHistory


def main():
    """docstring for main"""
    eh = EnrollmentHistory(input('Database: '), TERM)
    last = timestamp() - T_DATA
    try:
        while True:
            if timestamp() >= last + T_DATA:
                last = timestamp()
                eh.update_data()
                eh._db._connection.commit()
            time.sleep(T_PING)
    finally:
        eh.close()


if __name__ == '__main__':
    main()