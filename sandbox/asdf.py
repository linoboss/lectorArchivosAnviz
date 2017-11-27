from urllib.request import urlopen
import re

with urlopen('http://www.pythonchallenge.com/pc/def/equality.html') as f:
    html = f.read().decode('utf8')
    print(html)

    pattern = re.compile('''
        [^A-Z]    # any character except a capital letter
        [A-Z]{3}  # three capital letters
        (         # the beginning of a capturing group
        [a-z]     # one lowercase letter
        )         # the end of the group
        [A-Z]{3}  # three capital letters
        [^A-Z]    # any character except a capital letter
        ''', re.VERBOSE)
    print(str.join('', pattern.findall(html)))
