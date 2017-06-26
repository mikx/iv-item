import sqlite3 as lite
import sys
import json


# Item
class Item:
  def __init__(self):
    self.name = '?'

# Loader    
class Loader:

  jobs = {}
  base_params = {}
  uiCategory = {}
  items = []
  
  attributes = []

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
          self.base_params[row["Key"]] = row["Name_en"]
      
      # Category
      q = """SELECT Key, Name_en FROM ItemUICategory"""
      cur.execute(q)
      rows = cur.fetchall()
      for row in rows:
          self.uiCategory[row["Key"]] = row["Name_en"]

      # Items      
      q = """SELECT * FROM Item"""
      cur.execute(q)
      rows = cur.fetchall()
      self.items = list(map(Loader.makeItem, rows))
  
  def makeItem(row):
    item = Item()
    
    item.name       = row["UIName_en"]
    item.level      = row["EquipLevel"]
    item.iLevel     = row["Level"]
    
    classjob = row["classjob"].split(",")
    
    return item


