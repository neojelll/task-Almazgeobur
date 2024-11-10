CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    hash_file VARCHAR UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    name VARCHAR,
    quantity INTEGER,
    price NUMERIC(10, 2),
    category VARCHAR
);

CREATE TABLE llm_responses (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    response TEXT NOT NULL
);
