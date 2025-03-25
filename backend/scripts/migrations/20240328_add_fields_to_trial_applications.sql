-- 添加新字段到试用申请表
ALTER TABLE trial_applications
    ADD COLUMN company_size VARCHAR(50),
    ADD COLUMN business_description TEXT,
    ADD COLUMN application_reason TEXT;

-- 添加注释
COMMENT ON COLUMN trial_applications.company_size IS '公司规模';
COMMENT ON COLUMN trial_applications.business_description IS '业务描述';
COMMENT ON COLUMN trial_applications.application_reason IS '申请原因'; 