-- 1. 删除表并重新创建
DROP TABLE IF EXISTS interviews CASCADE;

CREATE TABLE interviews (
    id SERIAL PRIMARY KEY,
    resume_id INTEGER REFERENCES resumes(id),
    job_id INTEGER REFERENCES jobs(id),
    interviewer_id INTEGER REFERENCES users(id),
    status VARCHAR(50) DEFAULT 'scheduled',
    schedule_time TIMESTAMP,
    feedback VARCHAR(1000),
    duration INTEGER DEFAULT 60,
    interview_type VARCHAR(50) DEFAULT 'onsite',
    location VARCHAR(255),
    notes TEXT,
    status_updated_at TIMESTAMP,
    completed_at TIMESTAMP,
    evaluation_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 创建索引
CREATE INDEX idx_interviews_resume ON interviews(resume_id);
CREATE INDEX idx_interviews_job ON interviews(job_id);
CREATE INDEX idx_interviews_interviewer ON interviews(interviewer_id);
CREATE INDEX idx_interviews_status ON interviews(status);
CREATE INDEX idx_interviews_schedule_time ON interviews(schedule_time);

-- 3. 添加更新时间触发器
CREATE TRIGGER update_interviews_updated_at
    BEFORE UPDATE ON interviews
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 4. 添加注释
COMMENT ON TABLE interviews IS '面试表';
COMMENT ON COLUMN interviews.resume_id IS '关联的简历ID';
COMMENT ON COLUMN interviews.job_id IS '关联的职位ID';
COMMENT ON COLUMN interviews.interviewer_id IS '面试官ID';
COMMENT ON COLUMN interviews.status IS '面试状态：scheduled(已安排)、in_progress(进行中)、completed(已完成)、cancelled(已取消)';
COMMENT ON COLUMN interviews.schedule_time IS '面试时间';
COMMENT ON COLUMN interviews.feedback IS '面试反馈';
COMMENT ON COLUMN interviews.duration IS '面试时长（分钟）';
COMMENT ON COLUMN interviews.interview_type IS '面试类型：onsite(现场)、online(在线)、phone(电话)';
COMMENT ON COLUMN interviews.location IS '面试地点';
COMMENT ON COLUMN interviews.notes IS '面试备注';
COMMENT ON COLUMN interviews.status_updated_at IS '状态更新时间';
COMMENT ON COLUMN interviews.completed_at IS '完成时间';
COMMENT ON COLUMN interviews.evaluation_score IS '评分';

-- 5. 添加数据完整性检查
DO $$
BEGIN
    -- 检查是否有面试记录没有对应的简历
    IF EXISTS (
        SELECT 1 FROM interviews 
        WHERE resume_id IS NULL
    ) THEN
        RAISE WARNING '存在没有关联简历的面试记录';
    END IF;

    -- 检查是否有面试记录没有对应的职位
    IF EXISTS (
        SELECT 1 FROM interviews 
        WHERE job_id IS NULL
    ) THEN
        RAISE WARNING '存在没有关联职位的面试记录';
    END IF;

    -- 检查是否有面试记录没有对应的面试官
    IF EXISTS (
        SELECT 1 FROM interviews 
        WHERE interviewer_id IS NULL
    ) THEN
        RAISE WARNING '存在没有关联面试官的面试记录';
    END IF;
END $$; 