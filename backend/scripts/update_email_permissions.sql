-- 向租户管理员角色添加邮箱同步相关权限
INSERT INTO role_permission (role_id, permission_id)
SELECT r.id, p.id 
FROM role r, permission p 
WHERE r.name = 'tenant_admin' 
AND p.name IN (
    'resume_sync_email_read',
    'resume_sync_email_create',
    'resume_sync_email_update',
    'resume_sync_email_delete'
)
AND NOT EXISTS (
    SELECT 1 FROM role_permission rp 
    WHERE rp.role_id = r.id AND rp.permission_id = p.id
);

-- 向管理员角色添加邮箱同步相关权限
INSERT INTO role_permission (role_id, permission_id)
SELECT r.id, p.id 
FROM role r, permission p 
WHERE r.name = 'admin' 
AND p.name IN (
    'resume_sync_email_read',
    'resume_sync_email_create',
    'resume_sync_email_update',
    'resume_sync_email_delete'
)
AND NOT EXISTS (
    SELECT 1 FROM role_permission rp 
    WHERE rp.role_id = r.id AND rp.permission_id = p.id
); 