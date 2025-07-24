import logging
import sys


logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(levelname)s:%(name)s:%(line)s(%(id)s):%(message)s')
