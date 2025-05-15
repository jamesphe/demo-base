const getters = {
  sidebar: state => state.app.sidebar,
  size: state => state.app.size,
  device: state => state.app.device,
  visitedViews: state => state.tagsView.visitedViews,
  cachedViews: state => state.tagsView.cachedViews,
  token: state => state.user.token,
  avatar: state => state.user.avatar,
  name: state => state.user.name,
  introduction: state => state.user.introduction,
  roles: state => state.user.roles,
  permission_routes: state => state.permission.routes,
  errorLogs: state => state.errorLog.logs,
  routes: state => state.permission.routes,
  positionList: state => state.position.list,
  positionTotal: state => state.position.total,
  positionLoading: state => state.position.loading,
  currentPosition: state => state.position.currentPosition,
  isSuperuser: state => state.user.isSuperuser,
  user_id: state => state.user.id || '',
  currentUser: state => ({
    id: state.user.id || '',
    name: state.user.name || '',
    username: state.user.username || '',
    avatar: state.user.avatar || ''
  })
}
export default getters
