import re

def get(text):
    tags = ''

    # Build your own custom dynamic tags. For example:
    # if ('test TeSt TEST' in text):
    #     tags = tags + ' #Test'

    tags = re.sub('^\s*', '', tags)

    if tags != '':
        return tags
    else:
        return None
