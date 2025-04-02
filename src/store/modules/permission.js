import { asyncRoutes, constantRoutes } from '@/router'

/**
 * Use meta.role to determine if the current user has permission
 * @param roles
 * @param route
 */
function hasPermission(roles, route) {
  console.log('Checking permission for route:', route.path, 'roles:', roles)
  if (route.meta && route.meta.roles) {
    const hasRole = roles.some(role => route.meta.roles.includes(role))
    console.log('Route requires roles:', route.meta.roles, 'Has permission:', hasRole)
    return hasRole
  } else {
    console.log('Route has no role requirements')
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
      console.log('generateRoutes action called with roles:', roles)
      let accessedRoutes
      if (roles.includes('admin')) {
        console.log('User is admin, getting all routes')
        accessedRoutes = asyncRoutes || []
      } else {
        console.log('Filtering routes for roles:', roles)
        accessedRoutes = filterAsyncRoutes(asyncRoutes, roles)
      }
      console.log('Final accessed routes:', accessedRoutes)
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
