-- 添加租户ID到简历库表
BEGIN;

-- 1. 备份旧数据
CREATE TABLE resume_repositories_backup AS SELECT * FROM resume_repositories;

-- 2. 删除旧表的外键约束
ALTER TABLE resumes DROP CONSTRAINT IF EXISTS resumes_repository_id_fkey;

-- 3. 删除旧表
DROP TABLE resume_repositories;

-- 4. 创建新表
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

-- 5. 创建索引
CREATE INDEX idx_resume_repositories_tenant ON resume_repositories(tenant_id);
CREATE INDEX idx_resume_repositories_type ON resume_repositories(resume_type);
CREATE INDEX idx_resume_repositories_status ON resume_repositories(processing_status);

-- 6. 添加更新时间触发器
CREATE TRIGGER update_resume_repositories_updated_at
    BEFORE UPDATE ON resume_repositories
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 7. 迁移旧数据（假设默认租户ID为1）
INSERT INTO resume_repositories (
    id,
    name,
    resume_type,
    description,
    processing_status,
    processing_message,
    processing_started_at,
    processing_completed_at,
    processing_error,
    created_at,
    updated_at,
    tenant_id
)
SELECT 
    id,
    name,
    resume_type,
    description,
    processing_status,
    processing_message,
    processing_started_at,
    processing_completed_at,
    processing_error,
    created_at,
    updated_at,
    1 as tenant_id  -- 设置默认租户ID
FROM resume_repositories_backup;

-- 8. 重新创建外键约束
ALTER TABLE resumes 
    ADD CONSTRAINT resumes_repository_id_fkey 
    FOREIGN KEY (repository_id) REFERENCES resume_repositories(id);

-- 9. 添加注释
COMMENT ON TABLE resume_repositories IS '简历库表';
COMMENT ON COLUMN resume_repositories.tenant_id IS '租户ID';
COMMENT ON COLUMN resume_repositories.resume_type IS '简历类型，默认为general';
COMMENT ON COLUMN resume_repositories.processing_status IS '处理状态';

-- 10. 删除备份表
DROP TABLE resume_repositories_backup;

COMMIT;

-- 回滚脚本
/*
BEGIN;
-- 1. 备份数据
CREATE TABLE resume_repositories_backup AS SELECT * FROM resume_repositories;

-- 2. 删除外键约束
ALTER TABLE resumes DROP CONSTRAINT IF EXISTS resumes_repository_id_fkey;

-- 3. 删除新表
DROP TABLE resume_repositories;

-- 4. 创建旧表结构
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

-- 5. 恢复数据（不包含tenant_id）
INSERT INTO resume_repositories (
    id, name, resume_type, description,
    processing_status, processing_message,
    processing_started_at, processing_completed_at,
    processing_error, created_at, updated_at
)
SELECT 
    id, name, resume_type, description,
    processing_status, processing_message,
    processing_started_at, processing_completed_at,
    processing_error, created_at, updated_at
FROM resume_repositories_backup;

-- 6. 重新创建外键约束
ALTER TABLE resumes 
    ADD CONSTRAINT resumes_repository_id_fkey 
    FOREIGN KEY (repository_id) REFERENCES resume_repositories(id);

-- 7. 删除备份表
DROP TABLE resume_repositories_backup;

COMMIT;
*/ 