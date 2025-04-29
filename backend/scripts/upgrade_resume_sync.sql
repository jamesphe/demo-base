-- 创建简历同步邮箱表
CREATE TABLE IF NOT EXISTS resume_sync_emails (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL REFERENCES tenant(id),
    email VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    imap_server VARCHAR(255) NOT NULL,
    imap_port INTEGER DEFAULT 993,
    smtp_server VARCHAR(255) NOT NULL,
    smtp_port INTEGER DEFAULT 465,
    is_active BOOLEAN DEFAULT TRUE,
    last_sync_time TIMESTAMP,
    sync_interval INTEGER DEFAULT 15,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT,
    CONSTRAINT unique_email_per_tenant UNIQUE (email, tenant_id)
);

-- 创建职位关键字表
CREATE TABLE IF NOT EXISTS job_keywords (
    id SERIAL PRIMARY KEY,
    job_id INTEGER NOT NULL REFERENCES jobs(id),
    sync_email_id INTEGER NOT NULL REFERENCES resume_sync_emails(id),
    keyword VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT,
    CONSTRAINT unique_keyword_per_job UNIQUE (job_id, keyword)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_resume_sync_emails_tenant_id ON resume_sync_emails(tenant_id);
CREATE INDEX IF NOT EXISTS idx_resume_sync_emails_is_active ON resume_sync_emails(is_active);
CREATE INDEX IF NOT EXISTS idx_job_keywords_job_id ON job_keywords(job_id);
CREATE INDEX IF NOT EXISTS idx_job_keywords_sync_email_id ON job_keywords(sync_email_id);

-- 添加权限
INSERT INTO permission (name, description)
VALUES 
    ('resume_sync_email_create', '创建简历同步邮箱配置'),
    ('resume_sync_email_read', '读取简历同步邮箱配置'),
    ('resume_sync_email_update', '更新简历同步邮箱配置'),
    ('resume_sync_email_delete', '删除简历同步邮箱配置')
ON CONFLICT (name) DO NOTHING;

-- 为role_permission表添加唯一约束
ALTER TABLE role_permission ADD CONSTRAINT unique_role_permission UNIQUE (role_id, permission_id);

-- 为管理员角色添加权限
INSERT INTO role_permission (role_id, permission_id)
SELECT r.id, p.id
FROM role r
CROSS JOIN permission p
WHERE r.name = 'admin'
AND p.name IN (
    'resume_sync_email_create',
    'resume_sync_email_read',
    'resume_sync_email_update',
    'resume_sync_email_delete'
)
ON CONFLICT (role_id, permission_id) DO NOTHING;