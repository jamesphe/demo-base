-- 创建触发器函数
DROP FUNCTION IF EXISTS update_updated_at_column CASCADE;
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 1. 租户表 (最基础的表，许多表都依赖它)
CREATE TABLE tenant (
    id SERIAL PRIMARY KEY,
    tenant_name VARCHAR(100) NOT NULL UNIQUE,
    contact_person VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(100),
    address VARCHAR(255),
    external_id VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) CHECK (status IN ('active', 'inactive')) DEFAULT 'active'
);

-- 2. 用户表 (依赖租户表)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER REFERENCES tenant(id),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(255),
    user_type VARCHAR(20) CHECK (user_type IN ('candidate', 'tenant', 'admin')) DEFAULT 'tenant',
    hashed_password VARCHAR(255) NOT NULL,
    avatar VARCHAR(255),
    introduction VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    is_superuser BOOLEAN DEFAULT false,
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 添加手机号索引
CREATE INDEX idx_users_phone ON users(phone);

-- 3. 人才表 (依赖租户表)
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

-- 4. 职位表 (依赖租户表和用户表)
CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    external_id VARCHAR(100) UNIQUE,
    tenant_id INTEGER NOT NULL REFERENCES tenant(id),
    publisher_id INTEGER NOT NULL REFERENCES users(id),
    title VARCHAR(255) NOT NULL,
    job_type VARCHAR(50) NOT NULL,
    department VARCHAR(100),  -- 新增：所属部门
    headcount INTEGER NOT NULL DEFAULT 1,
    salary_min DECIMAL(10,2),
    salary_max DECIMAL(10,2),
    salary_type VARCHAR(10) CHECK (salary_type IN ('日薪','月薪','年薪','面议')) NOT NULL,
    salary_structure TEXT,    -- 新增：薪资构成说明
    location VARCHAR(255) NOT NULL,
    experience_required VARCHAR(50),
    education_required VARCHAR(50),
    description TEXT,
    requirements TEXT,
    benefits TEXT,
    preferences TEXT,         -- 新增：加分项说明
    status VARCHAR(20) CHECK (status IN ('draft','published','closed')) DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    published_at TIMESTAMP,
    closed_at TIMESTAMP,
    
    -- 添加薪资范围检查约束
    CONSTRAINT salary_check CHECK (
        (salary_type = '面议') OR 
        (salary_min IS NOT NULL AND salary_max IS NOT NULL AND salary_max >= salary_min)
    )
);

-- 添加注释
COMMENT ON COLUMN jobs.department IS '所属部门';
COMMENT ON COLUMN jobs.salary_structure IS '薪资构成说明，如基本工资、绩效奖金等';
COMMENT ON COLUMN jobs.preferences IS '加分项说明，非必需的优先考虑条件';
COMMENT ON COLUMN jobs.salary_type IS '薪资类型：日薪、月薪、年薪或面议';

-- 5. 候选人表 (依赖职位表)
CREATE TABLE candidates (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER REFERENCES tenant(id),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    resume_url VARCHAR(255),
    status VARCHAR(50) DEFAULT 'pending',
    job_id INTEGER REFERENCES jobs(id),
    resume_id INTEGER REFERENCES resumes(id),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 添加对应的注释
COMMENT ON COLUMN candidates.notes IS '候选人备注信息';
COMMENT ON COLUMN candidates.resume_id IS '关联的简历ID';

-- 6. 面试表 (依赖候选人表、用户表和职位表)
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

-- 7. 技能表
CREATE TABLE skills (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER REFERENCES tenant(id),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    category VARCHAR(50),
    status VARCHAR(20) CHECK (status IN ('active', 'inactive')) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 证书库表
CREATE TABLE certifications (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER REFERENCES tenant(id),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    category VARCHAR(50),
    issuing_organization VARCHAR(100),
    status VARCHAR(20) CHECK (status IN ('active', 'inactive')) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 8. 人才技能关联表 (依赖人才表和技能表)
CREATE TABLE talent_skill (
    talent_skill_id SERIAL PRIMARY KEY,
    talent_id INTEGER REFERENCES talent(talent_id) NOT NULL,
    skill_id INTEGER REFERENCES skills(id) NOT NULL
);

-- 9. 简历库表
DROP TABLE IF EXISTS resume_repositories CASCADE;
CREATE TABLE resume_repositories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    resume_type VARCHAR(50) DEFAULT 'general' NOT NULL,
    description TEXT,
    
    -- 添加租户ID字段
    tenant_id INTEGER NOT NULL REFERENCES tenant(id) ON DELETE CASCADE,
    
    -- 处理状态相关字段
    processing_status VARCHAR(20) DEFAULT 'pending',
    processing_message VARCHAR(200),
    processing_started_at TIMESTAMP WITH TIME ZONE,
    processing_completed_at TIMESTAMP WITH TIME ZONE,
    processing_error VARCHAR(500),
    
    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    -- 添加索引
    CONSTRAINT idx_resume_repositories_name_tenant UNIQUE (name, tenant_id)
);

-- 添加索引
CREATE INDEX idx_resume_repositories_tenant ON resume_repositories(tenant_id);
CREATE INDEX idx_resume_repositories_type ON resume_repositories(resume_type);
CREATE INDEX idx_resume_repositories_status ON resume_repositories(processing_status);

-- 添加更新时间触发器
CREATE TRIGGER update_resume_repositories_updated_at
    BEFORE UPDATE ON resume_repositories
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 添加注释
COMMENT ON TABLE resume_repositories IS '简历库表';
COMMENT ON COLUMN resume_repositories.tenant_id IS '租户ID';
COMMENT ON COLUMN resume_repositories.resume_type IS '简历类型，默认为general';
COMMENT ON COLUMN resume_repositories.processing_status IS '处理状态';

-- 10. 简历表
CREATE TABLE resumes (
    id SERIAL PRIMARY KEY,
    resume_id VARCHAR(100) UNIQUE NOT NULL,
    
    -- 文件信息（修改为可为NULL）
    file_name VARCHAR(255),  -- 修改为可为NULL
    file_path VARCHAR(500),  -- 修改为可为NULL
    file_type VARCHAR(50),   -- 已经是可为NULL
    resume_type VARCHAR(20) DEFAULT 'general',
    content TEXT,            -- 已经是可为NULL
    parsed_data JSONB,       -- 已经是可为NULL
    
    -- 添加手动创建标志
    is_manual_entry BOOLEAN DEFAULT FALSE,
    
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
    
    -- 项目经历
    project_experience JSON,
    
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
    other_info VARCHAR(255),
    
    -- 发布者信息
    publisher_id INTEGER REFERENCES users(id),
    publisher_type VARCHAR(20) CHECK (publisher_type IN ('candidate', 'tenant', 'admin')) NOT NULL,
    publisher_name VARCHAR(100),
    publish_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 审核信息
    review_status VARCHAR(20) CHECK (review_status IN ('pending', 'approved', 'rejected')) DEFAULT 'pending',
    reviewer_id INTEGER REFERENCES users(id),
    review_time TIMESTAMP,
    review_comment TEXT,
    
    -- 添加外键约束
    FOREIGN KEY (publisher_id) REFERENCES users(id),
    FOREIGN KEY (reviewer_id) REFERENCES users(id)
);

-- 11. 人才认证表
CREATE TABLE talent_certification (
    certification_id SERIAL PRIMARY KEY,
    talent_id INTEGER REFERENCES talent(talent_id) NOT NULL,
    certification_name VARCHAR(100) NOT NULL,
    issuing_organization VARCHAR(100),
    issue_date DATE,
    expiration_date DATE,
    document_url VARCHAR(255)
);

-- 12. 教育经历表
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

-- 13. 工作经历表
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

-- 14. 人才库表
CREATE TABLE talent_pool (
    pool_id SERIAL PRIMARY KEY,
    tenant_id INTEGER REFERENCES tenant(id) NOT NULL,
    pool_name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 15. 人才库成员表
CREATE TABLE talent_pool_member (
    member_id SERIAL PRIMARY KEY,
    pool_id INTEGER REFERENCES talent_pool(pool_id) NOT NULL,
    talent_id INTEGER REFERENCES talent(talent_id) NOT NULL,
    remark VARCHAR(255),
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 16. 角色表
CREATE TABLE role (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description VARCHAR(255)
);

-- 17. 权限表
CREATE TABLE permission (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 为权限表添加更新时间触发器
CREATE TRIGGER update_permission_updated_at
    BEFORE UPDATE ON permission
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 添加权限表索引
CREATE INDEX idx_permission_name ON permission(name);

-- 18. 角色-权限关联表
CREATE TABLE role_permission (
    id SERIAL PRIMARY KEY,
    role_id INTEGER REFERENCES role(id),
    permission_id INTEGER REFERENCES permission(id)
);

-- 19. 用户-角色关联表
CREATE TABLE user_role (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    role_id INTEGER REFERENCES role(id)
);

-- 20. LLM配置表
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

-- 21. 通知表
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

-- 为所有表添加更新时间触发器
CREATE TRIGGER update_tenant_updated_at
    BEFORE UPDATE ON tenant
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_talent_updated_at
    BEFORE UPDATE ON talent
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

CREATE TRIGGER update_skill_updated_at
    BEFORE UPDATE ON skills
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_certifications_updated_at
    BEFORE UPDATE ON certifications
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 创建索引
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_tenant ON users(tenant_id);
CREATE INDEX idx_talent_tenant ON talent(tenant_id);
CREATE INDEX idx_jobs_tenant ON jobs(tenant_id);
CREATE INDEX idx_jobs_publisher ON jobs(publisher_id);
CREATE INDEX idx_candidates_job ON candidates(job_id);
CREATE INDEX idx_candidates_tenant ON candidates(tenant_id);
CREATE INDEX idx_candidates_resume ON candidates(resume_id);
CREATE INDEX idx_interviews_candidate ON interviews(candidate_id);
CREATE INDEX idx_interviews_job ON interviews(job_id);
CREATE INDEX idx_skill_tenant ON skills(tenant_id);
CREATE INDEX idx_skill_status ON skills(status);
CREATE INDEX idx_talent_skill_talent ON talent_skill(talent_id);
CREATE INDEX idx_talent_skill_skill ON talent_skill(skill_id);
CREATE INDEX idx_certification_tenant ON certifications(tenant_id);
CREATE INDEX idx_certification_status ON certifications(status); 

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
CREATE INDEX idx_talent_phone ON talent(phone);
CREATE INDEX idx_talent_email ON talent(email);
CREATE INDEX idx_certification_talent ON talent_certification(talent_id);
CREATE INDEX idx_education_talent ON talent_education(talent_id);
CREATE INDEX idx_experience_talent ON talent_experience(talent_id);
CREATE INDEX idx_talent_pool_tenant ON talent_pool(tenant_id);
CREATE INDEX idx_pool_member_pool ON talent_pool_member(pool_id);
CREATE INDEX idx_pool_member_talent ON talent_pool_member(talent_id);
CREATE INDEX idx_llm_configs_name ON llm_configs(name);

-- 插入初始超级管理员
INSERT INTO users (
    email,
    username,
    hashed_password,
    user_type,
    is_active,
    is_superuser
) VALUES (
    'admin@admin.com',
    'admin',
    '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',  -- 密码: admin
    'admin',
    true,
    true
);

-- 添加新的索引
CREATE INDEX idx_resumes_source_channel ON resumes(source_channel);
CREATE INDEX idx_resumes_matching_status ON resumes(matching_status);
CREATE INDEX idx_resumes_source_batch ON resumes(source_batch);

-- 添加索引
CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_tenant ON notifications(tenant_id);

-- 创建职位相关的索引
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_job_type ON jobs(job_type);
CREATE INDEX idx_jobs_salary_type ON jobs(salary_type);
CREATE INDEX idx_jobs_location ON jobs(location);

-- 职位-技能要求关联表
CREATE TABLE job_required_skills (
    id SERIAL PRIMARY KEY,
    job_id INTEGER NOT NULL REFERENCES jobs(id),
    skill_id INTEGER NOT NULL REFERENCES skills(id),
    skill_level VARCHAR(50) NOT NULL,
    is_required BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 职位-证书要求关联表
CREATE TABLE job_required_certifications (
    id SERIAL PRIMARY KEY,
    job_id INTEGER NOT NULL REFERENCES jobs(id),
    certification_id INTEGER NOT NULL REFERENCES certifications(id),
    is_required BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 职位申请记录表
DROP TABLE IF EXISTS job_applications;
CREATE TABLE job_applications (
    id SERIAL PRIMARY KEY,
    job_id INTEGER NOT NULL REFERENCES jobs(id),
    resume_id INTEGER NOT NULL REFERENCES resumes(id),
    status VARCHAR(20) CHECK (
        status IN (
            'pending',
            'reviewed',
            'interviewed',
            'offered',
            'rejected',
            'withdrawn'
        )
    ) DEFAULT 'pending',
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 恢复重要的业务字段
    apply_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    review_time TIMESTAMP,
    review_notes TEXT,
    
    -- 添加租户ID字段
    tenant_id INTEGER REFERENCES tenant(id),
    
    -- 添加匹配度和匹配理由字段
    match_score FLOAT DEFAULT 0.0,
    match_reason TEXT
);

-- 添加触发器
CREATE TRIGGER update_job_applications_updated_at
    BEFORE UPDATE ON job_applications
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 添加索引
CREATE INDEX idx_job_applications_job ON job_applications(job_id);
CREATE INDEX idx_job_applications_resume ON job_applications(resume_id);
CREATE INDEX idx_job_applications_status ON job_applications(status);
CREATE INDEX idx_job_applications_tenant ON job_applications(tenant_id);
CREATE INDEX idx_job_applications_created_by ON job_applications(created_by);
CREATE INDEX idx_job_applications_match_score ON job_applications(match_score);

-- 添加新的索引
CREATE INDEX idx_resumes_publisher ON resumes(publisher_id);
CREATE INDEX idx_resumes_reviewer ON resumes(reviewer_id);
CREATE INDEX idx_resumes_review_status ON resumes(review_status);

-- 为新字段添加索引
CREATE INDEX idx_resumes_is_manual_entry ON resumes(is_manual_entry);

-- 添加注释
COMMENT ON COLUMN resumes.is_manual_entry IS '是否为手动创建的简历（无文件）';
COMMENT ON COLUMN resumes.file_name IS '文件名（可为空，表示手动创建的简历）';
COMMENT ON COLUMN resumes.file_path IS '文件路径（可为空，表示手动创建的简历）';

-- 试用申请表
DROP TABLE IF EXISTS trial_applications CASCADE;
CREATE TABLE trial_applications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),  -- 改为可空
    company_name VARCHAR(255) NOT NULL,
    contact_name VARCHAR(100) NOT NULL,
    contact_phone VARCHAR(20) NOT NULL,
    contact_email VARCHAR(255) NOT NULL,
    
    -- 新增字段
    company_size VARCHAR(50),
    business_description TEXT,
    application_reason TEXT,
    
    status VARCHAR(20) CHECK (
        status IN (
            'pending',
            'active', 
            'rejected',
            'expired'
        )
    ) DEFAULT 'pending',
    reject_reason TEXT,
    trial_start_date TIMESTAMP,
    trial_end_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 添加触发器
CREATE TRIGGER update_trial_applications_updated_at
    BEFORE UPDATE ON trial_applications
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 添加索引
CREATE INDEX idx_trial_applications_user ON trial_applications(user_id);
CREATE INDEX idx_trial_applications_status ON trial_applications(status);
CREATE INDEX idx_trial_applications_dates ON trial_applications(trial_start_date, trial_end_date);

-- 添加注释
COMMENT ON TABLE trial_applications IS '试用申请表';
COMMENT ON COLUMN trial_applications.user_id IS '申请用户ID（可选）';
COMMENT ON COLUMN trial_applications.company_name IS '公司名称';
COMMENT ON COLUMN trial_applications.contact_name IS '联系人姓名';
COMMENT ON COLUMN trial_applications.contact_phone IS '联系电话';
COMMENT ON COLUMN trial_applications.contact_email IS '联系邮箱';
COMMENT ON COLUMN trial_applications.company_size IS '公司规模';
COMMENT ON COLUMN trial_applications.business_description IS '业务描述';
COMMENT ON COLUMN trial_applications.application_reason IS '申请原因';
COMMENT ON COLUMN trial_applications.status IS '申请状态(pending:待审核,active:试用中,rejected:已拒绝,expired:已过期)';
COMMENT ON COLUMN trial_applications.reject_reason IS '拒绝原因';
COMMENT ON COLUMN trial_applications.trial_start_date IS '试用开始时间';
COMMENT ON COLUMN trial_applications.trial_end_date IS '试用结束时间';

-- 添加索引
CREATE INDEX idx_jobs_tenant ON jobs(tenant_id);
CREATE INDEX idx_jobs_publisher ON jobs(publisher_id);
CREATE INDEX idx_jobs_department ON jobs(department);
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_job_type ON jobs(job_type);
CREATE INDEX idx_jobs_salary_type ON jobs(salary_type);
CREATE INDEX idx_jobs_location ON jobs(location);

