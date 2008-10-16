import sys 

import re
print re.sub('QtGui\.QApplication\.translate\(\".*?\",\s(.*),\sNone,\sQtGui\.QApplication\.UnicodeUTF8\)', r'_(\1)',sys.stdin.read())
