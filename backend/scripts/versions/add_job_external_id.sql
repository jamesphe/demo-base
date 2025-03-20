-- 添加 external_id 字段到 jobs 表
ALTER TABLE jobs 
ADD COLUMN IF NOT EXISTS external_id VARCHAR(100);

-- 添加唯一约束
ALTER TABLE jobs 
ADD CONSTRAINT jobs_external_id_key UNIQUE (external_id);

-- 添加索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_jobs_external_id ON jobs(external_id);

-- 添加注释
COMMENT ON COLUMN jobs.external_id IS '职位外部编号，用于与外部系统对接'; 