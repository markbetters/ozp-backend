"""
Tokens File
"""

class Token(object):

    def __init__(self, short_name=None, long_name=None):
        self.short_name = short_name
        self.long_name = long_name

    def __str__(self):
        return '%s(%s)' % (self.token_type, self.long_name)

    def __repr__(self):
        return '%s(%s)' % (self.token_type, self.long_name)

    def __unicode__(self):
        return u'%s(%s)' % (self.token_type, self.long_name)


class InvalidFormatToken(Token):

    def __init__(self, **kwargs):
        super(InvalidFormatToken, self).__init__(**kwargs)
        self.token_type = 'InvalidFormatToken'

class UnknownToken(Token):

    def __init__(self, **kwargs):
        super(UnknownToken, self).__init__(**kwargs)
        self.token_type = 'UnknownToken'


class ClassificationToken(Token):

    def __init__(self, level=1, **kwargs):
        super(ClassificationToken, self).__init__(**kwargs)
        self.token_type = 'ClassificationToken'
        self.level = level


class DisseminationControlToken(Token):

    def __init__(self,  **kwargs):
        super(DisseminationControlToken, self).__init__(**kwargs)
        self.token_type = 'DisseminationControlToken'
