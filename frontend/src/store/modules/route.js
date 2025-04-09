const state = {
  currentRoute: '',
  routeName: '',
  hasNavHeader: true
}

const mutations = {
  SET_ROUTE_INFO: (state, routeInfo) => {
    state.currentRoute = routeInfo.currentRoute
    state.routeName = routeInfo.routeName
    state.hasNavHeader = routeInfo.hasNavHeader
  }
}

const actions = {
  // 如果需要异步操作可以添加 actions
}

export default {
  namespaced: true,
  state,
  mutations,
  actions
}
