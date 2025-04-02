-- 更新职位表结构
BEGIN;

-- 1. 添加新字段
ALTER TABLE jobs
    ADD COLUMN IF NOT EXISTS department VARCHAR(100),
    ADD COLUMN IF NOT EXISTS salary_structure TEXT,
    ADD COLUMN IF NOT EXISTS preferences TEXT;

-- 2. 更新 salary_type 的检查约束
ALTER TABLE jobs
    DROP CONSTRAINT IF EXISTS jobs_salary_type_check;

ALTER TABLE jobs
    ADD CONSTRAINT jobs_salary_type_check 
    CHECK (salary_type IN ('日薪', '月薪', '年薪', '面议'));

-- 3. 添加薪资范围检查约束
ALTER TABLE jobs
    ADD CONSTRAINT jobs_salary_check 
    CHECK (
        (salary_type = '面议') OR 
        (salary_min IS NOT NULL AND salary_max IS NOT NULL AND salary_max >= salary_min)
    );

-- 4. 添加字段注释
COMMENT ON COLUMN jobs.department IS '所属部门';
COMMENT ON COLUMN jobs.salary_structure IS '薪资构成说明，如基本工资、绩效奖金等';
COMMENT ON COLUMN jobs.preferences IS '加分项说明，非必需的优先考虑条件';
COMMENT ON COLUMN jobs.salary_type IS '薪资类型：日薪、月薪、年薪或面议';

-- 5. 添加新的索引
CREATE INDEX IF NOT EXISTS idx_jobs_tenant ON jobs(tenant_id);
CREATE INDEX IF NOT EXISTS idx_jobs_publisher ON jobs(publisher_id);
CREATE INDEX IF NOT EXISTS idx_jobs_department ON jobs(department);
CREATE INDEX IF NOT EXISTS idx_jobs_salary_type ON jobs(salary_type);
CREATE INDEX IF NOT EXISTS idx_jobs_location ON jobs(location);

COMMIT;

-- 回滚脚本
/*
BEGIN;

-- 删除新增的索引
DROP INDEX IF EXISTS idx_jobs_tenant;
DROP INDEX IF EXISTS idx_jobs_publisher;
DROP INDEX IF EXISTS idx_jobs_department;
DROP INDEX IF EXISTS idx_jobs_salary_type;
DROP INDEX IF EXISTS idx_jobs_location;

-- 删除约束
ALTER TABLE jobs
    DROP CONSTRAINT IF EXISTS jobs_salary_check;

ALTER TABLE jobs
    DROP CONSTRAINT IF EXISTS jobs_salary_type_check;

ALTER TABLE jobs
    ADD CONSTRAINT jobs_salary_type_check 
    CHECK (salary_type IN ('日薪', '月薪', '年薪'));

-- 删除新增字段
ALTER TABLE jobs
    DROP COLUMN IF EXISTS department,
    DROP COLUMN IF EXISTS salary_structure,
    DROP COLUMN IF EXISTS preferences;

COMMIT;
*/ 