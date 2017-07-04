// 1. create a layer for pub listings
CALL spatial.addPointLayer('pub_listings')

// 2. add the pub listings to this layer
MATCH (pl:PubListing)
WITH COLLECT(pl) AS plc
CALL spatial.addNodes('pub_listings', plc)

// 1. Merge based on similarly named nodes in very close proxmimity
MATCH (pl:PubListing)
WHERE
	not((pl)-[:PUB_ON_MAP]->())
  AND exists(pl.latitude)
  AND exists(pl.longitude)
  AND pl.latitude IS NOT NULL
  AND pl.longitude IS NOT NULL
// look for nodes very nearby, which are very likely to be the place we're talking about
// within 10m
CALL spatial.withinDistance('pois', { lat: pl.latitude, lon: pl.longitude }, 0.1) YIELD node AS pn
WITH pl, pn
WHERE
	(pn:Pub OR pn:Restaurant)
	// names the same?
	AND (
 	 toLower(pn.name) = toLower(pl.name)
  	// what about removing "the"?
  	OR trim(replace(toLower(pn.name), 'the', '')) = trim(replace(toLower(pl.name), 'the', ''))
  	// first word matches?
  	OR split(trim(replace(toLower(pl.name), 'the', '')), ' ')[0] in split(toLower(pn.name), ' ')
	)
MERGE (pl)-[:PUB_ON_MAP]->(pn)


MATCH (pl:PubListing)
WHERE
	not((pl)-[:PUB_ON_MAP]->())
  AND exists(pl.latitude)
  AND exists(pl.longitude)
  AND pl.latitude IS NOT NULL
  AND pl.longitude IS NOT NULL
// WITH pl LIMIT 20
CALL spatial.withinDistance('pois', { lat: pl.latitude, lon: pl.longitude }, 0.05) YIELD node AS pn
WITH pl, pn WHERE pn:Pub
RETURN COUNT(pl)
