-- 更新 jobs 表结构
BEGIN;

-- 1. 备份旧数据
CREATE TABLE jobs_backup AS SELECT * FROM jobs;

-- 2. 删除旧表的外键约束
-- ALTER TABLE candidates DROP CONSTRAINT IF EXISTS candidates_job_id_fkey;
ALTER TABLE interviews DROP CONSTRAINT IF EXISTS interviews_job_id_fkey;

-- 3. 删除旧表
DROP TABLE jobs;

-- 4. 创建新表
CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL REFERENCES tenant(id),
    publisher_id INTEGER NOT NULL REFERENCES users(id),
    title VARCHAR(255) NOT NULL,
    job_type VARCHAR(50) NOT NULL,
    headcount INTEGER NOT NULL DEFAULT 1,
    salary_min DECIMAL(10,2),
    salary_max DECIMAL(10,2),
    salary_type VARCHAR(10) CHECK (salary_type IN ('日薪','月薪','年薪')) NOT NULL,
    location VARCHAR(255) NOT NULL,
    experience_required VARCHAR(50),
    education_required VARCHAR(50),
    description TEXT,
    requirements TEXT,
    benefits TEXT,
    status VARCHAR(20) CHECK (status IN ('draft','published','closed')) DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    published_at TIMESTAMP,
    closed_at TIMESTAMP
);

-- 5. 创建索引
CREATE INDEX idx_jobs_tenant ON jobs(tenant_id);
CREATE INDEX idx_jobs_publisher ON jobs(publisher_id);
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_job_type ON jobs(job_type);

-- 6. 迁移旧数据
INSERT INTO jobs (
    id,
    tenant_id,
    publisher_id,
    title,
    job_type,
    description,
    requirements,
    location,
    status,
    created_at,
    updated_at
)
SELECT 
    id,
    -- 假设第一个租户和管理员用户
    1 as tenant_id,
    1 as publisher_id,
    title,
    '未分类' as job_type,
    description,
    requirements,
    location,
    'published' as status,  -- 默认设置为已发布状态
    created_at,
    updated_at
FROM jobs_backup;

-- 7. 重新创建外键约束
-- ALTER TABLE candidates 
--     ADD CONSTRAINT candidates_job_id_fkey 
--     FOREIGN KEY (job_id) REFERENCES jobs(id);

ALTER TABLE interviews 
    ADD CONSTRAINT interviews_job_id_fkey 
    FOREIGN KEY (job_id) REFERENCES jobs(id);

-- 8. 删除备份表
DROP TABLE jobs_backup;

-- 9. 添加更新时间触发器
CREATE TRIGGER update_jobs_updated_at
    BEFORE UPDATE ON jobs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

COMMIT; 