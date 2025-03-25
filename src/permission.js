import router from './router'
import store from './store'
import { Message } from 'element-ui'
import NProgress from 'nprogress' // progress bar
import 'nprogress/nprogress.css' // progress bar style
import { getToken } from '@/utils/auth' // get token from cookie
import getPageTitle from '@/utils/get-page-title'
import { getUserPermissions } from '@/api/user' // 导入获取用户权限的API函数

NProgress.configure({ showSpinner: false }) // NProgress Configuration

const whiteList = ['/', '/login', '/register', '/trial-application'] // 无需权限验证的路由路径白名单

router.beforeEach(async(to, from, next) => {
  // 如果是白名单中的路径，直接放行
  if (whiteList.includes(to.path)) {
    next()
    return
  }

  // start progress bar
  NProgress.start()

  // set page title
  document.title = getPageTitle(to.meta.title)

  // determine whether the user has logged in
  const hasToken = getToken()

  if (hasToken) {
    if (to.path === '/login') {
      // if is logged in, redirect to the home page
      next({ path: '/' })
      NProgress.done() // hack: https://github.com/PanJiaChen/vue-element-admin/pull/2939
    } else {
      // 获取用户信息
      const hasGetUserInfo = store.getters.name
      if (hasGetUserInfo) {
        // 如果是试用用户且试用已过期，跳转到试用状态页面
        if (store.getters.isTrialUser && store.getters.trialStatus === 'expired' &&
            to.path !== '/trial-status' && to.path !== '/pricing') {
          next({ path: '/trial-status' })
        } else {
          next()
        }
      } else {
        try {
          await store.dispatch('user/getInfo')
          await store.dispatch('user/getTrialStatus')

          // 如果是试用用户且试用已过期，跳转到试用状态页面
          if (store.getters.isTrialUser && store.getters.trialStatus === 'expired' &&
              to.path !== '/trial-status' && to.path !== '/pricing') {
            next({ path: '/trial-status' })
          } else {
            next()
          }
        } catch (error) {
          // remove token and go to login page to re-login
          await store.dispatch('user/resetToken')
          Message.error(error || 'Has Error')
          next(`/login?redirect=${to.path}`)
          NProgress.done()
        }
      }
    }
  } else {
    /* has no token*/

    if (whiteList.indexOf(to.path) !== -1) {
      // in the free login whitelist, go directly
      next()
    } else {
      // other pages that do not have permission to access are redirected to the login page.
      next(`/login?redirect=${to.path}`)
      NProgress.done()
    }
  }
})

router.afterEach(() => {
  // finish progress bar
  NProgress.done()
})
// eslint-disable-next-line no-unused-vars
async function getPermissionList() {
  try {
    console.log('开始获取权限列表...')
    const res = await getUserPermissions() // 使用导入的函数
    console.log('获取权限列表结果:', res)
    return res
  } catch (error) {
    console.error('获取权限列表详细错误:', {
      message: error.message,
      stack: error.stack,
      response: error.response
    })
    throw error
  }
}

