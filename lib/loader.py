import sqlite3 as lite
import sys
import json

from collections import namedtuple
from itertools import chain

# pip install pyfunctional
from functional import seq
#
# Item
#
Item = namedtuple('Item', 'name categoryName level equipLevel jobs attributes bonus')


#
# Loader
#
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
      multilist  = seq(rows).map(self.makeItems)
      self.items = seq(chain.from_iterable(multilist))
      
  def makeItems(self, row):
    data = row["data"]
    blob = json.loads(data)

    item = Item(
      name            = row["UIName_en"],
      categoryName    = self.uiCategory[row["UICategory"]],
      equipLevel      = row["EquipLevel"],
      level           = row["Level"],
      jobs            = self.makeJobs(row),
      attributes      = self.makeAttributes(self.allAttributes, row),
      bonus           = self.makeParams(blob["bonus"]) if "bonus" in blob else {})

    result = []
    result.append(item)
    
    if row['HQ'] == 1:
      name_hq = item.name + ' HQ'
      attributes_hq = self.makeAttributes(self.allAttributesHq, row)
      bonus_hq = self.makeParams(blob["bonus_hq"]) if "bonus_hq" in blob else {}
      item_hq = item._replace(name = name_hq, attributes = attributes_hq, bonus = bonus_hq)
      result.append(item_hq)
      
    return result

  def makeJobs(self, row):
    return seq(row["classjob"].split(",")).filter(None).map(int).filter(None).map(lambda x: self.jobs[x]).to_set()

  def makeAttributes(self, attributes, row):
    return dict([(a,row[a]) for a in attributes if row[a] != 0])
    
  def makeParams(self, bonus):
    return dict([(self.baseParams[int(k)],v) for kv in bonus for k,v in kv.items()])


#
# ItemFilter
#
class ItemFilter(object):

  def byCatrgoryName(names, item):
    return item if item.categoryName in names else None
    
  def byBonusName(names, item):
    return item if any(map(item.bonus.__contains__, names)) else None
    
  def byJobName(names, item):
    return item if any(map(item.jobs.__contains__, names)) else None
    
  def byLevel(min, max, item):
    return item if min <= item.equipLevel and item.equipLevel <= max else None

  
#
# ItemFormatter
# 
class ItemFormatter(object):

  def getEffectiveAttributes(items):
    result = set()
    for i in items:
      result = result.union(i.attributes.keys())
    return result

  def getEffectiveBonus(items):
    result = set()
    for i in items:
      result = result.union(i.bonus.keys())
    return result
    
  def toCsvString(arr):
    return '"' + '","'.join(map(str, arr)) + '"'
    
  def toCsvArray(items):
    base = ['Name', 'level', 'iLevel']
    attributes = sorted(ItemFormatter.getEffectiveAttributes(items))
    bonus = sorted(ItemFormatter.getEffectiveBonus(items))
    attr_bonus = { v:k for k,v in enumerate(attributes + bonus) }
    attr_bonus_len = len(attr_bonus)
    result = [ItemFormatter.toCsvString(base + attributes + bonus)]
    for item in items:
      line = [""] * attr_bonus_len
      for k,v in item.attributes.items():
        line[attr_bonus[k]] = v
      for k,v in item.bonus.items():
        line[attr_bonus[k]] = v
      result.append(ItemFormatter.toCsvString([item.name, item.equipLevel, item.level] + line))
    return result
  
  
  

  