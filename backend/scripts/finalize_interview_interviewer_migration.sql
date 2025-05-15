-- 在确认数据迁移成功后执行此脚本

-- 首先检查数据是否已经完全迁移
DO $$
DECLARE
    migration_count INTEGER;
    original_count INTEGER;
BEGIN
    -- 获取原有的非空面试官数量
    SELECT COUNT(*) INTO original_count 
    FROM interviews
    WHERE interviewer_id IS NOT NULL;
    
    -- 获取迁移后的记录数量
    SELECT COUNT(*) INTO migration_count
    FROM interview_interviewers;
    
    -- 检查是否所有记录都已迁移
    IF original_count != migration_count THEN
        RAISE EXCEPTION '数据迁移不完整，请先确保所有数据已迁移到interview_interviewers表';
    END IF;
END $$;

-- 移除interviews表中的interviewer_id列
ALTER TABLE interviews DROP COLUMN interviewer_id;

-- 移除相关索引
DROP INDEX IF EXISTS idx_interviews_interviewer;

-- 移除相关注释
COMMENT ON COLUMN interviews.interviewer_id IS NULL;

-- 输出成功消息
DO $$
BEGIN
    RAISE NOTICE '面试官ID列已成功移除，多对多关系迁移完成';
END $$; 