# 简历系统冒烟测试

这个目录包含简历系统的端到端冒烟测试，使用 Playwright 实现自动化测试。

## 测试范围

冒烟测试覆盖以下关键功能：

1. **基础功能**
   - 首页加载
   - 用户登录

2. **简历功能**
   - 查看简历列表
   - 创建新简历
   - 预览简历

3. **搜索功能**
   - 基本搜索
   - 无结果处理
   - 高级搜索

4. **API 健康度**
   - API 状态检查
   - 关键 API 功能验证

## 运行测试

在 Docker 环境中运行：

```bash
docker-compose -f docker/docker-compose.smoke.yml up
```

在本地环境运行：

```bash
# 安装依赖
npm install

# 运行所有冒烟测试
npm run smoke
```

## 测试报告

测试完成后，HTML 报告将生成在 `playwright-report` 目录中。

## 自定义测试环境

可以通过环境变量自定义测试配置：

- `BASE_URL`: 前端服务地址 (默认: http://localhost:6111)
- `API_URL`: 后端服务地址 (默认: http://resume-backend:8000)
- `WAIT_TIMEOUT`: 等待超时时间 (默认: 30000ms)

## 添加新测试

1. 在 `tests/smoke` 目录下创建新的 `.spec.js` 文件
2. 使用 Playwright API 编写测试用例
3. 运行测试验证 