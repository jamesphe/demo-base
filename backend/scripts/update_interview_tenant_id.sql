-- 更新interviews表，添加租户ID字段
-- 创建日期: 2023-10-26

-- 添加 tenant_id 字段（租户ID）
ALTER TABLE interviews ADD COLUMN tenant_id INTEGER;

-- 使用默认值更新现有记录的tenant_id
-- 此SQL假设所有面试都属于tenant_id=1的租户
-- 请根据实际情况修改此值
UPDATE interviews SET tenant_id = 1 WHERE tenant_id IS NULL;

-- 如果您希望根据resume的tenant_id来设置interview的tenant_id，请使用以下SQL：
-- UPDATE interviews i
-- SET tenant_id = r.tenant_id
-- FROM resumes r
-- WHERE i.resume_id = r.id AND i.tenant_id IS NULL;

-- 添加外键约束
ALTER TABLE interviews 
ADD CONSTRAINT fk_interview_tenant 
FOREIGN KEY (tenant_id) 
REFERENCES tenant (id);

-- 完成数据迁移后，您可以设置tenant_id为非空
-- ALTER TABLE interviews ALTER COLUMN tenant_id SET NOT NULL;

COMMIT; 