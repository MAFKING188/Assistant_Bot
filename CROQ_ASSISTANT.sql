START TRANSACTION;

-- Create the database
CREATE DATABASE IF NOT EXISTS CROQ_ASSISTANT;
USE CROQ_ASSISTANT;

CREATE TABLE users (
  id INT NOT NULL AUTO_INCREMENT,
  username VARCHAR(255) NOT NULL,
  created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY (username)
);

CREATE TABLE sessions (
  id INT NOT NULL AUTO_INCREMENT,
  user_id INT DEFAULT NULL,
  start_time TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  end_time TIMESTAMP NULL DEFAULT NULL,
  PRIMARY KEY (id),
  KEY (user_id),
  CONSTRAINT sessions_ibfk_1 FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE interactions (
  id INT NOT NULL AUTO_INCREMENT,
  session_id INT DEFAULT NULL,
  user_input TEXT,
  ai_response TEXT,
  timestamp TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY (session_id),
  CONSTRAINT interactions_ibfk_1 FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE
);

CREATE TABLE chat_history (
  id INT NOT NULL AUTO_INCREMENT,
  session_id INT DEFAULT NULL,
  message TEXT,
  role ENUM('user', 'ai') DEFAULT NULL,
  timestamp TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY (session_id),
  CONSTRAINT chat_history_ibfk_1 FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE
);

CREATE INDEX idx_sessions_user_id ON sessions (user_id);
CREATE INDEX idx_interactions_session_id ON interactions (session_id);
CREATE INDEX idx_chat_history_session_id ON chat_history (session_id);

COMMIT;
