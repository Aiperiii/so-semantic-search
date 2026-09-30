CREATE TABLE questions_subset AS SELECT * FROM questions ORDER BY id LIMIT 50000;
CREATE TABLE inverted_index_subset AS SELECT ii.* FROM inverted_index ii WHERE ii.question_id IN (SELECT id FROM questions_subset);
CREATE TABLE doc_stats_subset AS SELECT * FROM doc_stats WHERE question_id IN (SELECT id FROM questions_subset);
CREATE TABLE token_stats_subset AS SELECT token, COUNT(DISTINCT question_id) AS df FROM inverted_index_subset GROUP BY token;
CREATE TABLE expansions_subset AS SELECT * FROM expansions WHERE token IN (SELECT DISTINCT token FROM inverted_index_subset);