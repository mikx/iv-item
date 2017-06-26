import sqlite3 as lite
import sys
import json

from collections import namedtuple
from itertools import chain

# pip install pyfunctional
from functional import seq

# Item
Item = namedtuple('Item', 'name categoryName itemLevel equipLevel jobs attributes bonus')


# Loader    
class Loader:

  jobs = {}
  baseParams = {}
  uiCategory = {}
  items = []
  
  allAttributes = ['Damage', 'MagicDamage', 'Defense', 'MagicDefense', 'ShieldRate', 'ShieldBlockRate', 'AttackInterval', 'AutoAttack']
  allAttributesHq = seq(allAttributes).map(lambda a: a + '_hq').to_list()

  def loadData(self):
    con = lite.connect('lib/app_data.sqlite')
    con.row_factory = lite.Row
    with con:    
      cur = con.cursor()    
      
      # Jobs
      q = """SELECT Key, Abbreviation_en FROM ClassJob"""
      cur.execute(q)
      rows = cur.fetchall()
      for row in rows:
        self.jobs[row["Key"]] = row["Abbreviation_en"]
        
      # Params
      q = """SELECT Key, Name_en FROM BaseParam"""
      cur.execute(q)
      rows = cur.fetchall()
      for row in rows:
          self.baseParams[row["Key"]] = row["Name_en"]
      
      # Category
      q = """SELECT Key, Name_en FROM ItemUICategory"""
      cur.execute(q)
      rows = cur.fetchall()
      for row in rows:
          self.uiCategory[row["Key"]] = row["Name_en"]

      # Items      
      q = """SELECT i.* FROM Item i INNER JOIN ItemUICategory c ON i.UICategory = c.Key WHERE c.Kind <= 4 AND i.Legacy = 0"""
      cur.execute(q)
      rows = cur.fetchall()
      multilist = seq(rows).map(self.makeItems)
      self.items = list(chain.from_iterable(multilist))
      
  def makeJobs(self, row):
    return seq(row["classjob"].split(",")).filter(None).map(int).filter(None).map(lambda x: self.jobs[x]).to_set()

  def makeAttributes(self, attributes, row):
    return dict([(a,row[a]) for a in attributes if row[a] != 0])
    
  def makeParams(self, bonus):
    return dict([(self.baseParams[int(k)],v) for kv in bonus for k,v in kv.items()])

      
  def makeItems(self, row):
    data = row["data"]
    blob = json.loads(data)
    item = Item(
      name            = row["UIName_en"],
      categoryName    = self.uiCategory[row["UICategory"]],
      equipLevel      = row["EquipLevel"],
      itemLevel       = row["Level"],
      jobs            = self.makeJobs(row),
      attributes      = self.makeAttributes(self.allAttributes, row),
      bonus           = self.makeParams(blob["bonus"]) if "bonus" in blob else {})
    result = []
    result.append(item)
    return [result]


