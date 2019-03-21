import sys
import os

sys.path.append(os.path.split(os.path.realpath(__file__))[0])


from request.request import Request, post, get  # noqa
