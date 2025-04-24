import Vue from 'vue'
import Router from 'vue-router'
import VueCompositionAPI from '@vue/composition-api'

import Cookies from 'js-cookie'

import 'normalize.css/normalize.css' // a modern alternative to CSS resets

import Element from 'element-ui'
import './styles/element-variables.scss'
import zhCN from 'element-ui/lib/locale/lang/zh-CN'
import enUS from 'element-ui/lib/locale/lang/en'

import '@/styles/index.scss' // global css

import App from './App'
import store from './store'
import router from './router'

import './icons' // icon
import './permission' // permission control
import './utils/error-log' // error log

// 引入i18n国际化
import VueI18n from 'vue-i18n'
import messages from './lang'

import * as filters from './filters' // global filters

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

// 使用i18n
Vue.use(VueI18n)
const i18n = new VueI18n({
  locale: store.getters.language, // 设置语言环境
  messages // 设置语言环境信息
})

Vue.use(Element, {
  size: Cookies.get('size') || 'medium', // set element-ui default size
  i18n: (key, value) => i18n.t(key, value) // 为Element-UI设置国际化
})

// register global utility filters
Object.keys(filters).forEach(key => {
  Vue.filter(key, filters[key])
})

// 正确注册 Vue Router
Vue.use(Router)

Vue.use(VueCompositionAPI)

Vue.config.productionTip = false

new Vue({
  el: '#app',
  router,
  store,
  i18n,
  render: h => h(App)
})
