import {
  fetchList,
  createEmail,
  updateEmail,
  deleteEmail,
  triggerSync,
  testConnection
} from '@/api/resume-sync-email'

const state = {
  emailList: [],
  loading: false,
  pagination: {
    total: 0,
    page: 1,
    per_page: 10,
    total_pages: 0
  },
  currentEmail: null
}

const mutations = {
  SET_LOADING: (state, status) => {
    state.loading = status
  },
  SET_EMAIL_LIST: (state, { list, pagination }) => {
    state.emailList = list
    if (pagination) {
      state.pagination = pagination
    }
  },
  SET_PAGINATION: (state, pagination) => {
    state.pagination = pagination
  },
  SET_CURRENT_EMAIL: (state, email) => {
    state.currentEmail = email
  },
  ADD_EMAIL: (state, email) => {
    state.emailList.push(email)
  },
  UPDATE_EMAIL: (state, updatedEmail) => {
    const index = state.emailList.findIndex(item => item.id === updatedEmail.id)
    if (index !== -1) {
      state.emailList.splice(index, 1, updatedEmail)
    }
  },
  REMOVE_EMAIL: (state, id) => {
    const index = state.emailList.findIndex(item => item.id === id)
    if (index !== -1) {
      state.emailList.splice(index, 1)
    }
  }
}

const actions = {
  // 获取邮箱列表
  async getEmailList({ commit }, { page = 1, per_page = 10 }) {
    commit('SET_LOADING', true)
    try {
      const response = await fetchList({ page, per_page })
      console.log('API原始返回数据:', response)
      
      let dataArray = []
      let paginationInfo = null
      
      // 处理可能的不同响应格式
      if (response && response.data) {
        dataArray = response.data
        paginationInfo = response.meta
      } else if (Array.isArray(response)) {
        dataArray = response
      }
      
      // 调试输出第一条记录
      if (dataArray.length > 0) {
        console.log('第一条原始数据:', dataArray[0])
      }
      
      // 解析数据列表，确保各字段存在
      const list = dataArray.map(item => {
        // 调试原始字段名
        console.log('检查字段名:', Object.keys(item));
        
        // 确保端口是数字
        const imapPort = parseInt(item.imap_port || item.imapPort || 993, 10)
        const smtpPort = parseInt(item.smtp_port || item.smtpPort || 465, 10)
        
        // 处理服务器地址，注意可能的字段名差异
        const imapServer = item.imap_server || item.imapServer || '';
        const smtpServer = item.smtp_server || item.smtpServer || '';
        
        console.log('解析后的服务器和端口:', { 
          imapServer, 
          imapPort, 
          smtpServer, 
          smtpPort 
        });
        
        return {
          id: item.id,
          email: item.email || '',
          imap_server: imapServer,
          imap_port: isNaN(imapPort) ? 993 : imapPort,
          smtp_server: smtpServer,
          smtp_port: isNaN(smtpPort) ? 465 : smtpPort,
          is_active: !!item.is_active || !!item.isActive,
          sync_interval: parseInt(item.sync_interval || item.syncInterval || 15, 10),
          last_sync_time: item.last_sync_time || item.lastSyncTime,
          description: item.description || ''
        }
      })
      
      // 调试输出第一条处理后的数据
      if (list.length > 0) {
        console.log('第一条处理后数据:', list[0])
      }
      
      // 保存数据和分页信息
      commit('SET_EMAIL_LIST', { 
        list, 
        pagination: paginationInfo 
      })
      
      return response
    } catch (error) {
      console.error('获取邮箱列表失败', error)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // 创建邮箱配置
  async createEmail({ commit }, emailData) {
    try {
      const { data } = await createEmail(emailData)
      commit('ADD_EMAIL', data)
      return data
    } catch (error) {
      console.error('创建邮箱配置失败', error)
      throw error
    }
  },
  
  // 更新邮箱配置
  async updateEmail({ commit }, { id, data }) {
    try {
      const response = await updateEmail(id, data)
      const updatedEmail = { ...data, id }
      commit('UPDATE_EMAIL', updatedEmail)
      return response
    } catch (error) {
      console.error('更新邮箱配置失败', error)
      throw error
    }
  },
  
  // 删除邮箱配置
  async deleteEmail({ commit }, id) {
    try {
      await deleteEmail(id)
      commit('REMOVE_EMAIL', id)
      return true
    } catch (error) {
      console.error('删除邮箱配置失败', error)
      throw error
    }
  },
  
  // 触发手动同步
  async triggerSync({ commit }, id) {
    try {
      return await triggerSync(id)
    } catch (error) {
      console.error('触发同步失败', error)
      throw error
    }
  },
  
  // 测试邮箱连接
  async testConnection({ commit }, testData) {
    try {
      const response = await testConnection(testData)
      
      let success = false
      let message = '未知错误'
      
      if (response) {
        if (response.data) {
          // 标准axios响应格式
          success = response.data.success
          message = response.data.message || '未知错误'
        } else if (response.success !== undefined) {
          // 直接包含success的情况
          success = response.success
          message = response.message || '未知错误'
        }
      }
      
      return { success, message }
    } catch (error) {
      console.error('测试连接失败', error)
      throw error
    }
  }
}

const getters = {
  emailList: state => state.emailList,
  loading: state => state.loading,
  pagination: state => state.pagination
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
} 