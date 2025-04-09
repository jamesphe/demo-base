import { login, logout, getInfo, getTrialStatus } from '@/api/user'
import { getToken, setToken, removeToken } from '@/utils/auth'
import router, { resetRouter } from '@/router'

const state = {
  token: getToken(),
  name: '',
  avatar: '',
  introduction: '',
  roles: [],
  trialStatus: null,
  isTrialUser: false
}

const mutations = {
  SET_TOKEN: (state, token) => {
    state.token = token
  },
  SET_INTRODUCTION: (state, introduction) => {
    state.introduction = introduction
  },
  SET_NAME: (state, name) => {
    state.name = name
  },
  SET_AVATAR: (state, avatar) => {
    state.avatar = avatar
  },
  SET_ROLES: (state, roles) => {
    state.roles = roles
  },
  SET_TRIAL_STATUS(state, status) {
    state.trialStatus = status
  },
  SET_IS_TRIAL_USER(state, isTrialUser) {
    state.isTrialUser = isTrialUser
  }
}

const actions = {
  // login action
  login({ commit, dispatch }, userInfo) {
    return new Promise((resolve, reject) => {
      login(userInfo).then(response => {
        // 添加日志来检查响应
        console.log('Login response:', response)

        // 获取 token（兼容不同的返回格式）
        const token = response.accessToken || response.token || response.data?.token || response.data?.accessToken

        if (!token) {
          reject(new Error('登录失败：未获取到token'))
          return
        }

        // 确保 token 格式正确
        const formattedToken = token.startsWith('Bearer ') ? token : `Bearer ${token}`

        // 存储 token
        commit('SET_TOKEN', formattedToken)
        setToken(formattedToken)

        setTimeout(() => {
          console.log('开始获取用户信息')
          dispatch('getInfo').then(({ roles }) => {
            console.log('获取用户信息成功，开始生成路由')
            // 根据权限生成可访问的路由
            dispatch('permission/generateRoutes', roles, { root: true }).then(() => {
              console.log('路由生成成功')
              resolve()
            }).catch(error => {
              console.error('路由生成失败', error)
              reject(error)
            })
          }).catch(error => {
            console.error('获取用户信息失败', error)
            reject(error)
          })
        }, 100)
      }).catch(error => {
        console.error('登录失败', error)
        reject(error)
      })
    })
  },

  // get user info
  getInfo({ commit, state }) {
    return new Promise((resolve, reject) => {
      getInfo(state.token).then(response => {
        const { data } = response

        if (!data) {
          reject('验证失败，请重新登录')
        }

        const { roles, name, avatar, introduction } = data

        // roles 必须是非空数组
        if (!roles || roles.length <= 0) {
          reject('getInfo: roles must be a non-null array!')
        }

        commit('SET_ROLES', roles)
        commit('SET_NAME', name)
        commit('SET_AVATAR', avatar)
        commit('SET_INTRODUCTION', introduction)
        resolve(data)
      }).catch(error => {
        reject(error)
      })
    })
  },

  // user logout
  logout({ commit, state, dispatch }) {
    return new Promise((resolve, reject) => {
      logout(state.token).then(() => {
        commit('SET_TOKEN', '')
        commit('SET_ROLES', [])
        removeToken()
        resetRouter()

        // reset visited views and cached views
        // to fixed https://github.com/PanJiaChen/vue-element-admin/issues/2485
        dispatch('tagsView/delAllViews', null, { root: true })

        resolve()
      }).catch(error => {
        reject(error)
      })
    })
  },

  // remove token
  resetToken({ commit }) {
    return new Promise(resolve => {
      commit('SET_TOKEN', '')
      commit('SET_ROLES', [])
      removeToken()
      resolve()
    })
  },

  // dynamically modify permissions
  async changeRoles({ commit, dispatch }, role) {
    const token = role + '-token'

    commit('SET_TOKEN', token)
    setToken(token)

    const { roles } = await dispatch('getInfo')

    resetRouter()

    // generate accessible routes map based on roles
    const accessRoutes = await dispatch('permission/generateRoutes', roles, { root: true })
    // dynamically add accessible routes
    router.addRoutes(accessRoutes)

    // reset visited views and cached views
    dispatch('tagsView/delAllViews', null, { root: true })
  },

  register({ commit }, userInfo) {
    const { username, email, password } = userInfo
    return new Promise((resolve, reject) => {
      // 导入 register API 或使用其他方式处理注册
      import('@/api/user').then(({ register }) => {
        register({ username, email, password }).then(response => {
          resolve(response)
        }).catch(error => {
          reject(error)
        })
      })
    })
  },

  // 获取用户试用状态
  getTrialStatus({ commit }) {
    return new Promise((resolve, reject) => {
      getTrialStatus().then(response => {
        const { data } = response
        commit('SET_TRIAL_STATUS', data.status)
        commit('SET_IS_TRIAL_USER', data.status === 'active')
        resolve(data)
      }).catch(error => {
        reject(error)
      })
    })
  }
}

const getters = {
  trialStatus: state => state.trialStatus,
  isTrialUser: state => state.isTrialUser,
  userLoggedIn: state => !!state.token,
  token: state => state.token,
  avatar: state => state.avatar,
  name: state => state.name
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}
