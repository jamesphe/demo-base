-- 为面试官与面试的多对多关系表添加面试过程记录字段
ALTER TABLE interview_interviewers
ADD COLUMN IF NOT EXISTS process_record TEXT;

-- 添加注释
COMMENT ON COLUMN interview_interviewers.process_record IS '面试过程记录，记录面试官在面试中的实时记录'; 