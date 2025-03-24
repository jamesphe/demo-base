-- 数据库升级脚本：添加简历与职位匹配度功能
-- 版本：1.0.0
-- 日期：2023-11-15
-- 描述：为job_applications表添加匹配度和匹配理由字段

-- 开始事务
BEGIN;

-- 检查字段是否已存在，如果不存在则添加
DO $$
BEGIN
    -- 检查match_score字段
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'job_applications' 
        AND column_name = 'match_score'
    ) THEN
        -- 添加match_score字段
        ALTER TABLE job_applications 
        ADD COLUMN match_score FLOAT DEFAULT 0.0;
        
        RAISE NOTICE '已添加match_score字段到job_applications表';
    ELSE
        RAISE NOTICE 'match_score字段已存在，跳过添加';
    END IF;

    -- 检查match_reason字段
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'job_applications' 
        AND column_name = 'match_reason'
    ) THEN
        -- 添加match_reason字段
        ALTER TABLE job_applications 
        ADD COLUMN match_reason TEXT;
        
        RAISE NOTICE '已添加match_reason字段到job_applications表';
    ELSE
        RAISE NOTICE 'match_reason字段已存在，跳过添加';
    END IF;
END
$$;

-- 检查索引是否已存在，如果不存在则创建
DO $$
BEGIN
    -- 检查match_score索引
    IF NOT EXISTS (
        SELECT 1 
        FROM pg_indexes 
        WHERE tablename = 'job_applications' 
        AND indexname = 'idx_job_applications_match_score'
    ) THEN
        -- 创建match_score索引
        CREATE INDEX idx_job_applications_match_score 
        ON job_applications(match_score);
        
        RAISE NOTICE '已创建idx_job_applications_match_score索引';
    ELSE
        RAISE NOTICE 'idx_job_applications_match_score索引已存在，跳过创建';
    END IF;
END
$$;

-- 添加字段注释
COMMENT ON COLUMN job_applications.match_score IS '简历与职位的匹配度评分(0-100)';
COMMENT ON COLUMN job_applications.match_reason IS '匹配度分析理由说明';

-- 提交事务
COMMIT;

-- 输出升级完成信息
DO $$
BEGIN
    RAISE NOTICE '数据库升级完成：已添加简历与职位匹配度功能';
END
$$; 