from settings import *

DEBUG = TEMPLATE_DEBUG = False

ALLOWED_HOSTS = ['.skedg.tk']

STATIC_ROOT = os.path.join(BASE_DIR, 'static')

ADMINS = (
	('Minseung Choi', 'mschoi@princeton.edu'),
	('Roy Zhao', 'rhzhao@princeton.edu'),
	('Crystal Qian', 'cqian@princeton.edu'),
	('Jonathan Lin', 'jl25@princeton.edu'),
)