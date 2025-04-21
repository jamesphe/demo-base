import router from './router'
import store from './store'
import { Message } from 'element-ui'
import NProgress from 'nprogress' // progress bar
import 'nprogress/nprogress.css' // progress bar style
import { getToken } from '@/utils/auth' // get token from cookie
import getPageTitle from '@/utils/get-page-title'
import { getUserPermissions } from '@/api/user' // 导入获取用户权限的API函数

NProgress.configure({ showSpinner: false }) // NProgress Configuration

const whiteList = ['/', '/login', '/register', '/trial-application', '/trial-application/terms', '/trial-application/privacy'] // 无需权限验证的路由路径白名单

router.beforeEach(async(to, from, next) => {
  // 开始进度条
  NProgress.start()

  // 设置页面标题
  document.title = getPageTitle(to.meta.title)

  console.log('全局路由守卫 - 目标路由:', to)
  console.log('全局路由守卫 - 来源路由:', from)
  console.log('全局路由守卫 - 当前路由匹配:', to.matched)

  // 添加更多调试日志
  console.log('当前路由配置:', router.options.routes)
  console.log('动态添加的路由:', store.state.permission.addRoutes)
  console.log('用户角色:', store.getters.roles)

  const hasToken = getToken()

  if (hasToken) {
    if (to.path === '/login') {
      next({ path: '/dashboard' })
      NProgress.done()
    } else {
      const hasRoles = store.getters.roles && store.getters.roles.length > 0
      if (hasRoles) {
        // 检查路由是否存在
        if (to.matched.length === 0) {
          // 如果路由不存在，尝试重新加载动态路由
          try {
            const { roles } = await store.dispatch('user/getInfo')
            const accessRoutes = await store.dispatch('permission/generateRoutes', roles)
            router.addRoutes(accessRoutes)
            next({ ...to, replace: true })
          } catch (error) {
            await store.dispatch('user/resetToken')
            Message.error(error?.message || '获取用户信息失败')
            next(`/login?redirect=${to.path}`)
            NProgress.done()
          }
        } else {
          next()
        }
      } else {
        try {
          const { roles } = await store.dispatch('user/getInfo')
          const accessRoutes = await store.dispatch('permission/generateRoutes', roles)
          router.addRoutes(accessRoutes)
          next({ ...to, replace: true })
        } catch (error) {
          await store.dispatch('user/resetToken')
          Message.error(error?.message || '获取用户信息失败')
          next(`/login?redirect=${to.path}`)
          NProgress.done()
        }
      }
    }
  } else {
    if (whiteList.indexOf(to.path) !== -1) {
      next()
    } else {
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

export default router

