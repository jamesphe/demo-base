import axios from 'axios'
import store from '@/store'
import { getToken } from '@/utils/auth'

// create an axios instance
const service = axios.create({
  baseURL: process.env.VUE_APP_BASE_API, // url = base url + request url
  withCredentials: true, // 允许跨域请求携带cookie
  timeout: 5000 // request timeout
})

// request interceptor
service.interceptors.request.use(
  config => {
    // do something before request is sent

    if (store.getters.token) {
      const token = getToken()
      console.log('Current token in interceptor:', token)
      config.headers['Authorization'] = 'Bearer ' + token
    }

    console.log('Request headers:', config.headers)
    console.log('发送请求:', config.url, config.method, config.params || config.data)
    return config
  },
  error => {
    // do something with request error
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 添加一个转换函数：将下划线命名转为驼峰命名
function convertToCamelCase(data) {
  if (Array.isArray(data)) {
    return data.map(item => convertToCamelCase(item))
  }
  if (data !== null && typeof data === 'object') {
    const newData = {}
    Object.keys(data).forEach(key => {
      const newKey = key.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase())
      newData[newKey] = convertToCamelCase(data[key])
    })
    return newData
  }
  return data
}

// response interceptor
service.interceptors.response.use(
  /**
   * If you want to get http information such as headers or status
   * Please return  response => response
  */

  /**
   * Determine the request status by custom code
   * Here is just an example
   * You can also judge the status by HTTP Status Code
   */
  response => {
    // 直接返回响应数据，不需要包装
    const convertedData = convertToCamelCase(response.data)

    console.log('收到响应:', response.config.url, response.status, convertedData)
    return convertedData
  },
  error => {
    console.error('响应错误:', error)

    const status = error.response?.status
    // 获取错误信息，优先使用后端返回的message字段
    const errMsg = error.response?.data?.message ||
                  error.response?.data?.detail ||
                  '系统错误'

    // 根据不同的 HTTP 状态码处理
    switch (status) {
      case 400:
        error.message = errMsg
        break
      case 401:
        error.message = errMsg || '用户名或密码错误'
        // 只有在token失效时才重置
        if (errMsg === 'token已失效') {
          store.dispatch('user/resetToken').then(() => {
            location.reload()
          })
        }
        break
      case 403:
        error.message = '没有操作权限'
        break
      case 404:
        error.message = '请求的资源不存在'
        break
      default:
        error.message = errMsg
    }

    return Promise.reject(error)
  }
)

export default service
