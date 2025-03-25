-- 更新试用申请表的 user_id 字段为可空
BEGIN;

-- 1. 先删除原有的外键约束
ALTER TABLE trial_applications 
DROP CONSTRAINT IF EXISTS trial_applications_user_id_fkey;

-- 2. 修改 user_id 字段为可空
ALTER TABLE trial_applications 
ALTER COLUMN user_id DROP NOT NULL;

-- 3. 重新添加外键约束
ALTER TABLE trial_applications 
ADD CONSTRAINT trial_applications_user_id_fkey 
FOREIGN KEY (user_id) REFERENCES users(id);

-- 4. 更新字段注释
COMMENT ON COLUMN trial_applications.user_id IS '申请用户ID（可选）';

COMMIT; 