-- 用户表
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(255),
    hashed_password VARCHAR(255) NOT NULL,
    avatar VARCHAR(255),
    introduction VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    is_superuser BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 职位表
CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    requirements TEXT,
    salary_range VARCHAR(100),
    location VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 候选人表
CREATE TABLE candidates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    resume_url VARCHAR(255),
    status VARCHAR(50) DEFAULT 'pending',  -- pending, interviewing, rejected, hired
    job_id INTEGER REFERENCES jobs(id),  -- 新增职位关联
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 面试表
CREATE TABLE interviews (
    id SERIAL PRIMARY KEY,
    candidate_id INTEGER REFERENCES candidates(id),
    interviewer_id INTEGER REFERENCES users(id),
    job_id INTEGER REFERENCES jobs(id),
    status VARCHAR(50) DEFAULT 'scheduled',  -- scheduled, completed, cancelled
    schedule_time TIMESTAMP,
    feedback VARCHAR(1000),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 简历库表
CREATE TABLE resume_repositories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    resume_type VARCHAR(20) DEFAULT 'general' NOT NULL,
    description TEXT,
    processing_status VARCHAR(20) DEFAULT 'pending',
    processing_message VARCHAR(200),
    processing_started_at TIMESTAMP,
    processing_completed_at TIMESTAMP,
    processing_error VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 简历表
CREATE TABLE resumes (
    id SERIAL PRIMARY KEY,
    resume_id VARCHAR(100) UNIQUE,
    repository_id INTEGER REFERENCES resume_repositories(id),
    candidate_id INTEGER REFERENCES candidates(id),
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_type VARCHAR(50),  -- pdf, doc, docx
    resume_type VARCHAR(20) DEFAULT 'general',
    content TEXT,
    parsed_data JSONB,
    
    -- 处理状态
    processing_status VARCHAR(20) DEFAULT 'pending',
    processing_message VARCHAR(200),
    processing_started_at TIMESTAMP,
    processing_completed_at TIMESTAMP,
    processing_error TEXT,
    
    -- 个人信息
    name VARCHAR(100),
    gender VARCHAR(10),
    birthdate TIMESTAMP,
    id_number VARCHAR(50),
    phone VARCHAR(20),
    email VARCHAR(100),
    
    -- 教育信息
    highest_education VARCHAR(50),
    highest_degree VARCHAR(50),
    major VARCHAR(100),
    graduate_school VARCHAR(100),
    graduation_date TIMESTAMP,
    
    -- 工作经验
    experience_years INTEGER,
    current_company VARCHAR(100),
    current_position VARCHAR(100),
    current_salary VARCHAR(50),
    work_history JSONB,
    
    -- 求职意向
    expected_position VARCHAR(100),
    expected_salary VARCHAR(50),
    expected_location VARCHAR(100),
    
    -- 技能与证书
    skills JSONB,
    certificates JSONB,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_jobs_title ON jobs(title);
CREATE INDEX idx_candidates_email ON candidates(email);
CREATE INDEX idx_interviews_candidate ON interviews(candidate_id);
CREATE INDEX idx_interviews_interviewer ON interviews(interviewer_id);
CREATE INDEX idx_resumes_repository ON resumes(repository_id);

-- 新增索引
CREATE INDEX idx_resumes_resume_id ON resumes(resume_id);
CREATE INDEX idx_candidates_job ON candidates(job_id);
CREATE INDEX idx_resumes_candidate ON resumes(candidate_id);

-- 插入初始超级管理员
INSERT INTO users (
    email,
    username,
    hashed_password,
    is_active,
    is_superuser
) VALUES (
    'admin@admin.com',
    'admin',
    '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',  -- 密码: admin
    true,
    true
);

-- 创建触发器函数来自动更新updated_at
CREATE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 为所有表添加更新时间触发器
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_jobs_updated_at
    BEFORE UPDATE ON jobs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_candidates_updated_at
    BEFORE UPDATE ON candidates
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_interviews_updated_at
    BEFORE UPDATE ON interviews
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_resume_repositories_updated_at
    BEFORE UPDATE ON resume_repositories
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_resumes_updated_at
    BEFORE UPDATE ON resumes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column(); 