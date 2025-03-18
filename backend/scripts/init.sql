-- 1. 首先创建租户表
CREATE TABLE tenant (
    id SERIAL PRIMARY KEY,
    tenant_name VARCHAR(100) NOT NULL,
    contact_person VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(100),
    address VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive'))
);

-- 2. 创建职位表
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

-- 3. 创建用户表
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER REFERENCES tenant(id),
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

-- 4. 创建人才表
CREATE TABLE talent (
    talent_id SERIAL PRIMARY KEY,
    tenant_id INTEGER REFERENCES tenant(id),
    name VARCHAR(100) NOT NULL,
    gender VARCHAR(10) CHECK (gender IN ('M', 'F')),
    birth_date DATE,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(100),
    address VARCHAR(255),
    id_number VARCHAR(50),
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    verified_status BOOLEAN DEFAULT false,
    profile_picture VARCHAR(255),
    profile_summary TEXT,
    primary_job_type VARCHAR(50),
    job_location_preference VARCHAR(100),
    expected_salary VARCHAR(50),
    data_source VARCHAR(50) CHECK (data_source IN ('个人用户', '技术学校', '人力公司', '租户自建')) DEFAULT '个人用户'
);

-- 5. 创建候选人表
CREATE TABLE candidates (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER REFERENCES tenant(id),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    resume_url VARCHAR(255),
    status VARCHAR(50) DEFAULT 'pending',
    job_id INTEGER REFERENCES jobs(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. 创建简历库表
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

-- 7. 创建简历表
CREATE TABLE resumes (
    -- 基本信息
    id SERIAL PRIMARY KEY,
    resume_id VARCHAR(100) UNIQUE,
    
    -- 文件信息
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_type VARCHAR(50),
    resume_type VARCHAR(20) DEFAULT 'general',
    content TEXT,
    parsed_data JSON,
    
    -- 处理状态
    processing_status VARCHAR(20) DEFAULT 'pending',
    processing_message VARCHAR(200),
    processing_started_at TIMESTAMP,
    processing_completed_at TIMESTAMP,
    processing_error TEXT,
    
    -- 个人基本信息
    name VARCHAR(100),
    gender VARCHAR(10),
    birthdate TIMESTAMP,
    id_number VARCHAR(50),
    phone VARCHAR(20),
    email VARCHAR(100),
    
    -- 个人状态信息
    political_status VARCHAR(50),
    marital_status VARCHAR(20),
    hukou VARCHAR(100),
    current_address VARCHAR(255),
    
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
    work_time VARCHAR(50),
    work_history JSON,
    
    -- 求职意向
    expected_position VARCHAR(100),
    expected_salary VARCHAR(50),
    expected_location VARCHAR(100),
    
    -- 技能与证书
    skills JSON,
    certificates JSON,
    
    -- 匹配状态
    matching_status VARCHAR(20) CHECK (matching_status IN ('待匹配', '已匹配', '待确认', '新人才')) DEFAULT '待匹配',
    matching_score INTEGER,
    
    -- 版本信息
    resume_version INTEGER DEFAULT 1,
    is_latest BOOLEAN DEFAULT true,
    
    -- 来源信息
    source_channel VARCHAR(50),
    source_batch VARCHAR(100),
    
    -- 质量评分
    completeness_score INTEGER,
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 关联关系
    repository_id INTEGER REFERENCES resume_repositories(id),
    candidate_id INTEGER REFERENCES candidates(id),
    talent_id INTEGER REFERENCES talent(talent_id),
    tenant_id INTEGER REFERENCES tenant(id),
    
    -- 需要添加的个人基本信息字段
    stature VARCHAR(20),
    weight VARCHAR(20),
    nation VARCHAR(50),
    english_level VARCHAR(50),
    city VARCHAR(100),
    district VARCHAR(100),
    
    -- 需要添加的职称信息字段
    talent_name VARCHAR(100),
    talent_team VARCHAR(100),
    talent_type VARCHAR(100),
    title_rank VARCHAR(100),
    
    -- 需要添加的经历信息字段
    edu_experience JSON,
    awards JSON,
    
    -- 需要添加的其他信息字段
    family_situation VARCHAR(255),
    other_info VARCHAR(255)
);

-- 8. 创建面试表
CREATE TABLE interviews (
    id SERIAL PRIMARY KEY,
    candidate_id INTEGER REFERENCES candidates(id),
    interviewer_id INTEGER REFERENCES users(id),
    job_id INTEGER REFERENCES jobs(id),
    status VARCHAR(50) DEFAULT 'scheduled',
    schedule_time TIMESTAMP,
    feedback VARCHAR(1000),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 9. 其他表...

-- 创建索引
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_jobs_title ON jobs(title);
CREATE INDEX idx_candidates_email ON candidates(email);
CREATE INDEX idx_candidates_job ON candidates(job_id);
CREATE INDEX idx_interviews_candidate ON interviews(candidate_id);
CREATE INDEX idx_interviews_interviewer ON interviews(interviewer_id);
CREATE INDEX idx_resumes_repository ON resumes(repository_id);
CREATE INDEX idx_resumes_resume_id ON resumes(resume_id);
CREATE INDEX idx_resumes_candidate ON resumes(candidate_id);
CREATE INDEX idx_resumes_talent ON resumes(talent_id);
CREATE INDEX idx_resumes_tenant ON resumes(tenant_id);
CREATE INDEX idx_matching_status ON resumes(matching_status);
CREATE INDEX idx_is_latest ON resumes(is_latest);

-- 10. 人才认证表
CREATE TABLE talent_certification (
    certification_id SERIAL PRIMARY KEY,
    talent_id INTEGER REFERENCES talent(talent_id) NOT NULL,
    certification_name VARCHAR(100) NOT NULL,
    issuing_organization VARCHAR(100),
    issue_date DATE,
    expiration_date DATE,
    document_url VARCHAR(255)
);

-- 11. 教育经历表
CREATE TABLE talent_education (
    education_id SERIAL PRIMARY KEY,
    talent_id INTEGER REFERENCES talent(talent_id) NOT NULL,
    institution_name VARCHAR(255) NOT NULL,
    degree VARCHAR(100),
    field_of_study VARCHAR(100),
    start_date DATE,
    graduation_date DATE,
    certificate_url VARCHAR(255),
    description TEXT
);

-- 12. 工作经历表
CREATE TABLE talent_experience (
    experience_id SERIAL PRIMARY KEY,
    talent_id INTEGER REFERENCES talent(talent_id) NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    position VARCHAR(100) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    job_description TEXT,
    achievements TEXT,
    attachment_url VARCHAR(255)
);

-- 13. 技能表
CREATE TABLE skill (
    skill_id SERIAL PRIMARY KEY,
    skill_name VARCHAR(100) NOT NULL,
    skill_description TEXT,
    category VARCHAR(50)
);

-- 14. 人才技能关联表
CREATE TABLE talent_skill (
    talent_skill_id SERIAL PRIMARY KEY,
    talent_id INTEGER REFERENCES talent(talent_id) NOT NULL,
    skill_id INTEGER REFERENCES skill(skill_id) NOT NULL
);

-- 15. 人才库表
CREATE TABLE talent_pool (
    pool_id SERIAL PRIMARY KEY,
    tenant_id INTEGER REFERENCES tenant(id) NOT NULL,
    pool_name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 16. 人才库成员表
CREATE TABLE talent_pool_member (
    member_id SERIAL PRIMARY KEY,
    pool_id INTEGER REFERENCES talent_pool(pool_id) NOT NULL,
    talent_id INTEGER REFERENCES talent(talent_id) NOT NULL,
    remark VARCHAR(255),
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 17. 角色表
CREATE TABLE role (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description VARCHAR(255)
);

-- 18. 权限表
CREATE TABLE permission (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description VARCHAR(255)
);

-- 19. 角色-权限关联表
CREATE TABLE role_permission (
    id SERIAL PRIMARY KEY,
    role_id INTEGER REFERENCES role(id),
    permission_id INTEGER REFERENCES permission(id)
);

-- 20. 用户-角色关联表
CREATE TABLE user_role (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    role_id INTEGER REFERENCES role(id)
);

-- 21. LLM配置表
CREATE TABLE llm_configs (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    provider VARCHAR(50) NOT NULL,
    api_url VARCHAR(255),
    api_key VARCHAR(255),
    chat_model VARCHAR(100) NOT NULL,
    chat_config JSONB,
    embedding_model VARCHAR(100),
    embedding_config JSONB,
    is_default BOOLEAN DEFAULT false,
    is_enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建触发器函数来自动更新updated_at
DROP FUNCTION IF EXISTS update_updated_at_column CASCADE;
CREATE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 为所有表添加更新时间触发器
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
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

-- 添加相关索引
CREATE INDEX idx_role_name ON role(name);
CREATE INDEX idx_permission_name ON permission(name);
CREATE INDEX idx_role_permission_role ON role_permission(role_id);
CREATE INDEX idx_role_permission_permission ON role_permission(permission_id);
CREATE INDEX idx_user_role_user ON user_role(user_id);
CREATE INDEX idx_user_role_role ON user_role(role_id);

-- 为这些表也添加更新时间触发器
CREATE TRIGGER update_role_updated_at
    BEFORE UPDATE ON role
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_permission_updated_at
    BEFORE UPDATE ON permission
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 为LLM配置表添加更新时间触发器
CREATE TRIGGER update_llm_configs_updated_at
    BEFORE UPDATE ON llm_configs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 插入默认LLM配置
INSERT INTO llm_configs (
    name,
    provider,
    api_url,
    api_key,
    chat_model,
    chat_config,
    embedding_model,
    is_default,
    is_enabled
) VALUES (
    '豆包pro-256k',
    'openai_compatible',
    'https://ark.cn-beijing.volces.com/api/v3',
    'f3f927f8-8039-4cdd-9b19-b81a63c07da0',
    'ep-20250220171328-j24rc',
    '{"temperature": 0.6, "max_tokens": 8000}',
    'ep-20250220171131-79jk8',
    true,
    true
);

-- 创建索引
CREATE INDEX idx_talent_tenant ON talent(tenant_id);
CREATE INDEX idx_talent_phone ON talent(phone);
CREATE INDEX idx_talent_email ON talent(email);
CREATE INDEX idx_certification_talent ON talent_certification(talent_id);
CREATE INDEX idx_education_talent ON talent_education(talent_id);
CREATE INDEX idx_experience_talent ON talent_experience(talent_id);
CREATE INDEX idx_talent_skill_talent ON talent_skill(talent_id);
CREATE INDEX idx_talent_skill_skill ON talent_skill(skill_id);
CREATE INDEX idx_talent_pool_tenant ON talent_pool(tenant_id);
CREATE INDEX idx_pool_member_pool ON talent_pool_member(pool_id);
CREATE INDEX idx_pool_member_talent ON talent_pool_member(talent_id);

-- 为新表添加更新时间触发器
CREATE TRIGGER update_talent_pool_updated_at
    BEFORE UPDATE ON talent_pool
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 创建索引
CREATE INDEX idx_llm_configs_name ON llm_configs(name);

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

-- 添加新的索引
CREATE INDEX idx_resumes_source_channel ON resumes(source_channel);
CREATE INDEX idx_resumes_matching_status ON resumes(matching_status);
CREATE INDEX idx_resumes_source_batch ON resumes(source_batch);

-- 为租户表添加触发器（确保在文件最后部分的触发器创建部分）
CREATE TRIGGER update_tenant_updated_at
    BEFORE UPDATE ON tenant
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 创建通知表
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    type VARCHAR(50) NOT NULL,  -- system, resume, interview 等
    user_id INTEGER REFERENCES users(id) NOT NULL,
    tenant_id INTEGER REFERENCES tenant(id),
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 添加索引
CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_tenant ON notifications(tenant_id);

-- 添加更新时间触发器
CREATE TRIGGER update_notifications_updated_at
    BEFORE UPDATE ON notifications
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column(); 