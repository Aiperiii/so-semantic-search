CREATE TABLE questions (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    body TEXT,
    score INTEGER,
    owner_user_id INTEGER,
    creation_date TIMESTAMP,
    closed_date TIMESTAMP
);

CREATE TABLE answers (
    id INTEGER PRIMARY KEY,
    question_id INTEGER REFERENCES questions(id),
    body TEXT,
    score INTEGER,
    owner_user_id INTEGER,
    creation_date TIMESTAMP
);

CREATE TABLE question_tags (
    question_id INTEGER REFERENCES questions(id),
    tag TEXT,
    PRIMARY KEY (question_id, tag)
);

