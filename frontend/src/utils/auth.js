import Cookies from 'js-cookie'

const TokenKey = 'Admin-Token'

// 添加一个辅助函数来统一处理令牌格式
export function formatToken(token) {
  if (!token) return ''
  // 如果令牌已经包含Bearer前缀，则直接返回
  if (token.startsWith('Bearer ')) return token
  // 否则添加Bearer前缀
  return `Bearer ${token}`
}

export function getToken() {
  const token = Cookies.get(TokenKey)
  return token
}

export function setToken(token) {
  // 存储原始令牌，不添加Bearer前缀
  return Cookies.set(TokenKey, token)
}

export function removeToken() {
  return Cookies.remove(TokenKey)
}
