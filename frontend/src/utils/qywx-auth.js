import Cookies from 'js-cookie'
import { getToken } from '@/utils/auth'
import router from '@/router'
import request from '@/utils/request'

/**
 * 判断是否在企业微信环境中
 */
export function isInWorkWechat() {
  return /wxwork/i.test(navigator.userAgent)
}

/**
 * 获取企业微信网页授权链接
 * @param {String} redirectUri 授权后重定向的地址
 * @returns {Promise} 授权链接
 */
export async function getQywxAuthUrl(redirectUri) {
  try {
    const res = await request({
      url: '/api/auth/qywx/web-auth',
      method: 'get',
      params: { redirect_uri: redirectUri }
    })
    return res.data
  } catch (error) {
    console.error('获取企业微信授权链接失败', error)
    return null
  }
}

/**
 * 从URL中获取授权码并登录
 * @returns {Promise<Boolean>} 是否登录成功
 */
export async function handleQywxAuth() {
  // 获取URL参数
  const urlParams = new URLSearchParams(window.location.search)
  const code = urlParams.get('code')
  const appid = urlParams.get('appid')
  
  // 清除URL参数，避免刷新页面时重复授权
  if (code && appid) {
    const newUrl = window.location.href.split('?')[0]
    window.history.replaceState({}, document.title, newUrl)
    
    // 判断是否已有有效token
    if (getToken()) {
      return true
    }
    
    try {
      // 调用后端登录接口
      const res = await request({
        url: '/api/auth/qywx/login',
        method: 'post',
        data: { code, appid }
      })
      
      if (res.data && res.data.token) {
        // 保存token和用户信息
        Cookies.set('Token', res.data.token)
        localStorage.setItem('userInfo', JSON.stringify(res.data.user))
        return true
      }
    } catch (error) {
      console.error('企业微信登录失败', error)
      return false
    }
  }
  
  return false
}

/**
 * 检测并处理企微认证
 * @returns {Promise<Boolean>} 是否已认证
 */
export async function checkQywxAuth() {
  // 如果在企微环境中，且没有登录态
  if (isInWorkWechat() && !getToken()) {
    // 尝试处理URL中的授权码
    const authResult = await handleQywxAuth()
    
    if (!authResult) {
      // 重定向到企业微信授权页
      const authUrl = await getQywxAuthUrl(window.location.href)
      if (authUrl && authUrl.auth_url) {
        window.location.href = authUrl.auth_url
        return false
      }
    }
  }
  
  return true
}

/**
 * 获取企业微信登录URL
 * @returns {Promise} 返回包含auth_url的Promise
 */
export function getQyWxAuthUrl() {
  return request({
    url: '/auth/qywx/qywx/login-url',
    method: 'get'
  })
}

/**
 * 使用企业微信授权码进行登录
 * @param {Object} data - 包含code和appid的对象
 * @returns {Promise} 返回登录结果Promise
 */
export function loginWithQyWxCode(data) {
  return request({
    url: '/auth/qywx/qywx/login',
    method: 'post',
    data
  })
}

/**
 * 获取企业微信JSAPI配置
 * @param {String} url - 当前页面URL
 * @returns {Promise} 返回JSAPI配置Promise
 */
export function getQyWxJsapiConfig(url) {
  return request({
    url: '/auth/qywx/qywx/jsapi_config',
    method: 'get',
    params: { url }
  })
} 