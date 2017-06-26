from lib.loader import *
from functools import partial

loader = Loader()

loader.loadData()

#minerTools  = partial(ItemFilter.byCatrgoryName, ["Miner's Primary Tool", "Miner's Secondary Tool"])
#minerBonus  = partial(ItemFilter.byBonusName, ["Perception"])
#miners      = loader.items.filter(minerTools).filter(minerBonus)
#print (miners.to_list())

ninJobs  = partial(ItemFilter.byJobName, ["SAM", "NIN"])
ninHats  = partial(ItemFilter.byCatrgoryName, ["Head"])
ninLevel = partial(ItemFilter.byLevel, 10, 20)
ninjas   = loader.items.filter(ninJobs).filter(ninHats).filter(ninLevel).to_list()
print ("\n".join(ItemFormatter.toCsvArray(ninjas)))
