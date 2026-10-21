PRAGMA foreign_keys=off;
BEGIN TRANSACTION;
CREATE TABLE quizzes_new (
	id CHAR(32) NOT NULL, 
	document_id CHAR(32), 
	owner_id INTEGER NOT NULL, 
	difficulty VARCHAR(50) NOT NULL, 
	created_at DATETIME, 
    is_daily BOOLEAN DEFAULT 0, 
    quiz_date DATE, 
    quiz_number INTEGER, 
    status VARCHAR(50) DEFAULT 'Not Started', 
    topic VARCHAR(255), 
	PRIMARY KEY (id), 
	FOREIGN KEY(document_id) REFERENCES documents (id) ON DELETE CASCADE, 
	FOREIGN KEY(owner_id) REFERENCES users (id) ON DELETE CASCADE
);
INSERT INTO quizzes_new SELECT id, document_id, owner_id, difficulty, created_at, is_daily, quiz_date, quiz_number, status, topic FROM quizzes;
DROP TABLE quizzes;
ALTER TABLE quizzes_new RENAME TO quizzes;
CREATE INDEX ix_quizzes_document_id ON quizzes (document_id);
CREATE INDEX ix_quizzes_owner_id ON quizzes (owner_id);
CREATE INDEX ix_quizzes_id ON quizzes (id);
COMMIT;
PRAGMA foreign_keys=on;
