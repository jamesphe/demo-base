-- 添加发布者和审核相关字段到简历表
ALTER TABLE resumes
    -- 发布者信息
    ADD COLUMN publisher_id INTEGER REFERENCES users(id),
    ADD COLUMN publisher_type VARCHAR(20) CHECK (publisher_type IN ('candidate', 'tenant', 'admin')),
    ADD COLUMN publisher_name VARCHAR(100),
    ADD COLUMN publish_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 审核信息
    ADD COLUMN review_status VARCHAR(20) CHECK (review_status IN ('pending', 'approved', 'rejected')) DEFAULT 'pending',
    ADD COLUMN reviewer_id INTEGER REFERENCES users(id),
    ADD COLUMN review_time TIMESTAMP,
    ADD COLUMN review_comment TEXT;

-- 添加外键约束
ALTER TABLE resumes
    ADD CONSTRAINT fk_resumes_publisher FOREIGN KEY (publisher_id) REFERENCES users(id),
    ADD CONSTRAINT fk_resumes_reviewer FOREIGN KEY (reviewer_id) REFERENCES users(id);

-- 创建新的索引
CREATE INDEX idx_resumes_publisher ON resumes(publisher_id);
CREATE INDEX idx_resumes_reviewer ON resumes(reviewer_id);
CREATE INDEX idx_resumes_review_status ON resumes(review_status);

-- 更新现有记录的 publisher_type（如果需要）
UPDATE resumes 
SET publisher_type = 'tenant' 
WHERE publisher_type IS NULL;

-- 设置 publisher_type 为非空
ALTER TABLE resumes 
    ALTER COLUMN publisher_type SET NOT NULL;

-- 回滚脚本
-- DROP INDEX IF EXISTS idx_resumes_publisher;
-- DROP INDEX IF EXISTS idx_resumes_reviewer;
-- DROP INDEX IF EXISTS idx_resumes_review_status;
-- ALTER TABLE resumes
--     DROP COLUMN publisher_id,
--     DROP COLUMN publisher_type,
--     DROP COLUMN publisher_name,
--     DROP COLUMN publish_time,
--     DROP COLUMN review_status,
--     DROP COLUMN reviewer_id,
--     DROP COLUMN review_time,
--     DROP COLUMN review_comment; 