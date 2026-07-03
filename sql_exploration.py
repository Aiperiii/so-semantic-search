import psycopg2

conn = psycopg2.connect(dbname="stackoverflow", user="ajperiakzoltoeva")
cur = conn.cursor()

def run_query(title, query):
    print(f"\n{'='*60}")
    print(f"{title}")
    print('='*60)
    cur.execute(query)
    columns = [desc[0] for desc in cur.description]
    print(" | ".join(columns))
    print("-" * 60)
    for row in cur.fetchall():
        print(" | ".join(str(val) for val in row))

run_query("1. Score Distribution", """
    SELECT
        CASE
            WHEN score < 0 THEN 'negative'
            WHEN score = 0 THEN 'zero'
            WHEN score BETWEEN 1 AND 5 THEN '1-5'
            WHEN score BETWEEN 6 AND 20 THEN '6-20'
            WHEN score BETWEEN 21 AND 100 THEN '21-100'
            WHEN score > 100 THEN 'above 100'
        END AS score_range,
        COUNT(*) AS question_count,
        ROUND(COUNT(*) * 100.0 / 500000, 1) AS percentage
    FROM questions
    GROUP BY score_range
    ORDER BY MIN(score)
""")

run_query("2. Top 20 Tags", """
    SELECT tag, COUNT(*) AS question_count,
        ROUND(COUNT(*) * 100.0 / 500000, 2) AS percentage
    FROM question_tags
    GROUP BY tag
    ORDER BY question_count DESC
    LIMIT 20
""")

run_query("3. Question Volume by Year", """
    SELECT EXTRACT(YEAR FROM creation_date) AS year,
        COUNT(*) AS question_count
    FROM questions
    WHERE creation_date IS NOT NULL
    GROUP BY year
    ORDER BY year
""")

run_query("4. Answer Count Distribution", """
    SELECT answer_count,
        COUNT(*) AS number_of_questions,
        ROUND(COUNT(*) * 100.0 / 500000, 1) AS percentage
    FROM (
        SELECT q.id, COUNT(a.id) AS answer_count
        FROM questions q
        LEFT JOIN answers a ON a.question_id = q.id
        GROUP BY q.id
    ) AS question_answer_counts
    GROUP BY answer_count
    ORDER BY answer_count
    LIMIT 20
""")

run_query("5. Score vs Answer Count", """
    SELECT
        CASE
            WHEN q.score < 0 THEN 'negative'
            WHEN q.score = 0 THEN 'zero'
            WHEN q.score BETWEEN 1 AND 5 THEN '1-5'
            WHEN q.score BETWEEN 6 AND 20 THEN '6-20'
            WHEN q.score BETWEEN 21 AND 100 THEN '21-100'
            WHEN q.score > 100 THEN 'above 100'
        END AS score_range,
        COUNT(*) AS question_count,
        ROUND(AVG(answer_count), 2) AS avg_answers,
        ROUND(AVG(q.score), 1) AS avg_score
    FROM (
        SELECT q.id, q.score, COUNT(a.id) AS answer_count
        FROM questions q
        LEFT JOIN answers a ON a.question_id = q.id
        GROUP BY q.id, q.score
    ) AS q
    GROUP BY score_range
    ORDER BY MIN(q.score)
""")

run_query("6. Top Tag Co-occurrences", """
    SELECT t1.tag AS tag1, t2.tag AS tag2,
        COUNT(*) AS co_occurrences
    FROM question_tags t1
    JOIN question_tags t2
        ON t1.question_id = t2.question_id
        AND t1.tag < t2.tag
    GROUP BY t1.tag, t2.tag
    ORDER BY co_occurrences DESC
    LIMIT 20
""")

run_query("7. Unanswered Questions by Tag", """
    SELECT t.tag,
        COUNT(*) AS total_questions,
        SUM(CASE WHEN a.id IS NULL THEN 1 ELSE 0 END) AS unanswered,
        ROUND(SUM(CASE WHEN a.id IS NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS unanswered_pct
    FROM question_tags t
    JOIN questions q ON q.id = t.question_id
    LEFT JOIN answers a ON a.question_id = q.id
    WHERE t.tag IN (
        'c#','java','php','javascript','android',
        'jquery','c++','python','html','iphone',
        'asp.net','mysql','.net','ios','sql',
        'objective-c','css','ruby-on-rails','c','ruby'
    )
    GROUP BY t.tag
    HAVING COUNT(*) > 1000
    ORDER BY unanswered_pct DESC
""")

run_query("8. Average Score by Tag", """
    SELECT t.tag,
        COUNT(*) AS total_questions,
        ROUND(AVG(q.score), 2) AS avg_score,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY q.score) AS median_score,
        MAX(q.score) AS highest_score
    FROM question_tags t
    JOIN questions q ON q.id = t.question_id
    WHERE t.tag IN (
        'c#','java','php','javascript','android',
        'jquery','c++','python','html','iphone',
        'asp.net','mysql','.net','ios','sql',
        'objective-c','css','ruby-on-rails','c','ruby'
    )
    GROUP BY t.tag
    ORDER BY avg_score DESC
""")

run_query("9. Question Length vs Score", """
    SELECT
        CASE
            WHEN LENGTH(body) < 500 THEN 'short (under 500 chars)'
            WHEN LENGTH(body) BETWEEN 500 AND 1500 THEN 'medium (500-1500 chars)'
            WHEN LENGTH(body) BETWEEN 1501 AND 3000 THEN 'long (1500-3000 chars)'
            WHEN LENGTH(body) > 3000 THEN 'very long (over 3000 chars)'
        END AS length_bucket,
        COUNT(*) AS question_count,
        ROUND(AVG(score), 2) AS avg_score,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY score) AS median_score
    FROM questions
    WHERE body IS NOT NULL
    GROUP BY length_bucket
    ORDER BY MIN(LENGTH(body))
""")

cur.close()
conn.close()