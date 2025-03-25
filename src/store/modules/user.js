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
  // user login
  login({ commit, dispatch }, userInfo) {
    const { username, password } = userInfo
    return new Promise((resolve, reject) => {
      login({ username: username.trim(), password: password })
        .then(response => {
          const { access_token } = response
          commit('SET_TOKEN', access_token)
          setToken(access_token)
          dispatch('getInfo')
          dispatch('getTrialStatus')
          resolve()
        })
        .catch(error => {
          reject(error)
        })
    })
  },

  // get user info
  getInfo({ commit, state }) {
    return new Promise((resolve, reject) => {
      getInfo()
        .then(response => {
          const { data } = response

          if (!data) {
            reject('Verification failed, please Login again.')
          }

          const { roles, name, avatar, introduction } = data

          // roles must be a non-empty array
          if (!roles || roles.length <= 0) {
            reject('getInfo: roles must be a non-null array!')
          }

          commit('SET_ROLES', roles)
          commit('SET_NAME', name)
          commit('SET_AVATAR', avatar)
          commit('SET_INTRODUCTION', introduction)
          resolve(data)
        })
        .catch(error => {
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
  userLoggedIn: state => !!state.token
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}
