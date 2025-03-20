-- 数据库更新脚本：将job_application表更新为job_applications表
-- 创建于：2025-03-20

-- 步骤1：创建新表
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
    apply_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    review_time TIMESTAMP,
    review_notes TEXT,
    tenant_id INTEGER REFERENCES tenant(id)
);

-- 步骤2：如果旧表存在，迁移数据
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'job_application') THEN
        -- 迁移数据（将旧表中的数据复制到新表）
        INSERT INTO job_applications (
            id, job_id, resume_id, status, 
            created_at, updated_at, 
            apply_time, review_time, review_notes
        )
        SELECT 
            application_id, job_id, resume_id, status, 
            created_at, updated_at, 
            apply_time, review_time, review_notes
        FROM job_application;
        
        -- 更新序列，确保新记录不会与已迁移的记录冲突
        PERFORM setval(
            pg_get_serial_sequence('job_applications', 'id'),
            (SELECT MAX(id) FROM job_applications),
            true
        );
        
        -- 删除旧表
        DROP TABLE job_application;
    END IF;
END
$$;

-- 步骤3：添加触发器
DROP TRIGGER IF EXISTS update_job_applications_updated_at ON job_applications;
CREATE TRIGGER update_job_applications_updated_at
    BEFORE UPDATE ON job_applications
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 步骤4：添加索引
CREATE INDEX IF NOT EXISTS idx_job_applications_job ON job_applications(job_id);
CREATE INDEX IF NOT EXISTS idx_job_applications_resume ON job_applications(resume_id);
CREATE INDEX IF NOT EXISTS idx_job_applications_status ON job_applications(status);
CREATE INDEX IF NOT EXISTS idx_job_applications_tenant ON job_applications(tenant_id);
CREATE INDEX IF NOT EXISTS idx_job_applications_created_by ON job_applications(created_by);

-- 步骤5：更新外键关系（如果需要）
-- 如果有其他表引用了job_application表，需要更新这些外键关系
-- 例如：
-- ALTER TABLE some_table 
-- DROP CONSTRAINT some_table_application_id_fkey,
-- ADD CONSTRAINT some_table_application_id_fkey 
-- FOREIGN KEY (application_id) REFERENCES job_applications(id);

-- 步骤6：添加注释
COMMENT ON TABLE job_applications IS '职位申请记录表';
COMMENT ON COLUMN job_applications.tenant_id IS '租户ID，用于多租户隔离';
COMMENT ON COLUMN job_applications.created_by IS '创建者ID，引用users表'; 