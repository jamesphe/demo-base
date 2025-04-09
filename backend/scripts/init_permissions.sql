-- 添加职位相关权限
INSERT INTO permission (name, description) VALUES 
('job_read', '查看职位'),
('job_create', '创建职位'),
('job_update', '更新职位'),
('job_delete', '删除职位')
ON CONFLICT (name) DO NOTHING;

-- 添加候选人相关权限
INSERT INTO permission (name, description) VALUES 
('candidate_read', '查看候选人'),
('candidate_create', '创建候选人'),
('candidate_update', '更新候选人'),
('candidate_delete', '删除候选人')
ON CONFLICT (name) DO NOTHING;

-- 添加租户相关权限
INSERT INTO permission (name, description) VALUES 
('tenant_read', '查看租户'),
('tenant_create', '创建租户'),
('tenant_update', '更新租户'),
('tenant_delete', '删除租户')
ON CONFLICT (name) DO NOTHING;

-- 添加用户相关权限
INSERT INTO permission (name, description) VALUES 
('user_read', '查看用户'),
('user_create', '创建用户'),
('user_update', '更新用户'),
('user_delete', '删除用户')
ON CONFLICT (name) DO NOTHING;

-- 添加角色相关权限
INSERT INTO permission (name, description) VALUES 
('role_read', '查看角色'),
('role_create', '创建角色'),
('role_update', '更新角色'),
('role_delete', '删除角色')
ON CONFLICT (name) DO NOTHING;

-- 添加面试相关权限
INSERT INTO permission (name, description) VALUES 
('interview_read', '查看面试'),
('interview_create', '创建面试'),
('interview_update', '更新面试'),
('interview_delete', '删除面试')
ON CONFLICT (name) DO NOTHING;

-- 添加职位申请相关权限
INSERT INTO permission (name, description) VALUES 
('job_application_read', '查看职位申请'),
('job_application_create', '创建职位申请'),
('job_application_update', '更新职位申请'),
('job_application_delete', '删除职位申请')
ON CONFLICT (name) DO NOTHING;

-- 添加简历相关权限
INSERT INTO permission (name, description) VALUES 
('resume_read', '查看简历'),
('resume_create', '创建简历'),
('resume_update', '更新简历'),
('resume_delete', '删除简历'),
('resume_parse', '解析简历')
ON CONFLICT (name) DO NOTHING;

-- 添加简历评审相关权限
INSERT INTO permission (name, description) VALUES 
('resume_review_read', '查看简历评审'),
('resume_review_update', '更新简历评审')
ON CONFLICT (name) DO NOTHING;

-- 添加仓库相关权限
INSERT INTO permission (name, description) VALUES 
('repository_read', '查看仓库'),
('repository_create', '创建仓库'),
('repository_delete', '删除仓库')
ON CONFLICT (name) DO NOTHING;

-- 添加LLM配置相关权限
INSERT INTO permission (name, description) VALUES 
('llm_config_read', '查看LLM配置'),
('llm_config_create', '创建LLM配置'),
('llm_config_update', '更新LLM配置'),
('llm_config_delete', '删除LLM配置'),
('llm_config_validate', '验证LLM配置')
ON CONFLICT (name) DO NOTHING;

-- 创建基础角色
INSERT INTO role (name, description) VALUES 
('admin', '管理员'),
('hr', '人力资源'),
('interviewer', '面试官'),
('tenant_admin', '租户管理员'),
('tenant_user', '租户用户')
ON CONFLICT (name) DO NOTHING;

-- 为管理员角色分配所有权限
INSERT INTO role_permission (role_id, permission_id)
SELECT r.id, p.id 
FROM role r, permission p 
WHERE r.name = 'admin' 
AND NOT EXISTS (
    SELECT 1 FROM role_permission rp 
    WHERE rp.role_id = r.id AND rp.permission_id = p.id
);

-- 为HR角色分配权限
INSERT INTO role_permission (role_id, permission_id)
SELECT r.id, p.id 
FROM role r, permission p 
WHERE r.name = 'hr' 
AND p.name IN (
    'candidate_read',
    'candidate_create',
    'candidate_update',
    'job_read',
    'job_create',
    'job_application_read',
    'job_application_update',
    'resume_read',
    'resume_review_read',
    'resume_review_update'
)
AND NOT EXISTS (
    SELECT 1 FROM role_permission rp 
    WHERE rp.role_id = r.id AND rp.permission_id = p.id
);

-- 为面试官角色分配权限
INSERT INTO role_permission (role_id, permission_id)
SELECT r.id, p.id 
FROM role r, permission p 
WHERE r.name = 'interviewer' 
AND p.name IN (
    'candidate_read',
    'interview_read',
    'interview_create',
    'interview_update',
    'resume_read',
    'job_application_read'
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
    'candidate_read',
    'candidate_create',
    'candidate_update',
    'candidate_delete',
    'job_read',
    'job_create',
    'job_update',
    'job_delete',
    'interview_read',
    'interview_create',
    'interview_update',
    'interview_delete',
    'user_read',
    'user_create',
    'user_update',
    'user_delete',
    'role_read',
    'role_create',
    'role_update',
    'role_delete',
    'tenant_read',
    'tenant_create',
    'tenant_update',
    'tenant_delete',
    'job_application_read',
    'job_application_create',
    'job_application_update',
    'job_application_delete',
    'resume_read',
    'resume_create',
    'resume_update',
    'resume_delete',
    'resume_parse',
    'resume_review_read',
    'resume_review_update',
    'repository_read',
    'repository_create',
    'repository_delete',
    'llm_config_read',
    'llm_config_create',
    'llm_config_update',
    'llm_config_delete',
    'llm_config_validate'
)
AND NOT EXISTS (
    SELECT 1 FROM role_permission rp 
    WHERE rp.role_id = r.id AND rp.permission_id = p.id
);

-- 为租户用户角色分配权限
INSERT INTO role_permission (role_id, permission_id)
SELECT r.id, p.id 
FROM role r, permission p 
WHERE r.name = 'tenant_user' 
AND p.name IN (
    'candidate_read',
    'job_read',
    'interview_read',
    'user_read',
    'role_read',
    'tenant_read',
    'job_application_read',
    'resume_read',
    'resume_review_read',
    'repository_read',
    'llm_config_read'
)
AND NOT EXISTS (
    SELECT 1 FROM role_permission rp 
    WHERE rp.role_id = r.id AND rp.permission_id = p.id
); 