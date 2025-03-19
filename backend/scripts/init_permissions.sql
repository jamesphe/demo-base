-- 添加职位相关权限
INSERT INTO permission (name, description) VALUES 
('job_read', '查看职位'),
('job_create', '创建职位'),
('job_update', '更新职位'),
('job_delete', '删除职位')
ON CONFLICT (name) DO NOTHING;

-- 创建租户基础角色
INSERT INTO role (name, description) VALUES 
('tenant_user', '租户普通用户'),
('tenant_admin', '租户管理员')
ON CONFLICT (name) DO NOTHING;

-- 为租户普通用户角色添加基本职位权限
INSERT INTO role_permission (role_id, permission_id)
SELECT r.id, p.id 
FROM role r, permission p 
WHERE r.name = 'tenant_user' 
AND p.name IN ('job_read', 'job_create', 'job_update')
AND NOT EXISTS (
    SELECT 1 FROM role_permission rp 
    WHERE rp.role_id = r.id AND rp.permission_id = p.id
);

-- 为租户管理员角色添加所有职位权限
INSERT INTO role_permission (role_id, permission_id)
SELECT r.id, p.id 
FROM role r, permission p 
WHERE r.name = 'tenant_admin' 
AND p.name IN ('job_read', 'job_create', 'job_update', 'job_delete')
AND NOT EXISTS (
    SELECT 1 FROM role_permission rp 
    WHERE rp.role_id = r.id AND rp.permission_id = p.id
);

-- 为所有租户用户分配基础角色
INSERT INTO user_role (user_id, role_id)
SELECT u.id, r.id
FROM users u, role r
WHERE u.user_type = 'tenant'
AND r.name = 'tenant_user'
AND NOT EXISTS (
    SELECT 1 FROM user_role ur 
    WHERE ur.user_id = u.id AND ur.role_id = r.id
); 