CREATE TABLE IF NOT EXISTS users (
  user_id SERIAL PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
  password VARCHAR(64) NOT NULL --let's do the hash pw later
);

CREATE TABLE IF NOT EXISTS posts (
  post_id SERIAL PRIMARY KEY,
  author VARCHAR(50) NOT NULL, --let's care abt db normalization and join table later
  title VARCHAR(64) NOT NULL, 
  content TEXT,
  date_posted TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);