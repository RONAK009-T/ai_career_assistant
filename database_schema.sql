

CREATE DATABASE IF NOT EXISTS `ai_career_assistant_db`
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE `ai_career_assistant_db`;

-- 1. Users Table
CREATE TABLE IF NOT EXISTS `users` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(60) UNIQUE NOT NULL,
    `email` VARCHAR(120) UNIQUE NOT NULL,
    `password_hash` VARCHAR(255) NOT NULL,
    `full_name` VARCHAR(120) NOT NULL,
    `target_role` VARCHAR(120) DEFAULT 'Software Engineer',
    `bio` TEXT,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. Resumes Table
CREATE TABLE IF NOT EXISTS `resumes` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,-
    `filename` VARCHAR(255) NOT NULL,
    `file_type` VARCHAR(20) NOT NULL,
    `raw_text` MEDIUMTEXT NOT NULL,
    `uploaded_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_resumes_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Resume Analyses Table
CREATE TABLE IF NOT EXISTS `resume_analyses` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `resume_id` INT NOT NULL,
    `overall_score` INT DEFAULT 0,
    `summary` TEXT,
    `technical_skills` JSON,
    `soft_skills` JSON,
    `education` JSON,
    `experience` JSON,
    `projects` JSON,
    `certifications` JSON,
    `missing_sections` JSON,
    `strengths` JSON,
    `weaknesses` JSON,
    `suggestions` JSON,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_analyses_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_analyses_resume` FOREIGN KEY (`resume_id`) REFERENCES `resumes` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. Job Descriptions Table
CREATE TABLE IF NOT EXISTS `job_descriptions` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `title` VARCHAR(200) NOT NULL,
    `company` VARCHAR(120) DEFAULT '',
    `raw_text` MEDIUMTEXT NOT NULL,
    `parsed_json` JSON,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_jds_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. ATS Results Table
CREATE TABLE IF NOT EXISTS `ats_results` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `resume_id` INT,
    `jd_id` INT,
    `job_title` VARCHAR(200),
    `ats_score` INT DEFAULT 0,
    `keyword_match_pct` INT DEFAULT 0,
    `skill_match_pct` INT DEFAULT 0,
    `experience_match_pct` INT DEFAULT 0,
    `matching_skills` JSON,
    `missing_skills` JSON,
    `missing_keywords` JSON,
    `formatting_warnings` JSON,
    `recommendations` JSON,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_ats_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. Skills & Proficiency Table
CREATE TABLE IF NOT EXISTS `skills` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `skill_name` VARCHAR(100) NOT NULL,
    `category` VARCHAR(60) DEFAULT 'Technical',
    `status` VARCHAR(40) DEFAULT 'Need Improvement',
    `proficiency_score` INT DEFAULT 50,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_skills_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 7. Career Roadmaps Table
CREATE TABLE IF NOT EXISTS `career_roadmaps` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `target_role` VARCHAR(120) NOT NULL,
    `roadmap_json` JSON NOT NULL,
    `is_saved` TINYINT DEFAULT 1,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_roadmaps_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 8. Learning Goals Table
CREATE TABLE IF NOT EXISTS `learning_goals` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `topic` VARCHAR(120) NOT NULL,
    `goal_description` TEXT,
    `progress_pct` INT DEFAULT 0,
    `study_hours` DECIMAL(6,2) DEFAULT 0.00,
    `completed_lessons` INT DEFAULT 0,
    `total_lessons` INT DEFAULT 10,
    `start_date` VARCHAR(30),
    `target_date` VARCHAR(30),
    `notes` TEXT,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT `fk_goals_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 9. Uploaded Documents Table
CREATE TABLE IF NOT EXISTS `uploaded_documents` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `filename` VARCHAR(255) NOT NULL,
    `doc_type` VARCHAR(20) DEFAULT 'PDF',
    `raw_text` MEDIUMTEXT NOT NULL,
    `summary` TEXT,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_docs_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 10. Document Chat History Table
CREATE TABLE IF NOT EXISTS `doc_chat_history` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `doc_id` INT NOT NULL,
    `role` VARCHAR(20) NOT NULL,
    `message` TEXT NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_chat_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_chat_doc` FOREIGN KEY (`doc_id`) REFERENCES `uploaded_documents` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 11. Notes Table
CREATE TABLE IF NOT EXISTS `notes` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `title` VARCHAR(200) NOT NULL,
    `content` MEDIUMTEXT NOT NULL,
    `category` VARCHAR(60) DEFAULT 'General',
    `is_pinned` TINYINT DEFAULT 0,
    `ai_summary` TEXT,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT `fk_notes_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 12. Tasks Table
CREATE TABLE IF NOT EXISTS `tasks` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `title` VARCHAR(200) NOT NULL,
    `description` TEXT,
    `priority` VARCHAR(30) DEFAULT 'Medium',
    `category` VARCHAR(60) DEFAULT 'General',
    `status` VARCHAR(30) DEFAULT 'Pending',
    `due_date` VARCHAR(30),
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT `fk_tasks_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 13. Reminders Table
CREATE TABLE IF NOT EXISTS `reminders` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `title` VARCHAR(200) NOT NULL,
    `reminder_type` VARCHAR(60) DEFAULT 'Custom',
    `due_date` VARCHAR(50) NOT NULL,
    `is_completed` TINYINT DEFAULT 0,
    `notes` TEXT,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_reminders_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 14. Job Applications Table
CREATE TABLE IF NOT EXISTS `job_applications` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `company` VARCHAR(120) NOT NULL,
    `position` VARCHAR(120) NOT NULL,
    `job_url` VARCHAR(500) DEFAULT '',
    `application_date` VARCHAR(30) NOT NULL,
    `status` VARCHAR(40) DEFAULT 'Applied',
    `interview_date` VARCHAR(50) DEFAULT '',
    `notes` TEXT,
    `salary_range` VARCHAR(100) DEFAULT '',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT `fk_apps_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 15. Interview Sessions Table
CREATE TABLE IF NOT EXISTS `interview_sessions` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `target_role` VARCHAR(120) NOT NULL,
    `question_type` VARCHAR(60) DEFAULT 'Technical',
    `questions_json` JSON NOT NULL,
    `answers_json` JSON,
    `evaluation_json` JSON,
    `overall_score` INT DEFAULT 0,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_interview_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
