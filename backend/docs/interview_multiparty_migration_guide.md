# 面试系统多面试官支持迁移指南

本文档描述了如何将面试系统从单一面试官模式升级到支持多个面试官同时参与的模式。

## 数据库迁移

迁移过程分为两个主要步骤，以确保数据安全：

1. 创建多对多关系表并迁移数据（执行 `update_interview_interviewer_relationship.sql`）
2. 确认数据迁移成功后移除原表中的面试官ID字段（执行 `finalize_interview_interviewer_migration.sql`）

### 执行迁移的步骤

1. 首先执行第一个脚本，创建多对多关系表并迁移数据：

```bash
psql -U <用户名> -d <数据库名> -f backend/scripts/update_interview_interviewer_relationship.sql
```

2. 检查输出，确认数据迁移是否成功。脚本会显示类似下面的信息：

```
NOTICE:  原始面试记录数: XX
NOTICE:  迁移的面试官关联数: XX
NOTICE:  数据迁移成功完成
```

3. 如果数据迁移成功，执行第二个脚本移除原表中的面试官ID字段：

```bash
psql -U <用户名> -d <数据库名> -f backend/scripts/finalize_interview_interviewer_migration.sql
```

4. 检查输出，确认面试官ID字段是否成功移除：

```
NOTICE:  面试官ID列已成功移除，多对多关系迁移完成
```

## 代码迁移

完成数据库迁移后，需要更新代码以支持多面试官模式。主要涉及以下文件：

### 模型更新

1. `backend/app/models/interview_interviewer.py` - 新建文件，定义多对多关系表
2. `backend/app/models/interview.py` - 更新面试模型，使用多对多关系

### Schema更新

1. `backend/app/schemas/interview.py` - 更新面试Schema，支持多个面试官

### API和服务更新

1. `backend/app/api/api_v1/endpoints/interviews.py` - 更新API端点支持多面试官
2. `backend/app/services/interview_service.py` - 更新服务层支持多面试官
3. `backend/app/crud/crud_interview.py` - 更新CRUD操作支持多面试官

### 前端更新

1. `frontend/src/api/interview.js` - 更新API调用
2. `frontend/src/views/interview/schedule.vue` - 更新面试安排视图
3. `frontend/src/views/interview/evaluation.vue` - 更新面试评估视图
4. `frontend/src/store/modules/interview.js` - 更新Store模块

## 测试

完成迁移后，需要测试以下功能：

1. 创建面试时能选择多个面试官
2. 面试列表能正确显示所有面试官
3. 更新面试时能修改面试官列表
4. 查询特定面试官的面试记录能正确返回结果
5. 检查面试时间冲突能正确考虑多个面试官的时间安排

## 已知问题和注意事项

- 记得使用 `interviewers` 作为多面试官的参数，或者使用 `interviewer_ids`。前端提交的数据需要包含完整的面试官ID列表。
- 面试评估暂时仍是按照每次面试只有一个评估，未来可能需要支持每个面试官提交各自的评估。
- 如果发现bug，可以检查后端日志，看数据处理是否正确。 