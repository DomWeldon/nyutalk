USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM 'file:///output-comments-0030.csv' AS line
WITH line LIMIT 10
// find the pub it refers to
MATCH (pl:PubListing) WHERE pl.source_pub_id = toInteger(line.source_pub_id)
// ensure the comment node is created
MERGE (bc:BiteComment { source_comment_id: line.source_comment_id })
SET bc += line
// link the comment to the user
MERGE (u:BiteUser {username: bc.username })
MERGE (u)-[:USER_MADE_COMMENT]->(bc)
// is this the first comment a user has made?
WITH bc, u, pl
OPTIONAL MATCH (u)-[r:PREVIOUS_COMMENT_BY_USER]->(last_comment:BiteComment)
WHERE last_comment <> bc
FOREACH (ignore IN CASE last_comment WHEN NULL THEN [1] ELSE [] END |
  // no, append it to the latest comment
  MERGE (u)-[:PREVIOUS_COMMENT_BY_USER]->(bc)
)
FOREACH (ignore IN CASE last_comment WHEN NULL THEN [] ELSE [1] END |
  // no, append it to the latest comment
  MERGE (last_comment)-[:PREVIOUS_COMMENT_BY_USER]->(bc)
)
// link the comment to the pub
MERGE (bc)-[:COMMENT_ABOUT_PUB]->(pl)
WITH bc, pl
// is this the first comment about the pub?
OPTIONAL MATCH (pl)-[r:PREVIOUS_COMMENT_ABOUT_PUB]->(last_comment:BiteComment)
WHERE last_comment <> bc
FOREACH (ignore IN CASE last_comment WHEN NULL THEN [1] ELSE [] END |
  // no, append it to the latest comment
  MERGE (pl)-[:PREVIOUS_COMMENT_ABOUT_PUB]->(bc)
)
FOREACH (ignore IN CASE last_comment WHEN NULL THEN [] ELSE [1] END |
  // no, append it to the latest comment
  MERGE (last_comment)-[:PREVIOUS_COMMENT_ABOUT_PUB]->(bc)
)
RETURN *
