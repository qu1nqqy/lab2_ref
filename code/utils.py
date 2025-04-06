from starlette.templating import Jinja2Templates

import re  # for regular expressions

templates = Jinja2Templates(directory='templates')

# Regex for username: 4–20 alphanumeric characters
pattern = re.compile(r'\w{4,20}')
# Regex for password: 6–20 alphanumeric characters
pattern_pw = re.compile(r'\w{6,20}')
# Regex for email
pattern_mail = re.compile(r'^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$')