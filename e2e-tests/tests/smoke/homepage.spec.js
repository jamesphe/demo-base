const { test, expect } = require('@playwright/test');

test('首页能够正常加载', async ({ page }) => {
  await page.goto('/');
  
  // 检查页面标题是否正确
  const title = await page.title();
  expect(title).toContain('简历系统');
  
  // 检查导航栏是否存在
  await expect(page.locator('nav')).toBeVisible();
  
  // 检查页面上是否有标题文本
  await expect(page.locator('h1')).toBeVisible();
});

test('登录功能正常工作', async ({ page }) => {
  await page.goto('/login');
  
  // 填写登录表单
  await page.fill('input[name="username"]', 'testuser');
  await page.fill('input[name="password"]', 'password123');
  
  // 点击登录按钮
  await page.click('button[type="submit"]');
  
  // 验证登录成功
  await expect(page.locator('text=欢迎回来')).toBeVisible({ timeout: 5000 });
}); 