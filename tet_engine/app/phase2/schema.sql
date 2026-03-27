CREATE TABLE IF NOT EXISTS exams (
  id SERIAL PRIMARY KEY,
  code VARCHAR(20) UNIQUE NOT NULL,
  name VARCHAR(255) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS source_documents (
  id SERIAL PRIMARY KEY,
  exam_code VARCHAR(20) NOT NULL,
  name VARCHAR(255) NOT NULL,
  source_type VARCHAR(50) NOT NULL,
  storage_path VARCHAR(500) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS source_chunks (
  id SERIAL PRIMARY KEY,
  document_id INTEGER NOT NULL REFERENCES source_documents(id) ON DELETE CASCADE,
  chunk_index INTEGER NOT NULL,
  topic_hint VARCHAR(255) DEFAULT '',
  content TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_source_chunks_document_id ON source_chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_source_documents_exam_code ON source_documents(exam_code);

CREATE TABLE IF NOT EXISTS generated_questions (
  id SERIAL PRIMARY KEY,
  exam_code VARCHAR(20) NOT NULL,
  paper_name VARCHAR(100) NOT NULL,
  subject_name VARCHAR(100) NOT NULL,
  topic_name VARCHAR(150) NOT NULL,
  question_text TEXT NOT NULL,
  options_json TEXT NOT NULL,
  correct_option VARCHAR(2) NOT NULL,
  explanation TEXT NOT NULL,
  difficulty VARCHAR(20) NOT NULL,
  source_chunk_ids TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_generated_questions_topic ON generated_questions(topic_name);
CREATE INDEX IF NOT EXISTS idx_generated_questions_difficulty ON generated_questions(difficulty);
