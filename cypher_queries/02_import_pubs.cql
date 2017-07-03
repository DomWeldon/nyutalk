// USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM 'file:///output-pubs-0022.csv' AS line
WITH line
WITH
	line,
    split(line.facilities, ';') AS facilities
MERGE (pl:PubListing { soruce_pub_id: toInteger(line.source_pub_id) })
SET
  pl += line,
  pl.source_pub_id = toInteger(line.source_pub_id),
  pl.latitude = toFloat(line.latitude),
  pl.longitude = toFloat(line.longitude)
WITH pl, facilities
UNWIND facilities AS f
MERGE (pf:PubFacility { name: f })
MERGE (pf)<-[:PUB_HAS_FACILITY]-(pl)
WITH DISTINCT pl, split(pl.nearby_tube_stations, ';') AS tubes
UNWIND tubes as t
MERGE (rs:RailwayStation { name: t })
MERGE (rs)<-[:PUB_IS_NEARBY]-(pl)
WITH DISTINCT pl, [ x in split(pl.keywords, ';') | { word: split(x, ':')[0], frequency: split(x, ':')[1] } ] AS keywords
UNWIND keywords as k
MERGE (pk:PubKeyword { word: k.word })
MERGE (pk)<-[:PUB_HAS_KEYWORD { frequency: k.frequency }]-(pl)
RETURN True
