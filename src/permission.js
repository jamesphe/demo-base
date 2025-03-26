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
  // 开始进度条
  NProgress.start()

  // 设置页面标题
  document.title = getPageTitle(to.meta.title)

  try {
    // 如果是白名单中的路径，直接放行，不获取用户信息
    if (whiteList.includes(to.path)) {
      next()
      NProgress.done()
      return
    }

    const hasToken = getToken()

    if (hasToken) {
      if (to.path === '/login') {
        next({ path: '/dashboard' })
      } else {
        const hasGetUserInfo = store.getters.name
        if (hasGetUserInfo) {
          next()
        } else {
          try {
            // 只有在需要时才获取用户信息
            await store.dispatch('user/getInfo')
            await store.dispatch('user/getTrialStatus')
            next()
          } catch (error) {
            await store.dispatch('user/resetToken')
            Message.error(error || 'Has Error')
            next('/login')
          }
        }
      }
    } else {
      if (to.meta.requiresAuth) {
        next('/login')
      } else {
        next()
      }
    }
  } catch (error) {
    console.error('路由守卫错误:', error)
    next('/login')
  } finally {
    NProgress.done()
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

