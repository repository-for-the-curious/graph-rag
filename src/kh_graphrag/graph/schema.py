"""Neo4j schema: one database holds the graph and the vector index.

(:Repository)-[:CONTAINS]->(:Note)-[:HAS_CHUNK]->(:Chunk {embedding})
(:Repository|:Note)-[:TAGGED]->(:Tag {code, name, family})
(:Note)-[:LINKS_TO]->(:Note)
"""

VECTOR_INDEX = "chunk_embedding"


def schema_statements(dim: int) -> list[str]:
    return [
        "CREATE CONSTRAINT repo_name IF NOT EXISTS FOR (r:Repository) REQUIRE r.name IS UNIQUE",
        "CREATE CONSTRAINT note_path IF NOT EXISTS FOR (n:Note) REQUIRE n.path IS UNIQUE",
        "CREATE CONSTRAINT chunk_id IF NOT EXISTS FOR (c:Chunk) REQUIRE c.id IS UNIQUE",
        "CREATE CONSTRAINT tag_code IF NOT EXISTS FOR (t:Tag) REQUIRE t.code IS UNIQUE",
        (
            f"CREATE VECTOR INDEX {VECTOR_INDEX} IF NOT EXISTS "
            "FOR (c:Chunk) ON c.embedding "
            "OPTIONS {indexConfig: {"
            f"`vector.dimensions`: {int(dim)}, `vector.similarity_function`: 'cosine'"
            "}}"
        ),
    ]


UPSERT_TAGS = """
UNWIND $rows AS row
MERGE (t:Tag {code: row.code})
SET t.name = row.name, t.family = row.family
"""

UPSERT_REPOS = """
UNWIND $rows AS row
MERGE (r:Repository {name: row.name})
SET r.created_at = row.created_at, r.visibility = row.visibility,
    r.has_content = row.has_content, r.source = row.source
WITH r, row
UNWIND row.tags AS code
MERGE (t:Tag {code: code})
MERGE (r)-[:TAGGED]->(t)
"""

UPSERT_NOTES = """
UNWIND $rows AS row
MERGE (n:Note {path: row.path})
SET n.title = row.title, n.lang = row.lang
WITH n, row
MERGE (r:Repository {name: row.repo})
MERGE (r)-[:CONTAINS]->(n)
WITH n, row
UNWIND row.tags AS code
MERGE (t:Tag {code: code})
MERGE (n)-[:TAGGED]->(t)
"""

UPSERT_LINKS = """
UNWIND $rows AS row
MATCH (a:Note {path: row.src}), (b:Note {path: row.dst})
MERGE (a)-[:LINKS_TO]->(b)
"""

UPSERT_CHUNKS = """
UNWIND $rows AS row
MATCH (n:Note {path: row.note_path})
MERGE (c:Chunk {id: row.id})
SET c.text = row.text, c.heading = row.heading, c.ord = row.ord, c.embedding = row.embedding
MERGE (n)-[:HAS_CHUNK]->(c)
"""

VECTOR_SEARCH = f"""
CALL db.index.vector.queryNodes('{VECTOR_INDEX}', $k, $embedding) YIELD node, score
MATCH (n:Note)-[:HAS_CHUNK]->(node)
RETURN node.id AS chunk_id, node.text AS text, node.heading AS heading,
       n.path AS source, score
ORDER BY score DESC
"""

# Neighbours of the seed notes: explicit links (either direction) and notes of
# *other* repositories that share at least one TopicTag or LibraryTag.
# Chunks are re-ranked against the question embedding.
EXPAND = """
MATCH (sn:Note)-[:HAS_CHUNK]->(seed:Chunk) WHERE seed.id IN $ids
WITH collect(DISTINCT sn) AS seeds
UNWIND seeds AS sn
CALL (sn, seeds) {
  MATCH (sn)-[:LINKS_TO]-(nb:Note) WHERE NOT nb IN seeds
  RETURN nb, 'link:' + sn.path AS via
  UNION
  MATCH (sn)<-[:CONTAINS]-(r:Repository)-[:TAGGED]->(t:Tag)<-[:TAGGED]-(r2:Repository)-[:CONTAINS]->(nb:Note)
  WHERE r2 <> r AND t.family IN ['TopicTags', 'LibraryTags'] AND NOT nb IN seeds
  RETURN nb, 'tag:' + t.code AS via
}
WITH nb, collect(DISTINCT via) AS vias
MATCH (nb)-[:HAS_CHUNK]->(c:Chunk)
WITH c, nb, vias, vector.similarity.cosine(c.embedding, $embedding) AS score
RETURN c.id AS chunk_id, c.text AS text, c.heading AS heading, nb.path AS source,
       score, vias
ORDER BY score DESC
LIMIT $k
"""

ALL_TAGS = "MATCH (t:Tag) RETURN t.code AS code, t.name AS name, t.family AS family"

ALL_REPO_NAMES = "MATCH (r:Repository) RETURN r.name AS name"

REPOS_OF_NOTES = """
MATCH (r:Repository)-[:CONTAINS]->(n:Note) WHERE n.path IN $paths
RETURN DISTINCT r.name AS name
"""

REPOS_WITH_TAGS = """
MATCH (r:Repository)-[:TAGGED]->(t:Tag) WHERE t.code IN $codes
RETURN t.code AS code, t.name AS name, t.family AS family,
       collect(DISTINCT r.name) AS repos
ORDER BY code
"""

REPO_CARDS = """
MATCH (r:Repository) WHERE r.name IN $names
OPTIONAL MATCH (r)-[:TAGGED]->(t:Tag)
WITH r, t ORDER BY t.code
RETURN r.name AS name, r.visibility AS visibility, r.created_at AS created_at,
       r.has_content AS has_content, r.source AS source,
       collect(CASE WHEN t IS NULL THEN NULL ELSE t.code + ' ' + coalesce(t.name, '?') END) AS tags
"""
