import http from 'k6/http';
import { check, sleep } from 'k6';

const BACKEND_URL = __ENV.K6_BACKEND_URL || 'http://resume-backend:8000';

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
  const healthCheck = http.get(`${BACKEND_URL}/api/health`);
  check(healthCheck, {
    'health check status is 200': (r) => r.status === 200,
  });
  
  // 登录获取 token 
  const loginPayload = JSON.stringify({
    username: 'test_user',
    password: 'test_password'
  });
  const loginParams = {
    headers: {
      'Content-Type': 'application/json',
    },
  };
  const loginRes = http.post(`${BACKEND_URL}/api/login`, loginPayload, loginParams);
  check(loginRes, {
    'login status is 200': (r) => r.status === 200,
  });
  
  let token = '';
  try {
    token = loginRes.json('data.token');
  } catch (e) {
    console.log('无法获取token，但继续测试');
  }
  
  const authHeaders = {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
  };
  
  // 测试 2: 获取活动详情
  const activityId = 4; // 根据日志中的ID
  const activityRes = http.get(`${BACKEND_URL}/api/activities/${activityId}`, authHeaders);
  check(activityRes, {
    'get activity status is 200': (r) => r.status === 200,
  });
  
  // 测试 3: 获取活动奖品列表 (出错的接口)
  const prizesRes = http.get(`${BACKEND_URL}/api/activities/${activityId}/prizes`, authHeaders);
  check(prizesRes, {
    'get prizes status is 200': (r) => r.status === 200,
  });
  
  // 为了找出问题，添加不同的参数测试
  const prizesWithParamsRes = http.get(`${BACKEND_URL}/api/activities/${activityId}/prizes?active=true`, authHeaders);
  check(prizesWithParamsRes, {
    'get prizes with params status is 200': (r) => r.status === 200,
  });
  
  sleep(1);
} 