import WebSOC_handler

import time


#TERM = '2020-14'
#COURSE_CODE = 35490
#DEPARTMENT = 'I&C SCI'
#COURSE_NUMBER = '6D'
#COURSE_TITLE = DEPARTMENT + ' ' + COURSE_NUMBER

S_DEPARTMENTS = {' ALL', 'AC ENG', 'AFAM', 'ANATOMY', 'ANESTH', 'ANTHRO',
'ARABIC', 'ARMN', 'ART', 'ART HIS', 'ARTS', 'ARTSHUM', 'ASIANAM', 'BANA',
'BATS', 'BIO SCI', 'BIOCHEM', 'BME', 'BSEMD', 'CAMPREC', 'CBE', 'CBEMS',
'CEM', 'CHC/LAT', 'CHEM', 'CHINESE', 'CLASSIC', 'CLT&THY', 'COGS', 'COM LIT',
'COMPSCI', 'CRITISM', 'CRM/LAW', 'CSE', 'DANCE', 'DERM', 'DEV BIO', 'DRAMA',
'E ASIAN', 'EARTHSS', 'EAS', 'ECO EVO', 'ECON', 'ECPS', 'ED AFF', 'EDUC',
'EECS', 'EHS', 'ENGLISH', 'ENGR', 'ENGRCEE', 'ENGRMAE', 'ENGRMSE', 'EPIDEM',
'ER MED', 'EURO ST', 'FAM MED', 'FIN', 'FLM&MDA', 'FRENCH', 'GEN&SEX',
'GERMAN', 'GLBL ME', 'GLBLCLT', 'GREEK', 'HEBREW', 'HINDI', 'HISTORY', 'HUMAN',
'HUMARTS', 'I&C SCI', 'IN4MATX', 'INNO', 'INT MED', 'INTL ST', 'ITALIAN',
'JAPANSE', 'KOREAN', 'LATIN', 'LAW', 'LINGUIS', 'LIT JRN', 'LPS', 'LSCI',
'M&MG', 'MATH', 'MED', 'MED ED', 'MED HUM', 'MGMT', 'MGMT EP', 'MGMT FE',
'MGMT HC', 'MGMTMBA', 'MGMTPHD', 'MIC BIO', 'MOL BIO', 'MPAC', 'MUSIC',
'NET SYS', 'NEURBIO', 'NEUROL', 'NUR SCI', 'OB/GYN', 'OPHTHAL', 'PATH',
'PED GEN', 'PEDS', 'PERSIAN', 'PHARM', 'PHILOS', 'PHRMSCI', 'PHY SCI',
'PHYSICS', 'PHYSIO', 'PLASTIC', 'PM&R', 'POL SCI', 'PORTUG', 'PP&D', 'PSCI',
'PSY BEH', 'PSYCH', 'PUB POL', 'PUBHLTH', 'RADIO', 'REL STD', 'ROTC', 'RUSSIAN',
'SOC SCI', 'SOCECOL', 'SOCIOL', 'SPANISH', 'SPPS', 'STATS', 'SURGERY', 'SWE',
'TAGALOG', 'TOX', 'UCDC', 'UNI AFF', 'UNI STU', 'UPPP', 'VIETMSE', 'VIS STD',
'WOMN ST', 'WRITING'}

INTERVAL = 30

def systime(): return time.strftime('%X')

SOC_NAMES = {'Term': 'YearTerm', 'Show Comments': 'ShowComments',
    'Show Finals': 'ShowFinals', 'Breadth': 'Breadth',
    'Department': 'Dept', 'Course Number': 'CourseNum',
    'Course Level': 'Division', 'Course Code': 'CourseCodes',
    'Instructor': 'InstrName', 'Title': 'CourseTitle',
    'Course Type': 'ClassType', 'Units': 'Units',
    'Days': 'Days', 'Starts After': 'StartTime', 'Ends Before': 'EndTime',
    'Capacity': 'MaxCap', 'Courses Full Option': 'FullCourses',
    'Cancelled Courses': 'CancelledCourses',
    'Building': 'Bldg', 'Room': 'Room',}


class CourseTracker:
    def __init__(self, query: {str: str}, check: callable):
        self._flagged = False
        self._interval = INTERVAL
        self._query = query
        self._check = check
        self._course_title = f"{self._query['Dept']} {self._query['CourseNum']}"
        
        self._course_data = dict()
        self._get_course_data()
        self._last_course_data = self._course_data
    
    
    def _get_course_data(self) -> None:
        #query_params = {'YearTerm': TERM, 'Dept': self._query['department'], 'CourseNum': self._query['course_number']}
        self._last_course_data = self._course_data
        self._course_data = WebSoc_handler.get_course_data(self._query)
    
    
    def _check_listings(self) -> bool:
        return any(self._check(section) for section in self._course_data)
    
    
    def _interpret_listings(self) -> [str]:
        reading = ''
        for section in self._course_data:
            if self._check(section):
                reading += f"{section['type']} {section['sec']} - {section['enr']} enr of {section['max']} max"
                reading += '\n'
        return reading
    
    
    def _send_message(self, message: str) -> str:
        return self._notifier(message)
    
    
    def _print_course_data(self) -> print:
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
        
        #print('\t'.join(self._course_data[0].keys()))
        #for listing in self._course_data:
        #    print('\t'.join(listing.values()))
        printTable(self._course_data)
    
    
    def _check_action(self) -> None:
        pass
    
    
    def _default_action(self) -> None:
        pass
    
    
    def run_periodic(self) -> None:
        self._flagged = False
        while True:
            try:
                self._get_course_data()
                if not self._course_data:
                    print('Course data is empty.')
                else:
                    self._check_action()
                    self._default_action()
            except(WebSoc_handler.WebSocError):
                print('WebSoc could not be reached')
            time.sleep(self._interval)
#end CourseTracker
