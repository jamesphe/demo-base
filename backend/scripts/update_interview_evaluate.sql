
-- 如果evaluated_at字段在数据库中不存在，添加该字段
ALTER TABLE interviews ADD COLUMN evaluated_at TIMESTAMP WITHOUT TIME ZONE;

-- 修改evaluation_score字段类型为DOUBLE PRECISION（如果原来是INTEGER）
ALTER TABLE interviews ALTER COLUMN evaluation_score TYPE DOUBLE PRECISION;

-- 修改notes字段类型为TEXT（如果原来是VARCHAR）
ALTER TABLE interviews ALTER COLUMN notes TYPE TEXT; 

ALTER TABLE interviews ADD COLUMN created_by VARCHAR(255);
ALTER TABLE interviews ADD COLUMN updated_by VARCHAR(255);


