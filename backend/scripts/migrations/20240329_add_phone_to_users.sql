-- 为users表添加phone字段
BEGIN;

-- 添加phone字段
ALTER TABLE users 
    ADD COLUMN IF NOT EXISTS phone VARCHAR(20);

-- 创建phone字段的索引
CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone);

-- 添加注释
COMMENT ON COLUMN users.phone IS '用户手机号';

COMMIT;

-- 回滚脚本
/*
BEGIN;

DROP INDEX IF EXISTS idx_users_phone;
ALTER TABLE users DROP COLUMN IF EXISTS phone;

COMMIT;
*/ 