-- 创建面试官与面试的多对多关系表
CREATE TABLE IF NOT EXISTS interview_interviewers (
    interview_id INTEGER REFERENCES interviews(id) ON DELETE CASCADE,
    interviewer_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    feedback TEXT, -- 面试官对此次面试的反馈
    evaluation_score FLOAT, -- 面试官评分
    status VARCHAR(50) DEFAULT 'pending', -- 面试官状态：pending(待评估)、completed(已完成)
    technical_evaluation JSONB, -- 技术评估详情
    comprehensive_evaluation JSONB, -- 综合素质评估
    strengths TEXT, -- 候选人优势
    weaknesses TEXT, -- 候选人劣势
    hiring_recommendation VARCHAR(50), -- 录用建议：强烈推荐、推荐、待定、不推荐
    preparation_notes TEXT, -- 面试准备材料(Markdown格式)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (interview_id, interviewer_id)
);

-- 添加索引
CREATE INDEX IF NOT EXISTS idx_interview_interviewers_interview ON interview_interviewers(interview_id);
CREATE INDEX IF NOT EXISTS idx_interview_interviewers_interviewer ON interview_interviewers(interviewer_id);
CREATE INDEX IF NOT EXISTS idx_interview_interviewers_status ON interview_interviewers(status);

-- 将现有的面试官关系迁移到多对多表中
INSERT INTO interview_interviewers (interview_id, interviewer_id)
SELECT id, interviewer_id 
FROM interviews 
WHERE interviewer_id IS NOT NULL;

-- 添加注释
COMMENT ON TABLE interview_interviewers IS '面试官与面试的多对多关系表';
COMMENT ON COLUMN interview_interviewers.interview_id IS '面试ID';
COMMENT ON COLUMN interview_interviewers.interviewer_id IS '面试官ID';
COMMENT ON COLUMN interview_interviewers.feedback IS '面试官对此次面试的反馈';
COMMENT ON COLUMN interview_interviewers.evaluation_score IS '面试官评分，1-5分';
COMMENT ON COLUMN interview_interviewers.status IS '面试官评估状态：pending(待评估)、completed(已完成)';
COMMENT ON COLUMN interview_interviewers.technical_evaluation IS '技术能力评估详情，JSON格式';
COMMENT ON COLUMN interview_interviewers.comprehensive_evaluation IS '综合素质评估，JSON格式';
COMMENT ON COLUMN interview_interviewers.strengths IS '候选人优势';
COMMENT ON COLUMN interview_interviewers.weaknesses IS '候选人劣势';
COMMENT ON COLUMN interview_interviewers.hiring_recommendation IS '录用建议';
COMMENT ON COLUMN interview_interviewers.preparation_notes IS '面试准备材料，Markdown格式';

-- 添加更新时间触发器
CREATE OR REPLACE FUNCTION update_interview_interviewers_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_interview_interviewers_updated_at
    BEFORE UPDATE ON interview_interviewers
    FOR EACH ROW
    EXECUTE FUNCTION update_interview_interviewers_updated_at();

-- 检查是否成功迁移数据
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
    
    -- 输出迁移结果
    RAISE NOTICE '原始面试记录数: %', original_count;
    RAISE NOTICE '迁移的面试官关联数: %', migration_count;
    
    -- 检查是否所有记录都已迁移
    IF original_count = migration_count THEN
        RAISE NOTICE '数据迁移成功完成';
    ELSE
        RAISE WARNING '数据迁移可能不完整，请检查';
    END IF;
END $$;

-- 在确认数据迁移成功后，执行此语句移除原表中的面试官ID字段
-- ALTER TABLE interviews DROP COLUMN interviewer_id; 