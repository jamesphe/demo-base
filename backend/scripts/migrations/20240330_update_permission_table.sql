-- 更新权限表结构
BEGIN;

-- 1. 备份旧数据
CREATE TABLE permission_backup AS SELECT * FROM permission;

-- 2. 删除旧表的外键约束
ALTER TABLE role_permission DROP CONSTRAINT IF EXISTS role_permission_permission_id_fkey;

-- 3. 删除旧表
DROP TABLE permission;

-- 4. 创建新表
CREATE TABLE permission (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. 创建索引
CREATE INDEX idx_permission_name ON permission(name);

-- 6. 添加更新时间触发器
CREATE TRIGGER update_permission_updated_at
    BEFORE UPDATE ON permission
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 7. 迁移旧数据
INSERT INTO permission (
    id,
    name,
    description
)
SELECT 
    id,
    name,
    description
FROM permission_backup;

-- 8. 重新创建外键约束
ALTER TABLE role_permission 
    ADD CONSTRAINT role_permission_permission_id_fkey 
    FOREIGN KEY (permission_id) REFERENCES permission(id);

-- 9. 添加注释
COMMENT ON TABLE permission IS '权限表';
COMMENT ON COLUMN permission.name IS '权限名称';
COMMENT ON COLUMN permission.description IS '权限描述';
COMMENT ON COLUMN permission.created_at IS '创建时间';
COMMENT ON COLUMN permission.updated_at IS '更新时间';

-- 10. 删除备份表
DROP TABLE permission_backup;

COMMIT;

-- 回滚脚本
/*
BEGIN;

-- 1. 备份数据
CREATE TABLE permission_backup AS SELECT * FROM permission;

-- 2. 删除外键约束
ALTER TABLE role_permission DROP CONSTRAINT IF EXISTS role_permission_permission_id_fkey;

-- 3. 删除新表
DROP TABLE permission;

-- 4. 创建旧表结构
CREATE TABLE permission (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description VARCHAR(255)
);

-- 5. 恢复数据
INSERT INTO permission (
    id,
    name,
    description
)
SELECT 
    id,
    name,
    description
FROM permission_backup;

-- 6. 重新创建外键约束
ALTER TABLE role_permission 
    ADD CONSTRAINT role_permission_permission_id_fkey 
    FOREIGN KEY (permission_id) REFERENCES permission(id);

-- 7. 删除备份表
DROP TABLE permission_backup;

COMMIT;
*/ 