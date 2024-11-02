#pip install OSMPythonTools
from OSMPythonTools.api import Api
api = Api()
way = api.query('way/5887599')

print(way.tag('building'))