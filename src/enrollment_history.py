import WebSOC_handler as soc
from SQLite_handler import SQLDatabase

from datetime import datetime
from datetime import timedelta
import time

def timestamp() -> datetime:
    now = datetime.now()
    return now - timedelta(microseconds=now.microsecond)

def log(message: str) -> print:
    """prints message with timestamp"""
    print(f"[{timestamp()}] {message}")

def sleep(dt: timedelta) -> 'sleep':
    """pauses execution for the given time"""
    if (type(dt) == timedelta):
        dt = dt.total_seconds()
    time.sleep(dt)

# opposite of epoch
CHOPE = datetime.max

T_DATA = timedelta(hours=1)
QUERY_INTERVAL = max(timedelta(seconds=2), T_DATA / len(soc.S_DEPARTMENTS) - timedelta(seconds=2))
T_PING = timedelta(seconds=60)
TERM = '2020-92'    # for Fall 2020 term, enrollment occuring in Spring 2020

# DATABASE = 'fall-2020.db'

l_headers_static = ['dept', 'num', 'title', 'code', 'type', 'sec', 'units', 'instructor', 'time', 'place', 'final']
l_headers_live = ['code', 'max', 'enr', 'wl', 'req', 'nor', 'rstr', 'status']

l_headers_default = ['dept', 'num', 'title', 'code', 'type', 'sec', 'units', 'instructor', 'time', 'place', 'final', 'max', 'enr', 'wl', 'req', 'nor', 'rstr', 'status']


class EnrollmentHistory:
    """module to query WebSOC and store historical results in SQL database"""
    def __init__(self, database: 'path', term: str):
        """docstring for %s"""
        self._db = SQLDatabase(database)
        self._term = term
        self._initialize_tables()


    def _initialize_tables(self) -> None:
        """docstring for _initialize_tables"""
        db = self._db
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

        pragma_cinfo = [(0, 'dept', 'text', 1, None, 0),
                        (1, 'num', 'text', 1, None, 0),
                        (2, 'title', 'text', 0, None, 0),
                        (3, 'code', 'int', 1, None, 0),
                        (4, 'type', 'text', 0, None, 0),
                        (5, 'sec', 'text', 0, None, 0),
                        (6, 'units', 'text', 0, None, 0),
                        (7, 'instructor', 'text', 0, None, 0),
                        (8, 'time', 'text', 0, None, 0),
                        (9, 'place', 'text', 0, None, 0),
                        (10, 'final', 'text', 0, None, 0),
                        (11, 'start_date', 'date', 1, None, 0),
                        (12, 'end_date', 'date', 1, None, 0)]
        if list(db('''PRAGMA table_info(CourseInfo)''')) != pragma_cinfo:
            raise ValueError('table CourseInfo is not in the correct format')
        pragma_einfo = [(0, 'code', 'int', 1, None, 0),
                        (1, 'max', 'int', 0, None, 0),
                        (2, 'enr', 'int', 0, None, 0),
                        (3, 'wl', 'int', 0, None, 0),
                        (4, 'req', 'int', 0, None, 0),
                        (5, 'nor', 'int', 0, None, 0),
                        (6, 'rstr', 'text', 0, None, 0),
                        (7, 'status', 'text', 0, None, 0),
                        (8, 'start_date', 'date', 1, None, 0),
                        (9, 'end_date', 'date', 1, None, 0)]
        if list(db('''PRAGMA table_info(EnrollmentInfo)''')) != pragma_einfo:
            raise ValueError('table EnrollmentInfo is not in the correct format')
    # end _initialize_tables


    def _get_course_data(self, department: str) -> [dict]:
        """retrieves course data and sanitizes it for database usage"""
        query_params = {'YearTerm': self._term, 'Dept': department}
        while True:
            try:
                course_data = soc.get_course_data(query_params)
                for course in course_data:
                    if 'wl' in course and course['wl'] == 'n/a':
                        course['wl'] = -1
                    # entries like "off(x)" indicate the department turned off the course waitlist;
                    elif 'wl' in course and 'off' in course['wl']:
                        course['wl'] = -int(course['wl'][4:-1])

                    # entries like "section / joint" show enrollment totals for cross-listed courses
                    if 'enr' in course and '/' in course['enr']:
                        course['enr'], _, course['max'] = course['enr'].split()
                    for header in ('code', 'max', 'enr', 'wl', 'req', 'nor'):
                        try:
                            if header in course:
                                course[header] = int(course[header])
                        except ValueError as e:
                            raise soc.WebSOCError(e)
                return course_data
            except soc.WebSOCError as e:
                print('Encountered an error when attempting to reach WebSOC')
                print(e)
                sleep(QUERY_INTERVAL)
            except Error as e:
                print('Other error encountered')
                print(e)
                sleep(QUERY_INTERVAL)


    def _update_static_entry(self, course: dict) -> bool:
        """updates static entries in database using given course data"""
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
        """updates live entries in database using given course data"""
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


    def clean_up_removed_entries(self, course_data: [dict], department: str):
        """purges courses that were removed from WebSOC listings"""
        now = timestamp()
        codes_data = {course['code'] for course in course_data}
        db = self._db
        codes_db = set(i[0] for i in db('''SELECT code FROM CourseInfo
                                            WHERE dept == ?
                                                AND start_date <= ?
                                                AND ? < end_date
                                            ''', department, now, now))
        for code in codes_db - codes_data:
            self._db(f'''UPDATE CourseInfo
                            SET end_date = ?
                            WHERE code == ?
                                AND start_date <= ?
                                AND ? < end_date
                            ''', now, code, now, now)
            self._db(f'''UPDATE EnrollmentInfo
                            SET end_date = ?
                            WHERE code == ?
                                AND start_date <= ?
                                AND ? < end_date
                            ''', now, code, now, now)
            log(f" >> Course {code} was removed from {department}")
        # n_removed = len(codes_ci - codes_data)
        # if n_removed > 0:
        #     log(f"{n_removed} courses were removed from {department}")



    def update_data(self, departments: set=soc.S_DEPARTMENTS) -> None:
        """updates database with current WebSOC entries of given departments"""
        n_updates = 0
        n_courses = 0

        for department in departments:
            course_data = self._get_course_data(department)
            n_update = 0
            for course in course_data:
                n_update += (self._update_static_entry(course)\
                            + self._update_live_entry(course) + 1) // 2
            log(f"Updated {n_update} of {len(course_data)} courses in {department}")
            self.clean_up_removed_entries(course_data, department)
            n_updates += n_update
            n_courses += len(course_data)
            sleep(QUERY_INTERVAL)
        
        log(f"{n_updates} of {n_courses} courses in total have been updated.")
    # end update_data


    def get_data(self, params: dict, columns: [str]=l_headers_default, time: datetime=timestamp()) -> [(int or str)]:
        """returns a database query specified by parameters"""
        if not all(param in l_headers_default for param in params.keys()):
            raise ValueError
        if not all(col in l_headers_default for col in columns):
            raise ValueError

        # sanitize input columns since two tables are inner joined on 'code'
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
        """closes the database"""
        self._db.close()
# end EnrollmentHistory


def main() -> None:
    """docstring for main"""
    eh = EnrollmentHistory(input('Database: '), TERM)
    last = timestamp() - T_DATA
    try:
        while True:
            if timestamp() >= last + T_DATA:
                last = timestamp()
                eh.update_data()
                eh._db._connection.commit()
            sleep(T_PING)
    except(KeyboardInterrupt):
        print('Stopping enrollment history runner')
    finally:
        print('Exiting database')
        eh.close()


if __name__ == '__main__':
    main()
