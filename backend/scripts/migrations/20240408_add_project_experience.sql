-- 升级脚本：添加项目经历字段
-- 版本：V1.0.1
-- 描述：向resumes表添加project_experience字段，用于存储项目经历信息

-- 检查字段是否已存在
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'resumes'
        AND column_name = 'project_experience'
    ) THEN
        -- 添加project_experience字段
        ALTER TABLE resumes
        ADD COLUMN project_experience JSON;

        -- 添加注释
        COMMENT ON COLUMN resumes.project_experience IS '项目经历，包含项目名称、角色、时间等信息';
    END IF;
END $$;

-- 更新已有数据的project_experience字段为空数组
UPDATE resumes
SET project_experience = '[]'::json
WHERE project_experience IS NULL;
