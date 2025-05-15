-- 首先备份现有数据
CREATE TABLE job_applications_backup AS SELECT * FROM job_applications;

-- 创建新的枚举类型
DO $$ 
BEGIN
    -- 如果枚举类型已存在，先删除
    IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'application_status_new') THEN
        DROP TYPE application_status_new;
    END IF;
    
    -- 创建新的枚举类型
    CREATE TYPE application_status_new AS ENUM (
        'pending',
        'reviewed',
        'interview_scheduled',
        'interviewed',
        'offered',
        'rejected',
        'withdrawn'
    );
END $$;

-- 将现有数据转换为新类型
ALTER TABLE job_applications 
    ALTER COLUMN status TYPE application_status_new 
    USING status::text::application_status_new;

-- 处理依赖关系
DO $$
DECLARE
    r RECORD;
BEGIN
    -- 查找所有依赖
    FOR r IN (
        SELECT DISTINCT dependent_ns.nspname as dependent_schema,
               dependent_view.relname as dependent_view
        FROM pg_depend 
        JOIN pg_rewrite ON pg_depend.objid = pg_rewrite.oid 
        JOIN pg_class as dependent_view ON pg_rewrite.ev_class = dependent_view.oid 
        JOIN pg_class as source_table ON pg_depend.refobjid = source_table.oid 
        JOIN pg_attribute ON pg_depend.refobjid = pg_attribute.attrelid 
            AND pg_depend.refobjsubid = pg_attribute.attnum 
        JOIN pg_namespace dependent_ns ON dependent_view.relnamespace = dependent_ns.oid 
        JOIN pg_namespace source_ns ON source_table.relnamespace = source_ns.oid 
        WHERE source_table.relname = 'job_applications'
        AND pg_attribute.attname = 'status'
    ) LOOP
        -- 删除依赖
        EXECUTE format('DROP VIEW IF EXISTS %I.%I CASCADE', r.dependent_schema, r.dependent_view);
    END LOOP;
END $$;

-- 删除旧的枚举类型
DROP TYPE IF EXISTS application_status CASCADE;

-- 重命名新的枚举类型
ALTER TYPE application_status_new RENAME TO application_status;

-- 添加注释
COMMENT ON COLUMN job_applications.status IS '申请状态：
    pending: 待处理
    reviewed: 已审核
    interview_scheduled: 已安排面试
    interviewed: 已面试
    offered: 已录用
    rejected: 已拒绝
    withdrawn: 已撤回';

-- 更新现有数据
UPDATE job_applications 
SET status = 'interview_scheduled'::application_status
WHERE status = 'interviewed'::application_status
AND EXISTS (
    SELECT 1 
    FROM interviews i 
    WHERE i.job_id = job_applications.job_id 
    AND i.resume_id = job_applications.resume_id 
    AND i.status = 'scheduled'
);

-- 验证更新
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM pg_enum 
        WHERE enumlabel = 'interview_scheduled' 
        AND enumtypid = 'application_status'::regtype
    ) THEN
        RAISE EXCEPTION '枚举类型更新失败';
    END IF;
END $$; 