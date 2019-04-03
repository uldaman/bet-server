from configparser import ConfigParser

cfg = ConfigParser()
cfg.read('config.ini')


database = cfg.get('database', 'database')
user = cfg.get('database', 'user')
password = cfg.get('database', 'password')

endpoint = cfg.get('blockchain', 'endpoint')
contract = cfg.get('blockchain', 'contract')
abifile = cfg.get('blockchain', 'abifile')
