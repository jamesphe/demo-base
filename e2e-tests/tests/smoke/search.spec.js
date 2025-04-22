const { test, expect } = require('@playwright/test');

test('搜索功能正常工作', async ({ page }) => {
  // 访问首页
  await page.goto('/');
  
  // 输入搜索关键词
  await page.fill('input[type="search"]', '工程师');
  
  // 点击搜索按钮
  await page.click('button:has-text("搜索")');
  
  // 确认搜索结果页面加载
  await expect(page.locator('.search-results')).toBeVisible();
  
  // 检查搜索结果中包含搜索关键词
  const resultText = await page.locator('.search-results').innerText();
  expect(resultText.toLowerCase()).toContain('工程师');
});

test('无结果搜索正确处理', async ({ page }) => {
  // 访问首页
  await page.goto('/');
  
  // 输入一个不太可能有结果的搜索词
  await page.fill('input[type="search"]', 'xyzzzzzzz12345');
  
  // 点击搜索按钮
  await page.click('button:has-text("搜索")');
  
  // 确认显示无结果信息
  await expect(page.locator('text=未找到匹配结果')).toBeVisible();
});

test('高级搜索功能可用', async ({ page }) => {
  // 访问高级搜索页面
  await page.goto('/advanced-search');
  
  // 填写高级搜索表单
  await page.fill('input[name="keywords"]', '前端');
  await page.selectOption('select[name="experience"]', '3-5年');
  await page.check('input[name="skills"][value="React"]');
  
  // 提交高级搜索
  await page.click('button[type="submit"]');
  
  // 检查搜索结果
  await expect(page.locator('.search-results')).toBeVisible();
  
  // 验证筛选条件是否生效
  const filterText = await page.locator('.active-filters').innerText();
  expect(filterText).toContain('前端');
  expect(filterText).toContain('React');
}); 