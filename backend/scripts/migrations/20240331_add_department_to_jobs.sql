-- 更新职位表，添加所属部门字段
BEGIN;

-- 1. 检查字段是否已存在，如果不存在则添加
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'jobs' 
        AND column_name = 'department'
    ) THEN
        -- 添加 department 字段
        ALTER TABLE jobs 
        ADD COLUMN department VARCHAR(100);
        
        RAISE NOTICE '已添加 department 字段到 jobs 表';
    ELSE
        RAISE NOTICE 'department 字段已存在，跳过添加';
    END IF;
END
$$;

-- 2. 检查索引是否已存在，如果不存在则创建
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM pg_indexes 
        WHERE tablename = 'jobs' 
        AND indexname = 'idx_jobs_department'
    ) THEN
        -- 创建部门索引
        CREATE INDEX idx_jobs_department 
        ON jobs(department);
        
        RAISE NOTICE '已创建 idx_jobs_department 索引';
    ELSE
        RAISE NOTICE 'idx_jobs_department 索引已存在，跳过创建';
    END IF;
END
$$;

-- 3. 添加字段注释
COMMENT ON COLUMN jobs.department IS '所属部门';

-- 4. 更新现有数据（如果需要）
-- UPDATE jobs 
-- SET department = '未分类'
-- WHERE department IS NULL;

COMMIT;

-- 输出升级完成信息
DO $$
BEGIN
    RAISE NOTICE '数据库升级完成：已添加所属部门字段';
END
$$;

-- 回滚脚本
/*
BEGIN;

-- 删除索引
DROP INDEX IF EXISTS idx_jobs_department;

-- 删除字段
ALTER TABLE jobs DROP COLUMN IF EXISTS department;

COMMIT;
*/ 