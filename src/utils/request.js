import axios from 'axios'
import { Message } from 'element-ui'
import store from '@/store'
import { getToken } from '@/utils/auth'

// create an axios instance
const service = axios.create({
  baseURL: process.env.VUE_APP_BASE_API, // url = base url + request url
  withCredentials: true,  // 允许跨域请求携带cookie
  timeout: 5000 // request timeout
})

// request interceptor
service.interceptors.request.use(
  config => {
    // do something before request is sent

    if (store.getters.token) {
      // 修改这里,使用Bearer认证方案
      config.headers['Authorization'] = `Bearer ${getToken()}`
    }
    return config
  },
  error => {
    // do something with request error
    console.log(error) // for debug
    return Promise.reject(error)
  }
)

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
    const res = response.data
    
    // 添加响应数据日志
    console.log('接口响应数据:', {
      url: response.config.url,
      status: response.status,
      data: res
    })

    // 处理登录成功的情况
    if (res.access_token) {
      return res
    }

    // 如果响应中包含 data 字段，说明是正常的业务数据
    if (res.data !== undefined) {
      return res
    }

    // 处理错误情况
    const errorMsg = res.detail || res.message || 'Error'
    Message({
      message: errorMsg,
      type: 'error',
      duration: 5 * 1000
    })
    return Promise.reject(new Error(errorMsg))
  },
  error => {
    console.error('请求错误:', {
      url: error.config?.url,
      method: error.config?.method,
      params: error.config?.params,
      data: error.config?.data,
      status: error.response?.status,
      statusText: error.response?.statusText,
      responseData: error.response?.data,
      errorMessage: error.message
    })

    const errMsg = error.response?.data?.detail || error.message || 'Error'
    Message({
      message: errMsg,
      type: 'error',
      duration: 5 * 1000
    })

    if (error.response?.status === 401) {
      store.dispatch('user/resetToken').then(() => {
        location.reload()
      })
    }

    return Promise.reject(error)
  }
)

export default service
