-- 添加职位相关权限
INSERT INTO permission (name, description) VALUES 
('job_read', '查看职位'),
('job_create', '创建职位'),
('job_update', '更新职位'),
('job_delete', '删除职位')
ON CONFLICT (name) DO NOTHING;

-- 添加简历相关权限
INSERT INTO permission (name, description) VALUES 
('resume_create', '创建简历'),
('resume_read', '查看简历'),
('resume_update', '编辑简历'),
('resume_delete', '删除简历'),
('resume_review', '审核简历'),
('resume_export', '导出简历'),
('resume_batch_import', '批量导入简历')
ON CONFLICT (name) DO NOTHING;

-- 创建基础角色
INSERT INTO role (name, description) VALUES 
('tenant_user', '租户普通用户'),
('tenant_admin', '租户管理员'),
('tenant_hr', '租户HR'),
('candidate', '求职者'),
('platform_admin', '平台管理员')
ON CONFLICT (name) DO NOTHING;

-- 为求职者角色分配权限
INSERT INTO role_permission (role_id, permission_id)
SELECT r.id, p.id 
FROM role r, permission p 
WHERE r.name = 'candidate' 
AND p.name IN ('resume_create', 'resume_read', 'resume_update', 'resume_export')
AND NOT EXISTS (
    SELECT 1 FROM role_permission rp 
    WHERE rp.role_id = r.id AND rp.permission_id = p.id
);

-- 为租户普通用户角色分配权限
INSERT INTO role_permission (role_id, permission_id)
SELECT r.id, p.id 
FROM role r, permission p 
WHERE r.name = 'tenant_user' 
AND p.name IN ('job_read', 'job_create', 'job_update', 'resume_read', 'resume_create')
AND NOT EXISTS (
    SELECT 1 FROM role_permission rp 
    WHERE rp.role_id = r.id AND rp.permission_id = p.id
);

-- 为租户HR角色分配权限
INSERT INTO role_permission (role_id, permission_id)
SELECT r.id, p.id 
FROM role r, permission p 
WHERE r.name = 'tenant_hr' 
AND p.name IN (
    'resume_create', 'resume_read', 'resume_update', 
    'resume_review', 'resume_export', 'resume_batch_import',
    'job_read', 'job_create', 'job_update'
)
AND NOT EXISTS (
    SELECT 1 FROM role_permission rp 
    WHERE rp.role_id = r.id AND rp.permission_id = p.id
);

-- 为租户管理员角色分配权限
INSERT INTO role_permission (role_id, permission_id)
SELECT r.id, p.id 
FROM role r, permission p 
WHERE r.name = 'tenant_admin' 
AND p.name IN (
    'job_read', 'job_create', 'job_update', 'job_delete',
    'resume_create', 'resume_read', 'resume_update', 
    'resume_review', 'resume_export', 'resume_batch_import'
)
AND NOT EXISTS (
    SELECT 1 FROM role_permission rp 
    WHERE rp.role_id = r.id AND rp.permission_id = p.id
);

-- 为平台管理员角色分配所有权限
INSERT INTO role_permission (role_id, permission_id)
SELECT r.id, p.id 
FROM role r, permission p 
WHERE r.name = 'platform_admin' 
AND NOT EXISTS (
    SELECT 1 FROM role_permission rp 
    WHERE rp.role_id = r.id AND rp.permission_id = p.id
);

-- 为用户分配基础角色
INSERT INTO user_role (user_id, role_id)
SELECT u.id, r.id
FROM users u, role r
WHERE 
    (u.user_type = 'tenant' AND r.name = 'tenant_user')
    OR (u.user_type = 'candidate' AND r.name = 'candidate')
AND NOT EXISTS (
    SELECT 1 FROM user_role ur 
    WHERE ur.user_id = u.id AND ur.role_id = r.id
); 