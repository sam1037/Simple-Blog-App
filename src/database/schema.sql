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

CREATE TABLE IF NOT EXISTS user_likes (
  user_id INT NOT NULL, 
  post_id INT NOT NULL,
  PRIMARY KEY (user_id, post_id),
  CONSTRAINT fk_user
    FOREIGN KEY (user_id)
    REFERENCES users (user_id)
    ON DELETE CASCADE,
  CONSTRAINT fk_post
    FOREIGN KEY (post_id)
    REFERENCES posts (post_id)
    ON DELETE CASCADE
);

CREATE INDEX idx_posts_author ON posts (author);
CREATE INDEX idx_posts_date_posted ON posts (date_posted);
CREATE INDEX idx_user_likes_user_post ON user_likes (user_id, post_id);