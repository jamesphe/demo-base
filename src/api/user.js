import request from '@/utils/request'

export function login(data) {
  console.log('\n=== Login Request Data ===');
  console.log('Username:', data.username);
  console.log('Password:', data.password);
  
  const formData = new URLSearchParams({
    grant_type: 'password',
    username: data.username,
    password: data.password,
    scope: '',
    client_id: 'string',
    client_secret: 'string'
  }).toString();
  
  console.log('Form Data:', formData);
  
  return request({
    url: '/api/v1/login/access-token',
    method: 'post',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'Accept': 'application/json'
    },
    data: formData,
    timeout: 10000,
    withCredentials: false
  })
}

export function getInfo() {
  return request({
    url: '/api/v1/users/me',
    method: 'get'
  })
}

export function logout() {
  return request({
    url: '/api/v1/auth/logout',
    method: 'post'
  })
}
