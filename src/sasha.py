from course_tracker import CourseTracker
import WebSOC_handler as soc
import fb_notifier
import fbchat

import time

#SASHA = '100040755275062'


def systime(): return time.strftime('%X')


class Sasha(CourseTracker):
    def __init__(self, query: {str: str}, notifier: fb_notifier.FB_Notifier, check: callable):
        self._notifier = notifier
        super().__init__(query, check)
    
    
    def _send_message(self, message: str) -> str:
        return self._notifier(message)
    
    
    def _check_action(self) -> None:
        if not self._check_listings() and self._flagged:
            self._flagged = False
            #self._interval = INTERVAL
            message = f"{self._course_title} has closed."
            send = self._send_message(message)
            print(f'[{systime()}]', 'Course is no longer flagged.')
        if self._check_listings() and not self._flagged:
            self._flagged = True
            #self._interval = INTERVAL / 10
            message = f"{self._course_title} is open:" + '\n' + self._interpret_listings()
            send = self._send_message(message)
            print(f'[{systime()}]', 'Course has been flagged. Message sent.')
            self._print_course_data()
        elif self._last_course_data != self._course_data and self._flagged:
            message = f"Openings for {self._course_title} have changed:" + '\n' + self._interpret_listings()
            self._send_message(message)
            print(f'[{systime()}]', 'Openings updated. Message sent.')
            self._print_course_data()
    
    
    def _default_action(self) -> None:
        #self._send_message(f"course {COURSE_TITLE} has {self._course_data['enr']} out of {self._course_data['max']} enrolled")
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


def input_parameters() -> {str: str}:
    def input_str(message: str, is_legal=(lambda x: True), error_message='') -> str:
        while True:
            response = input(message + ': ')
            if is_legal(response):
                return response
            else:
                print(error_message)
    
    department = input_str('Department', (lambda s: s in soc.S_DEPARTMENTS), 'invalid department name')
    course_number = input_str('Course Number')
    course_code = input_str('Course Code')
    return {'Dept': department, 'CourseNum': course_number, 'CourseCodes': course_code}


if __name__ == '__main__':
    try:
        print('---------------WebSOC Course Tracker---------------')
        notifier = fb_notifier.connect()
        parameters = input_parameters()
        ct = Sasha(parameters, notifier, lambda sec: sec['status'] == 'OPEN')
        
        try:
            ct.run_periodic()
        except KeyboardInterrupt:
            print('All Done')
        finally:
            notifier.logout()
    except(fbchat.FBchatException):
        print('User could not be logged in.')