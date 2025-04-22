const { test, expect } = require('@playwright/test');

test.beforeEach(async ({ page }) => {
  // 首先进行登录操作
  await page.goto('/login');
  await page.fill('input[name="username"]', 'testuser');
  await page.fill('input[name="password"]', 'password123');
  await page.click('button[type="submit"]');
  
  // 等待登录成功
  await expect(page.locator('text=欢迎回来')).toBeVisible({ timeout: 5000 });
});

test('能够查看简历列表', async ({ page }) => {
  // 访问简历列表页面
  await page.goto('/resumes');
  
  // 确认页面包含简历列表
  await expect(page.locator('.resume-list')).toBeVisible();
  
  // 验证至少有一个简历项存在
  const resumeItems = await page.locator('.resume-item').count();
  expect(resumeItems).toBeGreaterThan(0);
});

test('能够创建新简历', async ({ page }) => {
  // 访问创建简历页面
  await page.goto('/resumes/create');
  
  // 填写简历表单
  await page.fill('input[name="title"]', '测试简历');
  await page.fill('textarea[name="summary"]', '这是一份测试简历的简介');
  
  // 添加一个技能
  await page.click('button:has-text("添加技能")');
  await page.fill('input[name="skills[0].name"]', 'JavaScript');
  await page.selectOption('select[name="skills[0].level"]', '熟练');
  
  // 提交表单
  await page.click('button[type="submit"]');
  
  // 验证创建成功
  await expect(page.locator('text=简历创建成功')).toBeVisible({ timeout: 5000 });
});

test('能够预览简历', async ({ page }) => {
  // 访问简历列表
  await page.goto('/resumes');
  
  // 点击第一个简历的预览按钮
  await page.click('.resume-item >> text=预览');
  
  // 验证预览页面加载
  await expect(page.locator('.resume-preview')).toBeVisible();
  
  // 检查预览中包含基本信息
  await expect(page.locator('.resume-title')).toBeVisible();
  await expect(page.locator('.resume-summary')).toBeVisible();
}); 