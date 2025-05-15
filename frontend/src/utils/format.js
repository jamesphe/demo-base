/**
 * 格式化工具函数
 */
import { parseTime } from '@/utils'

/**
 * 格式化日期时间
 * @param {Date|string|number} time 时间
 * @param {string} pattern 格式模式
 * @returns {string} 格式化后的时间字符串
 */
export function formatDateTime(time, pattern = '{y}-{m}-{d} {h}:{i}:{s}') {
  return parseTime(time, pattern)
}

/**
 * 格式化日期
 * @param {Date|string|number} time 时间
 * @returns {string} 格式化后的日期字符串 YYYY-MM-DD
 */
export function formatDate(time) {
  return parseTime(time, '{y}-{m}-{d}')
}

/**
 * 格式化货币
 * @param {number} amount 金额
 * @param {string} currency 货币符号
 * @param {number} decimals 小数位数
 * @returns {string} 格式化后的货币字符串
 */
export function formatCurrency(amount, currency = '¥', decimals = 2) {
  if (amount === null || amount === undefined) return ''
  
  const num = parseFloat(amount)
  if (isNaN(num)) return ''
  
  return currency + ' ' + num.toFixed(decimals).replace(/\d(?=(\d{3})+\.)/g, '$&,')
}

/**
 * 格式化百分比
 * @param {number} value 值
 * @param {number} decimals 小数位数
 * @returns {string} 格式化后的百分比字符串
 */
export function formatPercent(value, decimals = 2) {
  if (value === null || value === undefined) return ''
  
  const num = parseFloat(value)
  if (isNaN(num)) return ''
  
  return (num * 100).toFixed(decimals) + '%'
}

/**
 * 格式化文件大小
 * @param {number} bytes 字节数
 * @returns {string} 格式化后的文件大小
 */
export function formatFileSize(bytes) {
  if (bytes === 0) return '0 B'
  
  const units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
  const k = 1024
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + units[i]
}

/**
 * 格式化电话号码
 * @param {string} phone 电话号码
 * @returns {string} 格式化后的电话号码
 */
export function formatPhone(phone) {
  if (!phone) return ''
  
  // 处理中国大陆手机号
  if (/^1\d{10}$/.test(phone)) {
    return phone.replace(/(\d{3})(\d{4})(\d{4})/, '$1 $2 $3')
  }
  
  return phone
}

/**
 * 格式化数字，添加千分位
 * @param {number} num 数字
 * @returns {string} 格式化后的数字
 */
export function formatNumber(num) {
  if (num === null || num === undefined) return ''
  
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

/**
 * 格式化时长(秒转为时分秒)
 * @param {number} seconds 秒数
 * @returns {string} 格式化后的时长
 */
export function formatDuration(seconds) {
  if (!seconds || isNaN(seconds)) return '0秒'
  
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = Math.floor(seconds % 60)
  
  let result = ''
  if (h > 0) result += h + '小时'
  if (m > 0) result += m + '分'
  if (s > 0 || (h === 0 && m === 0)) result += s + '秒'
  
  return result
}

/**
 * 格式化姓名，保留姓氏，其他用*代替
 * @param {string} name 姓名
 * @returns {string} 格式化后的姓名
 */
export function formatName(name) {
  if (!name) return ''
  
  if (name.length === 2) {
    return name.substr(0, 1) + '*'
  } else if (name.length > 2) {
    const firstName = name.substr(0, 1)
    const stars = new Array(name.length - 1).fill('*').join('')
    return firstName + stars
  }
  
  return name
}

export default {
  formatDateTime,
  formatDate,
  formatCurrency,
  formatPercent,
  formatFileSize,
  formatPhone,
  formatNumber,
  formatDuration,
  formatName
} 