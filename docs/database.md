蓝领用工平台数据库设计文档

1. 项目概述

本平台旨在构建一个蓝领用工平台，通过统一管理人才数据，实现候选人筛选、简历管理、技能匹配以及灵活的自定义人才库组织。平台采用 SaaS 多租户模式，不同用人单位作为租户隔离数据，同时提供公共人才库作为全局共享资源。候选人数据与辅助信息均统一存储，结合基于角色的权限控制（RBAC）确保数据安全与访问控制。

2. 设计目标
	•	统一数据管理：公共人才与租户私域人才统一存储在同一张人才表（Talent），通过 tenant_id 字段区分数据归属。
	•	候选人筛选与管理：租户可在公共人才库中筛选候选人，同时可录入私域人才。候选人记录在 Candidate 表中保存，用于后续面试安排与流程跟踪。
	•	辅助信息与简历管理：认证、教育、工作经历、技能、简历等辅助信息均以 talent_id 为外键统一关联，保证数据结构简洁、查询高效。
	•	自定义人才库功能：租户可以创建自定义人才库（Talent Pool），按不同招聘需求组织候选人，实现如"2025春季招聘库"、"2025年高级钳工库"等功能。
	•	多租户隔离与权限控制：通过 Tenant 表及用户、角色、权限管理模块，实现不同租户数据严格隔离，同时公共人才库资源对各租户开放。
	•	RBAC 权限管理：利用用户、角色、权限及关联表，确保不同用户仅能访问与其权限相符的数据与功能。

3. 数据库总体架构

本设计采用关系型数据库，整体架构主要包括以下模块：
	•	租户管理模块：记录各租户（用人单位）的基本信息。
	•	人才管理模块：统一管理所有人才数据，包含公共人才与租户私域人才；所有辅助信息（认证、教育、工作经历、技能、简历）均与之关联。
	•	候选人管理模块：记录租户筛选出的候选人，明确候选人与租户的归属关系。
	•	自定义人才库模块：支持租户建立并管理自定义人才库及其成员。
	•	用户及权限管理模块：实现平台用户的账户管理、角色分配、权限控制以及多租户数据隔离。
	•	批量导入日志模块：记录批量数据导入操作，便于数据质量追踪和问题排查。
	•	专用工种扩展模块：支持记录特定工种（例如焊工）的专有信息，并提供视图以方便查询。

下图（示意图）展示了各模块之间的主要数据关联关系（图中每个模块的具体字段请参见后续章节）。

          +------------------+
          |     Tenant       |
          +------------------+
                   │
                   │  (租户ID)
                   ▼
          +------------------+         +-------------------+
          |     Talent       |◄─────┐  |   Candidate       |
          +------------------+      │  +-------------------+
                   │               │          │
                   │               │          │
                   │               │          │
       +-----------+-----------+   │          │
       |  辅助信息模块（认证、   |   │          │
       |  教育、工作经历、技能、 |   │          │
       |      简历等）          |   │          │
       +-----------------------+   │          │
                                   │          │
          +------------------+     │          │
          |  自定义人才库  |     │          │
          |  (Talent Pool) |◄────┼──────────┘
          +------------------+     │
                                   │
          +------------------+     │
          | Talent Pool    |     │
          | Member         |─────┘
          +------------------+

4. 数据表设计

4.1 租户管理

用于存储各租户的基本信息，实现多租户数据隔离与管理。

CREATE TABLE tenant (
    tenant_id INT PRIMARY KEY AUTO_INCREMENT,         -- 租户唯一标识
    tenant_name VARCHAR(100) NOT NULL,                 -- 租户名称（用人单位名称）
    contact_person VARCHAR(100),                       -- 联系人
    phone VARCHAR(20),                                 -- 联系电话
    email VARCHAR(100),                                -- 邮箱
    address VARCHAR(255),                              -- 地址
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,     -- 创建时间
    status ENUM('active', 'inactive') DEFAULT 'active'  -- 租户状态
);

4.2 人才库（Talent）

统一存储所有人才信息。
	•	若 tenant_id 为 NULL，则表示公共人才库（例如个人用户注册的数据）；
	•	若 tenant_id 非空，则表示租户私域数据，由租户自行维护。

CREATE TABLE talent (
    talent_id INT PRIMARY KEY AUTO_INCREMENT,         -- 人才唯一标识
    tenant_id INT DEFAULT NULL,                         -- 租户ID；NULL 表示公共人才，非 NULL 表示租户私域数据
    name VARCHAR(100) NOT NULL,                         -- 姓名
    gender ENUM('M', 'F') DEFAULT 'M',                  -- 性别
    birth_date DATE,                                    -- 出生日期（可选）
    phone VARCHAR(20) NOT NULL,                         -- 联系电话
    email VARCHAR(100),                                 -- 邮箱
    address VARCHAR(255),                               -- 居住/工作地址
    id_number VARCHAR(50),                              -- 身份证号码
    registration_date DATETIME DEFAULT CURRENT_TIMESTAMP,  -- 注册/录入时间
    verified_status TINYINT(1) DEFAULT 0,               -- 认证状态（0 未认证，1 已认证）
    profile_picture VARCHAR(255),                       -- 头像 URL（可选）
    profile_summary TEXT,                               -- 个人简介/简历描述（可选）
    primary_job_type VARCHAR(50),                       -- 主要工种，如 "welding"、"electrician" 等
    job_location_preference VARCHAR(100),               -- 期望工作地点（可选）
    expected_salary VARCHAR(50),                        -- 期望薪资（可选）
    data_source ENUM('个人用户', '技术学校', '人力公司', '租户自建') DEFAULT '个人用户',
    FOREIGN KEY (tenant_id) REFERENCES tenant(tenant_id)
);

4.3 候选人（Candidate）

用于记录租户筛选出的候选人，明确候选人与租户的归属关系。

CREATE TABLE candidate (
    candidate_id INT PRIMARY KEY AUTO_INCREMENT,      -- 候选人记录唯一标识
    tenant_id INT NOT NULL,                             -- 归属租户（用人单位），外键关联 tenant 表
    talent_id INT NOT NULL,                             -- 引用统一人才表中的记录
    selection_date DATETIME DEFAULT CURRENT_TIMESTAMP,  -- 筛选时间
    match_info TEXT,                                    -- 筛选备注或匹配理由
    FOREIGN KEY (tenant_id) REFERENCES tenant(tenant_id),
    FOREIGN KEY (talent_id) REFERENCES talent(talent_id)
);

4.4 辅助信息模块

所有辅助信息均与统一人才表关联，结构统一，便于扩展和查询。

4.4.1 认证证书表

CREATE TABLE candidate_certification (
    certification_id INT PRIMARY KEY AUTO_INCREMENT,  -- 认证记录ID
    talent_id INT NOT NULL,                             -- 关联人才表
    certification_name VARCHAR(100) NOT NULL,           -- 证书名称
    issuing_organization VARCHAR(100),                  -- 颁发机构
    issue_date DATE,                                    -- 颁发日期
    expiration_date DATE,                               -- 有效期至
    document_url VARCHAR(255),                          -- 证书文件链接
    FOREIGN KEY (talent_id) REFERENCES talent(talent_id)
);

4.4.2 教育经历表

CREATE TABLE candidate_education (
    education_id INT PRIMARY KEY AUTO_INCREMENT,        -- 教育记录ID
    talent_id INT NOT NULL,                             -- 关联人才表
    institution_name VARCHAR(255) NOT NULL,             -- 教育/培训机构名称
    degree VARCHAR(100),                                -- 学历或证书名称
    field_of_study VARCHAR(100),                        -- 专业或培训方向
    start_date DATE,                                    -- 入学/培训开始日期
    graduation_date DATE,                               -- 毕业/培训结束日期
    certificate_url VARCHAR(255),                       -- 证书链接（可选）
    description TEXT,                                   -- 备注说明
    FOREIGN KEY (talent_id) REFERENCES talent(talent_id)
);

4.4.3 工作经历表

CREATE TABLE candidate_experience (
    experience_id INT PRIMARY KEY AUTO_INCREMENT,       -- 工作经历记录ID
    talent_id INT NOT NULL,                             -- 关联人才表
    company_name VARCHAR(255) NOT NULL,                 -- 工作单位名称
    position VARCHAR(100) NOT NULL,                     -- 职位/岗位名称
    start_date DATE NOT NULL,                           -- 工作开始日期
    end_date DATE,                                      -- 工作结束日期（在职时可为空）
    job_description TEXT,                               -- 工作职责与描述
    achievements TEXT,                                  -- 工作期间成就或亮点（可选）
    attachment_url VARCHAR(255),                        -- 附件链接（如推荐信）
    FOREIGN KEY (talent_id) REFERENCES talent(talent_id)
);

4.4.4 人才技能关联表

技能词库表：

CREATE TABLE skill (
    skill_id INT PRIMARY KEY AUTO_INCREMENT,          -- 技能ID
    tenant_id INT DEFAULT NULL,                         -- 租户ID，NULL表示平台公共技能
    skill_name VARCHAR(100) NOT NULL,                   -- 技能名称
    skill_description TEXT,                             -- 技能描述
    category VARCHAR(50),                               -- 技能类别或所属工种
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,      -- 创建时间
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,  -- 更新时间
    status ENUM('active', 'inactive') DEFAULT 'active', -- 技能状态
    FOREIGN KEY (tenant_id) REFERENCES tenant(tenant_id),
    UNIQUE KEY `uk_tenant_skill` (tenant_id, skill_name)  -- 确保同一租户下技能名称唯一
);

人才技能关联表：

CREATE TABLE talent_skill (
    talent_skill_id INT PRIMARY KEY AUTO_INCREMENT,    -- 关联记录ID
    talent_id INT NOT NULL,                             -- 关联人才表
    skill_id INT NOT NULL,                              -- 关联技能ID
    FOREIGN KEY (talent_id) REFERENCES talent(talent_id),
    FOREIGN KEY (skill_id) REFERENCES skill(skill_id)
);

4.5 简历（Resume）表

记录人才详细简历，支持多版本和附件存储。

CREATE TABLE resume (
    resume_id INT PRIMARY KEY AUTO_INCREMENT,           -- 简历记录ID
    talent_id INT NOT NULL,                             -- 关联人才表
    version INT DEFAULT 1,                              -- 简历版本号
    resume_content TEXT,                                -- 简历详细描述（支持富文本）
    resume_file_url VARCHAR(255),                       -- 简历附件链接（如 PDF）
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,      -- 创建时间
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,  -- 更新时间
    is_active TINYINT(1) DEFAULT 1,                     -- 是否为当前版本
    FOREIGN KEY (talent_id) REFERENCES talent(talent_id)
);

4.6 专用工种子表（以焊工为例）

记录专用工种的特有信息，与人才表关联。

CREATE TABLE welding_worker (
    talent_id INT PRIMARY KEY,                          -- 关联人才表
    welding_method VARCHAR(50),                         -- 焊接方式，如 MIG、TIG、手工电弧焊等
    welding_certification VARCHAR(100),                 -- 焊工专用证书或资质描述
    years_experience INT,                               -- 焊接年限
    additional_skills TEXT,                             -- 其他相关技能描述
    FOREIGN KEY (talent_id) REFERENCES talent(talent_id)
);

4.7 批量导入日志表

记录批量导入操作日志，便于追踪与问题排查。

CREATE TABLE import_log (
    log_id INT PRIMARY KEY AUTO_INCREMENT,            -- 日志记录ID
    importer VARCHAR(100),                              -- 导入者标识（如学校名称或人力公司账号）
    data_source ENUM('技术学校', '人力公司', '租户自建') DEFAULT '租户自建',
    import_time DATETIME DEFAULT CURRENT_TIMESTAMP,     -- 导入时间
    record_count INT,                                   -- 本次导入记录数
    status ENUM('成功', '失败') DEFAULT '成功',          -- 导入状态
    remark TEXT                                         -- 失败原因或其他说明
);

4.8 自定义人才库模块

4.8.1 自定义人才库（Talent Pool）表

租户创建自定义人才库，用于组织特定招聘需求下的人才。

CREATE TABLE talent_pool (
    pool_id INT PRIMARY KEY AUTO_INCREMENT,         -- 人才库唯一标识
    tenant_id INT NOT NULL,                            -- 归属租户，外键关联 tenant 表
    pool_name VARCHAR(100) NOT NULL,                   -- 人才库名称，如 "2025春季招聘库"
    description TEXT,                                  -- 人才库描述信息
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,     -- 创建时间
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,  -- 更新时间
    FOREIGN KEY (tenant_id) REFERENCES tenant(tenant_id)
);

4.8.2 人才库成员关联（Talent Pool Member）表

用于记录各自定义人才库中包含的人才，引用统一人才表的 talent_id。

CREATE TABLE talent_pool_member (
    member_id INT PRIMARY KEY AUTO_INCREMENT,        -- 关联记录唯一标识
    pool_id INT NOT NULL,                              -- 外键，关联 talent_pool 表
    talent_id INT NOT NULL,                            -- 外键，关联人才表（talent）的 talent_id
    added_at DATETIME DEFAULT CURRENT_TIMESTAMP,       -- 添加时间
    remark VARCHAR(255),                               -- 备注，如人才分类、优先级等
    FOREIGN KEY (pool_id) REFERENCES talent_pool(pool_id),
    FOREIGN KEY (talent_id) REFERENCES talent(talent_id)
);

4.9 用户及权限管理模块

4.9.1 用户表

存储所有平台用户的账户信息。
- 候选人账号为全局用户，不归属租户；
- 租户用户（如用人单位的所有账号）关联到对应租户；
- 平台管理员为全局用户。

CREATE TABLE user (
    user_id INT PRIMARY KEY AUTO_INCREMENT,           -- 用户唯一标识
    tenant_id INT DEFAULT NULL,                         -- 若为租户用户则关联租户ID，其他类型为空
    username VARCHAR(100) NOT NULL UNIQUE,              -- 登录用户名
    password VARCHAR(255) NOT NULL,                     -- 密码（哈希存储）
    email VARCHAR(100),
    phone VARCHAR(20),
    user_type ENUM('candidate', 'tenant', 'admin') NOT NULL,  -- 用户类型：求职者、租户用户、平台管理员
    status ENUM('active', 'inactive') DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (tenant_id) REFERENCES tenant(tenant_id)
);

4.9.2 角色与权限管理

角色表：用于定义系统中的各类角色，如租户管理员、招聘专员等。

CREATE TABLE role (
    role_id INT PRIMARY KEY AUTO_INCREMENT,           -- 角色唯一标识
    role_name VARCHAR(50) NOT NULL UNIQUE,              -- 角色名称，如 tenant_admin、tenant_hr 等
    description VARCHAR(255)                            -- 角色描述
);

-- 示例角色数据
INSERT INTO role (role_name, description) VALUES
('tenant_admin', '租户管理员'),
('tenant_hr', '租户招聘专员'),
('tenant_viewer', '租户只读用户'),
('platform_admin', '平台超级管理员'),
('platform_operator', '平台运营人员');

权限表：

CREATE TABLE permission (
    permission_id INT PRIMARY KEY AUTO_INCREMENT,      -- 权限唯一标识
    permission_name VARCHAR(100) NOT NULL UNIQUE,       -- 权限名称
    description VARCHAR(255)                            -- 权限描述
);

角色权限关联表：

CREATE TABLE role_permission (
    role_permission_id INT PRIMARY KEY AUTO_INCREMENT,  -- 关联记录唯一标识
    role_id INT,                                        -- 关联角色
    permission_id INT,                                  -- 关联权限
    FOREIGN KEY (role_id) REFERENCES role(role_id),
    FOREIGN KEY (permission_id) REFERENCES permission(permission_id)
);

用户角色关联表：

CREATE TABLE user_role (
    user_role_id INT PRIMARY KEY AUTO_INCREMENT,      -- 关联记录唯一标识
    user_id INT NOT NULL,                             -- 关联用户
    role_id INT NOT NULL,                             -- 关联角色
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,     -- 创建时间
    FOREIGN KEY (user_id) REFERENCES user(user_id),
    FOREIGN KEY (role_id) REFERENCES role(role_id)
);

4.10 视图示例

为方便企业查询特定工种人才，例如焊工人才，建立视图将人才表与焊工专用信息关联展示。

CREATE VIEW vw_welding_worker AS
SELECT 
    t.talent_id, 
    t.name, 
    t.phone, 
    t.email, 
    t.address, 
    t.registration_date,
    w.welding_method, 
    w.welding_certification, 
    w.years_experience, 
    w.additional_skills
FROM talent t
JOIN welding_worker w ON t.talent_id = w.talent_id
WHERE t.primary_job_type = 'welding';

4.11 招聘职位模块

4.11.1 职位表

CREATE TABLE jobs (
    id INT PRIMARY KEY AUTO_INCREMENT,               -- 职位唯一标识
    tenant_id INT NOT NULL,                          -- 发布职位的租户ID
    publisher_id INT NOT NULL,                       -- 发布人ID，关联user表
    title VARCHAR(100) NOT NULL,                     -- 职位标题
    job_type VARCHAR(50) NOT NULL,                   -- 工种类型
    headcount INT NOT NULL DEFAULT 1,                -- 招聘人数
    salary_min DECIMAL(10,2),                        -- 薪资范围最小值
    salary_max DECIMAL(10,2),                        -- 薪资范围最大值
    salary_type ENUM('日薪','月薪','年薪') NOT NULL,   -- 薪资类型
    location VARCHAR(255) NOT NULL,                  -- 工作地点
    experience_required VARCHAR(50),                 -- 要求工作经验
    education_required VARCHAR(50),                  -- 学历要求
    description TEXT NOT NULL,                       -- 职位描述
    requirements TEXT,                               -- 岗位要求
    benefits TEXT,                                   -- 福利待遇
    status ENUM('draft','published','closed') DEFAULT 'draft', -- 职位状态
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,   -- 创建时间
    published_at DATETIME,                           -- 发布时间
    closed_at DATETIME,                             -- 关闭时间
    FOREIGN KEY (tenant_id) REFERENCES tenant(tenant_id),
    FOREIGN KEY (publisher_id) REFERENCES user(user_id)
);

4.11.2 职位-技能要求关联表

CREATE TABLE job_required_skill (
    job_skill_id INT PRIMARY KEY AUTO_INCREMENT,    -- 关联记录唯一标识
    job_id INT NOT NULL,                            -- 关联职位ID
    skill_id INT NOT NULL,                          -- 关联技能ID
    is_required BOOLEAN DEFAULT true,               -- 是否必需技能
    FOREIGN KEY (job_id) REFERENCES jobs(id),
    FOREIGN KEY (skill_id) REFERENCES skill(skill_id)
);

4.11.3 职位-证书要求关联表

CREATE TABLE job_required_certification (
    job_cert_id INT PRIMARY KEY AUTO_INCREMENT,     -- 关联记录唯一标识
    job_id INT NOT NULL,                            -- 关联职位ID
    certification_name VARCHAR(100) NOT NULL,        -- 要求的证书名称
    is_required BOOLEAN DEFAULT true,               -- 是否必需证书
    FOREIGN KEY (job_id) REFERENCES jobs(id)
);

4.11.4 职位申请记录表

CREATE TABLE job_application (
    application_id INT PRIMARY KEY AUTO_INCREMENT,   -- 申请记录唯一标识
    job_id INT NOT NULL,                            -- 关联职位ID
    resume_id INT NOT NULL,                         -- 关联简历ID
    status ENUM('pending','reviewed','interviewed','offered','rejected','withdrawn') DEFAULT 'pending', -- 申请状态
    apply_time DATETIME DEFAULT CURRENT_TIMESTAMP,   -- 申请时间
    review_time DATETIME,                           -- 审核时间
    review_notes TEXT,                              -- 审核备注
    FOREIGN KEY (job_id) REFERENCES jobs(id),
    FOREIGN KEY (resume_id) REFERENCES resume(id)   -- 修正为关联简历表的主键id
);

5. 数据流与业务流程说明
	1.	人才数据录入
	•	个人候选人通过前端注册进入 Talent 表（tenant_id 为空，归属于公共人才库）；
	•	租户可自行录入或批量导入私域人才，Talent 表中 tenant_id 填写相应租户编号。
	2.	辅助信息管理
	•	认证、教育、工作经历、技能、简历等均以 talent_id 为外键关联 Talent 表，实现公共与租户私域数据统一管理。
	3.	候选人筛选与组织
	•	租户在平台上筛选候选人后，在 Candidate 表生成记录，明确候选人与租户的归属；
	•	同时租户可创建自定义人才库（Talent Pool），并通过 Talent Pool Member 表组织管理不同招聘需求下的人才。
	4.	用户及权限控制
	•	系统采用用户类型（User Type）和用户角色（Role）两层设计
	•	用户类型分为：求职者（candidate）、租户用户（tenant）、平台管理员（admin）
	•	通过角色（Role）和权限（Permission）实现细粒度的权限控制
	•	租户用户（如技术学校、人力资源公司、用人单位）通过不同角色区分具体权限
	5.	查询与展示
	•	利用视图和租户过滤条件，确保租户只能访问与自己相关的数据，同时公共人才库数据对所有租户开放查看权限。
	6. 职位发布与申请流程
    • 租户可创建职位信息，设置职位要求、技能要求和证书要求
    • 职位可以是草稿、已发布或已关闭状态
    • 求职者可以查看已发布的职位并提交申请
    • 申请记录跟踪整个应聘流程，包括待审核、已审核、已面试、已录用等状态

6. 总结

本设计方案采用统一的人才表管理公共人才和租户私域人才，通过 tenant_id 字段实现数据隔离，并利用统一的辅助信息表、候选人记录、简历、专用工种扩展模块及自定义人才库功能，满足 SaaS 多租户平台对人才数据管理、筛选与组织的需求。同时结合用户及权限管理模块，实现细粒度的操作权限控制，确保数据安全。该方案具有以下特点：
	•	统一管理与扩展：所有人才数据存储于单一表中，扩展信息通过 talent_id 关联，结构清晰、易于维护。
	•	多租户隔离：通过 Tenant 表和 tenant_id 字段，实现公共数据与租户私域数据严格隔离，同时提供数据共享。
	•	自定义人才库：租户可根据需求创建自定义人才库，方便对特定招聘项目进行组织和管理。
	•	灵活的权限控制：基于 RBAC 的用户、角色、权限管理确保各类用户只能访问和操作授权数据。
	•	便于后续扩展：统一的数据模型和模块化设计为后续智能匹配、数据统计和业务流程优化提供了坚实基础。

该设计方案为蓝领用工平台提供了全面且灵活的数据存储和管理方案，适用于 SaaS 多租户场景下的实际业务需求。

