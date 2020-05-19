import urllib.parse
import urllib.request
from pyquery import PyQuery as pq

WEBSOC_URL = 'https://www.reg.uci.edu/perl/WebSoc/listing'
TERM = '2020-14'

S_DEPARTMENTS = {'AC ENG', 'AFAM', 'ANATOMY', 'ANESTH', 'ANTHRO', 'ARABIC',
    'ARMN', 'ART', 'ART HIS', 'ARTS', 'ARTSHUM', 'ASIANAM', 'BANA', 'BATS',
    'BIO SCI', 'BIOCHEM', 'BME', 'BSEMD', 'CAMPREC', 'CBE', 'CBEMS', 'CEM',
    'CHC/LAT', 'CHEM', 'CHINESE', 'CLASSIC', 'CLT&THY', 'COGS', 'COM LIT',
    'COMPSCI', 'CRITISM', 'CRM/LAW', 'CSE', 'DANCE', 'DERM', 'DEV BIO',
    'DRAMA', 'E ASIAN', 'EARTHSS', 'EAS', 'ECO EVO', 'ECON', 'ECPS', 'ED AFF',
    'EDUC', 'EECS', 'EHS', 'ENGLISH', 'ENGR', 'ENGRCEE', 'ENGRMAE', 'ENGRMSE',
    'EPIDEM', 'ER MED', 'EURO ST', 'FAM MED', 'FIN', 'FLM&MDA', 'FRENCH',
    'GEN&SEX', 'GERMAN', 'GLBL ME', 'GLBLCLT', 'GREEK', 'HEBREW', 'HINDI',
    'HISTORY', 'HUMAN', 'HUMARTS', 'I&C SCI', 'IN4MATX', 'INNO', 'INT MED',
    'INTL ST', 'ITALIAN', 'JAPANSE', 'KOREAN', 'LATIN', 'LAW', 'LINGUIS',
    'LIT JRN', 'LPS', 'LSCI', 'M&MG', 'MATH', 'MED', 'MED ED', 'MED HUM',
    'MGMT', 'MGMT EP', 'MGMT FE', 'MGMT HC', 'MGMTMBA', 'MGMTPHD', 'MIC BIO',
    'MOL BIO', 'MPAC', 'MUSIC', 'NET SYS', 'NEURBIO', 'NEUROL', 'NUR SCI',
    'OB/GYN', 'OPHTHAL', 'PATH', 'PED GEN', 'PEDS', 'PERSIAN', 'PHARM',
    'PHILOS', 'PHRMSCI', 'PHY SCI', 'PHYSICS', 'PHYSIO', 'PLASTIC', 'PM&R',
    'POL SCI', 'PORTUG', 'PP&D', 'PSCI', 'PSY BEH', 'PSYCH', 'PUB POL',
    'PUBHLTH', 'RADIO', 'REL STD', 'ROTC', 'RUSSIAN', 'SOC SCI', 'SOCECOL',
    'SOCIOL', 'SPANISH', 'SPPS', 'STATS', 'SURGERY', 'SWE', 'TAGALOG', 'TOX',
    'UCDC', 'UNI AFF', 'UNI STU', 'UPPP', 'VIETMSE', 'VIS STD', 'WOMN ST',
    'WRITING'}

#https://webreg4.reg.uci.edu/cgi-bin/wramia?page=startUp&call=


SOC_NAMES = ['YearTerm', 'ShowComments', 'ShowFinals', 'Breadth', 'Dept', 'CourseNum', 'Division', 'CourseCodes', 'InstrName', 'CourseTitle', 'ClassType', 'Units', 'Days', 'StartTime', 'EndTime', 'MaxCap', 'FullCourses', 'CancelledCourses', 'Bldg', 'Room']

#RAW_HEADERS = ['code', 'type', 'sec', 'units', 'instructor', 'time', 'place',
#    'final', 'max', 'enr', 'wl', 'req', 'nor', 'rstr',
#    'textbooks', 'web', 'status']
#RAW_HEADERS = ['code', 'type', 'sec', 'units', 'instructor', 'time', 'place',
#    'final', 'max', 'enr', 'wl', 'req', 'rstr',
#    'textbooks', 'web', 'status']
#HEADERS = {item: RAW_HEADERS.index(item) for item in RAW_HEADERS}


class WebSOCError(Exception):
    pass


def _build_query_url(query_params: {str: str}) -> str:
    """docstring for _build_query_url"""
    default_params = {'YearTerm': TERM, 'ShowFinals': 1}
    # query_params can override default
    query_params = {**default_params, **query_params}
    return WEBSOC_URL + '?' + urllib.parse.urlencode(query_params)


def _pull_page(url: str) -> str:
    """docstring for _pull_page"""
    response = None
    try:
        response = urllib.request.urlopen(url)
        raw_page = response.read().decode(encoding = 'utf-8')
        #raw_lines = raw_text.split('\n')
        return raw_page
    finally:
        if response != None:
            response.close()


def _parse_course_data(raw_page: str) -> [{str: str}]:
    """docstring for _parse_course_data"""
    # try:
    #     d = pq(raw_page)('.course-list')
    #     q_listings = d("tr[valign*='top']:not([bgcolor='#fff0ff'])")
    #     #credits to Tristan Jogminas
    # except(ParserError):
    #     return dict()
    #
    # l_headers = d('th').contents()
    # d_headers = {item.lower(): l_headers.index(item) for item in l_headers}
    # course_data = []
    # for q_list in q_listings.items():
    #     data = {k: q_list('td').eq(v).text() for k, v in d_headers.items()}
    #     if 'time' in data:
    #         data['time'] = ' '.join(data['time'].split())
    #     course_data.append(data)
    # return course_data
    
    d = pq(raw_page)('.course-list')
    #adapted from Tristan Jogminas
    tr_listings = d("tr[valign*='top'], tr[align*=left]")
    
    l_headers = []
    dept = ''
    num = ''
    title = ''
    
    course_data = []
    for tr in tr_listings.items():
        tr_type = len(tr('td'))
        if tr_type == 1: # course title
            dept = tr('td').contents()[0].strip().split('\xa0')[0][:-1]
            num = tr('td').contents()[0].strip().split('\xa0')[1][1:]
            title = tr.text().split('\n')[1]
        elif tr_type == 0: # table headers
            l_headers = [header.lower() for header in tr('th').contents()]
            #d_headers = dict(enumerate(l_headers, 0))
        else: # course listing
            tr_data = {'dept': dept.upper(), 'num': num, 'title': title}
            tr_data.update((th, td.text()) for th, td in zip(l_headers, tr('td').items()))
            #tr_data.update({v: tr('td').eq(k).text() for k, v in d_headers.items()})
            if 'time' in tr_data:
                tr_data['time'] = ' '.join(tr_data['time'].split())
            course_data.append(tr_data)
    return course_data


def get_course_data(query_params: {str, str}) -> [{str: str}]:
    """docstring for get_course_data"""
    try:
        query_url = _build_query_url(query_params)
        raw_page = _pull_page(query_url)
        course_data = _parse_course_data(raw_page)
        return course_data
    except urllib.error.URLError as e:
        raise WebSOCError(e)
