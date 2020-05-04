import urllib.parse
import urllib.request
from pyquery import PyQuery as pq

WEBSOC_URL = 'https://www.reg.uci.edu/perl/WebSoc/listing'
TERM = '2020-14'

#https://webreg4.reg.uci.edu/cgi-bin/wramia?page=startUp&call=

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
    default_params = {'YearTerm': TERM, 'ShowFinals': 1}
    # query_params can override default
    query_params = {**default_params, **query_params}
    return WEBSOC_URL + '?' + urllib.parse.urlencode(query_params)


def _pull_page(url: str) -> str:
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
    # raw_listings = []
#     for line in raw_page:
#         if 'valign="top"' in line and 'bgcolor="#fff0ff"' not in line:
#             raw_listings.append(line.strip())
#     if not raw_listings:
#         return dict()
#
#     parsed_data = []
#     for listing in raw_listings:
#         ls = pq(listing)
#         data = {k: ls('td').eq(v).text() for k, v in HEADERS.items()}
#         parsed_data.append(data)
#     return parsed_data
    try:
        d = pq(raw_page)('.course-list')
        q_listings = d("tr[valign*='top']:not([bgcolor='#fff0ff'])")
        #credits to Tristan Jogminas
    except(ParserError):
        return dict()
    
    l_headers = d('th').contents()
    d_headers = {item.lower(): l_headers.index(item) for item in l_headers}
    course_data = []
    for q_list in q_listings.items():
        data = {k: q_list('td').eq(v).text() for k, v in d_headers.items()}
        if 'time' in data:
            data['time'] = ' '.join(data['time'].split())
        course_data.append(data)
    return course_data


def get_course_data(query_params: {str, str}) -> [{str: str}]:
    try:
        query_url = _build_query_url(query_params)
        raw_page = _pull_page(query_url)
        course_data = _parse_course_data(raw_page)
        return course_data
    except(urllib.error.URLError):
        raise WebSocError
