CREATE TABLE IF NOT EXISTS users (
  user_id SERIAL PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
  hashed_pw VARCHAR(60) NOT NULL
);

CREATE TABLE IF NOT EXISTS posts (
  post_id SERIAL PRIMARY KEY,
  author VARCHAR(50) NOT NULL, --let's care abt db normalization and join table later
  title VARCHAR(64) NOT NULL, 
  content TEXT,
  date_posted TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);