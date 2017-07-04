// associate keywords together
MATCH (pk:PubKeyword { word: "rude" })<-[:PUB_HAS_KEYWORD]-(:PubListing)-[r:PUB_HAS_KEYWORD]->(pk2:PubKeyword)
WITH pk, COLLECT(DISTINCT pk2) AS pk2
UNWIND pk2 AS other_pk
MATCH p=(pk)<-[:PUB_HAS_KEYWORD]-(:PubListing)-[r:PUB_HAS_KEYWORD]->(other_pk)
WITH pk, COLLECT(p) AS p, other_pk
WITH pk, size(p) AS num_in_common, other_pk
ORDER BY num_in_common DESC
RETURN *

// simply expand an area of the graph
// call the param first
// :param kcl_coords:{ lon: -0.116253000712072, lat: 51.5116117881682 }
CALL spatial.withinDistance('pois', {kcl_coords}, 0.5) YIELD node as p
WITH p WHERE p:Pub
MATCH (p)-[:PUB_ON_MAP|PUB_HAS_FACILITY|COMMENT_ABOUT_PUB|PUB_HAS_KEYWORD|PUB_IS_NEARBY*1..2]-(n)
RETURN *
