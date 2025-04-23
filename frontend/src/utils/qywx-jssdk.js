import request from '@/utils/request'

let isWxConfigReady = false
let wxReadyCallbacks = []

/**
 * 配置企业微信JS-SDK
 * @param {String} pageUrl 当前页面URL，不含#号及其后面部分
 * @returns {Promise} 配置结果
 */
export async function configWxJsApi(pageUrl) {
  if (isWxConfigReady) return Promise.resolve(true)
  
  try {
    // 获取签名配置
    const url = pageUrl || window.location.href.split('#')[0]
    const res = await request({
      url: '/api/auth/qywx/jsapi_config',
      method: 'get',
      params: { url: encodeURIComponent(url) }
    })
    
    if (!res.data || res.data.errcode !== 0) {
      console.error('获取企业微信JS-SDK配置失败', res.data)
      return Promise.reject(new Error('获取企业微信JS-SDK配置失败'))
    }
    
    const config = res.data.config
    
    return new Promise((resolve, reject) => {
      if (typeof wx === 'undefined') {
        return reject(new Error('企业微信JS-SDK未加载'))
      }
      
      // 配置JS-SDK
      wx.config({
        beta: true,
        debug: process.env.NODE_ENV === 'development',
        appId: config.corpid,
        timestamp: config.timestamp,
        nonceStr: config.noncestr,
        signature: config.signature,
        jsApiList: [
          'selectExternalContact',
          'openUserProfile',
          'scanQRCode',
          'shareToExternalChat',
          'chooseImage',
          'getLocalImgData'
        ]
      })
      
      // 注册成功回调
      wx.ready(() => {
        console.log('企业微信JS-SDK初始化成功')
        isWxConfigReady = true
        
        // 执行所有等待的回调
        wxReadyCallbacks.forEach(callback => callback())
        wxReadyCallbacks = []
        
        resolve(true)
      })
      
      // 注册失败回调
      wx.error(err => {
        console.error('企业微信JS-SDK初始化失败', err)
        isWxConfigReady = false
        reject(err)
      })
    })
  } catch (error) {
    console.error('配置企业微信JS-SDK失败', error)
    return Promise.reject(error)
  }
}

/**
 * 注册wx.ready回调
 * @param {Function} callback 回调函数
 */
export function registerWxReady(callback) {
  if (isWxConfigReady) {
    callback()
  } else {
    wxReadyCallbacks.push(callback)
  }
}

/**
 * 扫描二维码
 * @returns {Promise<String>} 扫描结果
 */
export function scanQRCode() {
  return new Promise((resolve, reject) => {
    registerWxReady(() => {
      wx.scanQRCode({
        needResult: 1,
        scanType: ['qrCode', 'barCode'],
        success: function(res) {
          resolve(res.resultStr)
        },
        fail: function(err) {
          reject(err)
        }
      })
    })
  })
}

/**
 * 选择图片
 * @returns {Promise<Array>} 图片列表
 */
export function chooseImage(count = 1) {
  return new Promise((resolve, reject) => {
    registerWxReady(() => {
      wx.chooseImage({
        count: count,
        sizeType: ['original', 'compressed'],
        sourceType: ['album', 'camera'],
        success: function(res) {
          resolve(res.localIds)
        },
        fail: function(err) {
          reject(err)
        }
      })
    })
  })
}

/**
 * 获取本地图片数据
 * @param {String} localId 本地图片ID
 * @returns {Promise<String>} 图片base64数据
 */
export function getLocalImgData(localId) {
  return new Promise((resolve, reject) => {
    registerWxReady(() => {
      wx.getLocalImgData({
        localId: localId,
        success: function(res) {
          resolve(res.localData)
        },
        fail: function(err) {
          reject(err)
        }
      })
    })
  })
} 