import { asyncRoutes, constantRoutes } from '@/router'

/**
 * Use meta.role to determine if the current user has permission
 * @param roles
 * @param route
 */
function hasPermission(roles, route) {
  //console.log('Checking permission for route:', route.path, 'roles:', roles)
  if (route.meta && route.meta.roles) {
    const hasRole = roles.some(role => route.meta.roles.includes(role))
    //console.log('Route requires roles:', route.meta.roles, 'Has permission:', hasRole)
    return hasRole
  } else {
    //console.log('Route has no role requirements')
    return true
  }
}

/**
 * Filter asynchronous routing tables by recursion
 * @param routes asyncRoutes
 * @param roles
 */
export function filterAsyncRoutes(routes, roles) {
  const res = []

  routes.forEach(route => {
    const tmp = { ...route }
    if (hasPermission(roles, tmp)) {
      if (tmp.children) {
        tmp.children = filterAsyncRoutes(tmp.children, roles)
      }
      res.push(tmp)
    }
  })

  return res
}

const state = {
  routes: [],
  addRoutes: []
}

const mutations = {
  SET_ROUTES: (state, routes) => {
    state.addRoutes = routes
    state.routes = constantRoutes.concat(routes)
  }
}

const actions = {
  generateRoutes({ commit }, roles) {
    return new Promise(resolve => {
      let accessedRoutes
      if (roles.includes('admin')) {
        accessedRoutes = asyncRoutes || []
      } else {
        accessedRoutes = filterAsyncRoutes(asyncRoutes, roles)
      }

      // 确保路由配置正确
      accessedRoutes = accessedRoutes.map(route => {
        const tmp = { ...route }
        if (tmp.children) {
          tmp.children = tmp.children.map(child => ({
            ...child,
            meta: {
              ...child.meta,
              roles: child.meta?.roles || tmp.meta?.roles || []
            }
          }))
        }
        return tmp
      })

      commit('SET_ROUTES', accessedRoutes)
      resolve(accessedRoutes)
    })
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions
}
