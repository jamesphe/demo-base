import http from 'k6/http';
import { check, sleep } from 'k6';

const BACKEND_URL = __ENV.K6_BACKEND_URL || 'http://resume-backend:8000';
const BASE_API = `${BACKEND_URL}/api/v1`;

export const options = {
  stages: [
    { duration: '30s', target: 20 }, // 在30秒内逐步增加到20个虚拟用户
    { duration: '1m', target: 20 },  // 保持20个虚拟用户1分钟
    { duration: '30s', target: 0 },  // 在30秒内逐步减少到0个虚拟用户
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95%的请求应该在500ms内完成
    http_req_failed: ['rate<0.01'],   // 失败率应该小于1%
  },
};

// 测试场景
export default function () {
  // 测试 1: 健康检查接口
  const healthCheck = http.get(`${BASE_API}/health`);
  check(healthCheck, {
    '健康检查状态为 200': (r) => r.status === 200,
  });
  
  // 测试 2: 登录获取token
  // 注意：根据前端调用，登录使用的是表单格式
  const loginPayload = `username=${encodeURIComponent('admin@admin.com')}&password=${encodeURIComponent('admin')}`;
  const loginParams = {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    },
  };
  const loginRes = http.post(`${BASE_API}/login/access-token`, loginPayload, loginParams);
  check(loginRes, {
    '登录状态为 200': (r) => r.status === 200,
  });
  
  let token = '';
  try {
    if (loginRes.json('access_token')) {
      token = loginRes.json('access_token');
      console.log('获取到token格式1: access_token');
    } else if (loginRes.json('data') && loginRes.json('data.access_token')) {
      token = loginRes.json('data.access_token');
      console.log('获取到token格式2: data.access_token');
    }
    
    if (token) {
      console.log('成功获取到token');
    }
  } catch (e) {
    console.log('无法获取token：', e.message);
    try {
      console.log('响应内容：', JSON.stringify(loginRes).substring(0, 200));
    } catch (err) {
      console.log('无法打印响应内容');
    }
  }
  
  sleep(1);
} 