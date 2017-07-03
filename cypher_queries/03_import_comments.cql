USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM 'file:///output-comments-0031.csv' AS line
WITH line
// find the pub it refers to
MATCH (pl:PubListing) WHERE pl.source_pub_id = toInteger(line.source_pub_id)
// ensure the comment node is created
MERGE (bc:BiteComment { source_comment_id: toInteger(line.source_comment_id) })
SET
  bc += line,
  bc.source_pub_id = toInteger(line.source_pub_id),
  bc.source_comment_id = toInteger(line.source_comment_id),
  bc.created_timestamp = toInteger(line.created_timestamp)
// link the comment to the user
MERGE (u:BiteUser {username: bc.username })
MERGE (u)-[:USER_MADE_COMMENT]->(bc)
WITH bc
RETURN *
