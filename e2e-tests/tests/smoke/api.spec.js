const { test, expect } = require('@playwright/test');

test('API状态检查', async ({ request }) => {
  const response = await request.get(`${process.env.API_URL || 'http://resume-backend:8000'}/api/health`);
  expect(response.ok()).toBeTruthy();
  
  const body = await response.json();
  expect(body.status).toBe('ok');
});

test('获取简历列表API', async ({ request }) => {
  // 先进行登录获取token
  const loginResponse = await request.post(`${process.env.API_URL || 'http://resume-backend:8000'}/api/auth/login`, {
    data: {
      username: 'testuser',
      password: 'password123'
    }
  });
  expect(loginResponse.ok()).toBeTruthy();
  const loginData = await loginResponse.json();
  expect(loginData.token).toBeDefined();
  
  // 使用token获取简历列表
  const resumesResponse = await request.get(`${process.env.API_URL || 'http://resume-backend:8000'}/api/resumes`, {
    headers: {
      'Authorization': `Bearer ${loginData.token}`
    }
  });
  
  expect(resumesResponse.ok()).toBeTruthy();
  const resumes = await resumesResponse.json();
  expect(Array.isArray(resumes)).toBeTruthy();
});

test('搜索API正常工作', async ({ request }) => {
  const searchResponse = await request.get(`${process.env.API_URL || 'http://resume-backend:8000'}/api/search?q=工程师`);
  expect(searchResponse.ok()).toBeTruthy();
  
  const results = await searchResponse.json();
  expect(results.items).toBeDefined();
  expect(Array.isArray(results.items)).toBeTruthy();
  expect(results.total).toBeDefined();
}); 