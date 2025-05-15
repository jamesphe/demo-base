import Vue from 'vue'
import Router from 'vue-router'
import VueCompositionAPI from '@vue/composition-api'

import Cookies from 'js-cookie'

import 'normalize.css/normalize.css' // a modern alternative to CSS resets

import Element from 'element-ui'
import './styles/element-variables.scss'
import zhCN from 'element-ui/lib/locale/lang/zh-CN'

import '@/styles/index.scss' // global css

import App from './App'
import store from './store'
import router from './router'

import './icons' // icon
import './permission' // permission control
import './utils/error-log' // error log

import * as filters from './filters' // global filters
import CustomComponents from '@/components'

/**
 * If you don't want to use mock-server
 * you want to use MockJs for mock api
 * you can execute: mockXHR()
 *
 * Currently MockJs will be used in the development environment,
 * please remove it before going online ! ! !
 */
if (process.env.NODE_ENV === 'development') {
  const { mockXHR } = require('../mock')
  mockXHR()
}

Vue.use(Element, {
  size: Cookies.get('size') || 'medium', // set element-ui default size
  locale: zhCN
})

// 注册自定义组件
Vue.use(CustomComponents)

// register global utility filters
Object.keys(filters).forEach(key => {
  Vue.filter(key, filters[key])
})

// 正确注册 Vue Router
Vue.use(Router)

Vue.use(VueCompositionAPI)

Vue.config.productionTip = false

// 防止路由重复点击报错
const originalPush = Router.prototype.push
Router.prototype.push = function push(location) {
  try {
    return originalPush.call(this, location)
  } catch (err) {
    if (err.name !== 'NavigationDuplicated') {
      throw err
    }
  }
}

new Vue({
  el: '#app',
  router,
  store,
  render: h => h(App)
})
