-- 修改 resumes 表，允许文件相关字段为 NULL
ALTER TABLE resumes 
    ALTER COLUMN file_name DROP NOT NULL,
    ALTER COLUMN file_path DROP NOT NULL;

-- 添加一个标志字段，用于区分手动创建的简历和上传文件解析的简历
ALTER TABLE resumes
    ADD COLUMN is_manual_entry BOOLEAN DEFAULT FALSE;

-- 为新字段添加索引
CREATE INDEX idx_resumes_is_manual_entry ON resumes(is_manual_entry);

-- 更新注释
COMMENT ON COLUMN resumes.is_manual_entry IS '是否为手动创建的简历（无文件）';
COMMENT ON COLUMN resumes.file_name IS '文件名（可为空，表示手动创建的简历）';
COMMENT ON COLUMN resumes.file_path IS '文件路径（可为空，表示手动创建的简历）'; 