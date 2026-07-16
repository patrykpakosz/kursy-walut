import json,urllib.request,xml.etree.ElementTree as ET,time
from datetime import date
B='https://www.thesportsdb.com/api/v1/json/3/'
def get(p):
 for i in range(4):
  try:
   r=urllib.request.urlopen(urllib.request.Request(B+p,headers={'User-Agent':'Mozilla/5.0'}),timeout=35);return json.load(r)
  except: time.sleep(12+i*10)
 return {}
def team(id,name,api_name):
 a=get(f'lookupteam.php?id={id}').get('teams',[{}])[0];time.sleep(3);ev=get(f'eventslast.php?id={id}').get('results',[]);time.sleep(3);nx=get(f'eventsnext.php?id={id}').get('events',[]);l=ev[0] if ev else {};z=nx[0] if nx else {}
 def txt(e):return f"{e.get('strHomeTeam','?')} {e.get('intHomeScore','-')} : {e.get('intAwayScore','-')} {e.get('strAwayTeam','?')}"
 f=[]
 for e in ev[:5]:
  h,aa=e.get('intHomeScore'),e.get('intAwayScore');mine,other=(h,aa) if e.get('strHomeTeam')==api_name else (aa,h)
  f.append('N' if mine is None else 'W' if int(mine)>int(other) else 'R' if int(mine)==int(other) else 'P')
 while len(f)<5:f.append('N')
 return {'name':name,'badge':a.get('strBadge'),'last':{'text':txt(l) if l else 'Brak danych','date':l.get('dateEvent','')},'next':{'text':f"{z.get('strHomeTeam','?')} — {z.get('strAwayTeam','?')}" if z else 'Brak zaplanowanego meczu','date':(z.get('dateEvent','')+' • '+(z.get('strTime')or'')[:5]).strip(' •')},'form':f}
def table(id,title,focus):
 m=get(f'lookupleague.php?id={id}').get('leagues',[{}])[0];time.sleep(3);a=get(f"lookuptable.php?l={id}&s={m.get('strCurrentSeason')}").get('table',[])
 return {'title':title,'badge':m.get('strBadge'),'focus':focus,'rows':[{'rank':x.get('intRank'),'team':x.get('strTeam'),'played':x.get('intPlayed'),'goals':f"{x.get('intGoalsFor',0)}:{x.get('intGoalsAgainst',0)}",'points':x.get('intPoints')} for x in a]}
def feed():
 for u in ['https://www.espn.com/espn/rss/soccer/news','https://feeds.bbci.co.uk/sport/football/rss.xml']:
  try:
   root=ET.fromstring(urllib.request.urlopen(u,timeout=30).read());return [x.findtext('title','') for x in root.findall('./channel/item')[:4]]
  except:pass
 return ['Brak bieżących nagłówków']
d={'teams':[team('135303','WISŁA KRAKÓW','Wisła Kraków'),team('133612','MANCHESTER UNITED','Manchester United'),team('133901','POLSKA','Poland')],'tables':{'ekstra':table('4422','TABELA EKSTRAKLASY','Wisła Kraków'),'premier':table('4328','TABELA PREMIER LEAGUE','Manchester United')},'fifa':{'rows':[{'rank':1,'team':'Argentyna'},{'rank':2,'team':'Hiszpania'},{'rank':3,'team':'Francja'},{'rank':4,'team':'Anglia'},{'rank':5,'team':'Brazylia'},{'rank':36,'team':'Polska'}]},'matches':[],'news':feed()}
open('pilka/football-data.json','w',encoding='utf8').write(json.dumps(d,ensure_ascii=False))