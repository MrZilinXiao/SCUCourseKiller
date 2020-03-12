class CookieInvalidException(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class PasswordInvalidException(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class NoSuchCourseException(Exception):
    def __init__(self, *args):
        super().__init__(*args)
