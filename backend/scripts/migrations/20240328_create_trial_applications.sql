-- 创建试用申请表
BEGIN;

-- 创建试用申请表
CREATE TABLE trial_applications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    company_name VARCHAR(255) NOT NULL,
    contact_name VARCHAR(100) NOT NULL,
    contact_phone VARCHAR(20) NOT NULL,
    contact_email VARCHAR(255) NOT NULL,
    status VARCHAR(20) CHECK (
        status IN (
            'pending',
            'active', 
            'rejected',
            'expired'
        )
    ) DEFAULT 'pending',
    reject_reason TEXT,
    trial_start_date TIMESTAMP,
    trial_end_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 添加触发器
CREATE TRIGGER update_trial_applications_updated_at
    BEFORE UPDATE ON trial_applications
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 添加索引
CREATE INDEX idx_trial_applications_user ON trial_applications(user_id);
CREATE INDEX idx_trial_applications_status ON trial_applications(status);
CREATE INDEX idx_trial_applications_dates ON trial_applications(trial_start_date, trial_end_date);

-- 添加注释
COMMENT ON TABLE trial_applications IS '试用申请表';
COMMENT ON COLUMN trial_applications.user_id IS '申请用户ID';
COMMENT ON COLUMN trial_applications.company_name IS '公司名称';
COMMENT ON COLUMN trial_applications.contact_name IS '联系人姓名';
COMMENT ON COLUMN trial_applications.contact_phone IS '联系电话';
COMMENT ON COLUMN trial_applications.contact_email IS '联系邮箱';
COMMENT ON COLUMN trial_applications.status IS '申请状态(pending:待审核,active:试用中,rejected:已拒绝,expired:已过期)';
COMMENT ON COLUMN trial_applications.reject_reason IS '拒绝原因';
COMMENT ON COLUMN trial_applications.trial_start_date IS '试用开始时间';
COMMENT ON COLUMN trial_applications.trial_end_date IS '试用结束时间';

COMMIT;

-- 回滚脚本
/*
BEGIN;

DROP TABLE IF EXISTS trial_applications;

COMMIT;
*/ 