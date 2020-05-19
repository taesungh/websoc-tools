import WebSOC_handler

import time


# TERM = '2020-14'
# COURSE_TITLE = DEPARTMENT + ' ' + COURSE_NUMBER

T_QUERY = 30

def systime(): return time.strftime('%X')


class CourseTracker:
    """iterative template to query a course and call subsequent actions"""
    def __init__(self, query: {str: str}, check: callable):
        self._flagged = False
        self._interval = T_QUERY
        self._query = query
        self._check = check
        self._course_title = f"{self._query['Dept']} {self._query['CourseNum']}"

        self._course_data = dict()
        self._get_course_data()
        self._last_course_data = self._course_data


    def _get_course_data(self) -> None:
        """retrieves the course data using the parameters in self._query"""
        # query_params = {'YearTerm': TERM, 'Dept': self._query['department'], 'CourseNum': self._query['course_number']}
        self._last_course_data = self._course_data
        self._course_data = WebSOC_handler.get_course_data(self._query)


    def _check_listings(self) -> bool:
        """returns True when any section satifies the self._check predicate"""
        return any(self._check(section) for section in self._course_data)


    def _interpret_listings(self) -> str:
        """turn course data into multi-line string of enrollment readings"""
        return '\n'.join(f"{section['type']} {section['sec']} - {section['enr']} enr of {section['max']} max" if self._check(sec) for sec in self._course_data) + '\n'


    def _print_course_data(self) -> print:
        """prints course data as a table with dividers"""
        def printTable(myDict, colList=None, sep='\n'):
            """ Pretty print a list of dictionaries (myDict) as a dynamically sized table.
            If column names (colList) aren't specified, they will show in random order.
            sep: row separator. Ex: sep='\n' on Linux. Default: dummy to not split line.
            Author: Thierry Husson - Use it as you want but don't blame me."""
            hl = '\u2500'; vl = '\u2502'; vhl = '\u253c'
            if not colList: colList = list(myDict[0].keys() if myDict else [])
            myList = [colList] # 1st row = header
            for item in myDict: myList.append([str(item[col] or '') for col in colList])
            colSize = [max(map(len,(sep.join(col)).split(sep))) for col in zip(*myList)]
            formatStr = f' {vl} '.join(["{{:<{}}}".format(i) for i in colSize])
            line = formatStr.replace(f' {vl} ', f'{hl}{vhl}{hl}').format(*[hl * i for i in colSize])
            item=myList.pop(0); lineDone=False
            while myList:
                if all(not i for i in item):
                    item=myList.pop(0)
                    if line and (sep!='\n' or not lineDone): print(line); lineDone=True
                row = [i.split(sep,1) for i in item]
                print(formatStr.format(*[i[0] for i in row]))
                item = [i[1] if len(i)>1 else '' for i in row]
        
        # print('\t'.join(self._course_data[0].keys()))
        # for listing in self._course_data:
        #     print('\t'.join(listing.values()))
        printTable(self._course_data)


    def _check_action(self) -> None:
        """called whenever course data is retrieved"""
        pass


    def _default_action(self) -> None:
        """called whenever course data is retrieved"""


    def run_periodic(self) -> None:
        """once called, periodically runs course tracking system"""
        self._flagged = False
        while True:
            try:
                self._get_course_data()
                if not self._course_data:
                    print('Course data is empty.')
                else:
                    self._check_action()
                    self._default_action()
            except(WebSOC_handler.WebSOCError):
                print('WebSOC could not be reached')
            time.sleep(self._interval)
# end CourseTracker
