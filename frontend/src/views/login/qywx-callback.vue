<template>
  <div class="qywx-callback-container">
    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span>企业微信登录处理中</span>
      </div>
      <div v-if="loading" class="callback-content">
        <el-progress type="circle" :percentage="percentage" status="success" />
        <p class="message">{{ message }}</p>
      </div>
      <div v-if="error" class="callback-content">
        <i class="el-icon-error error-icon"></i>
        <p class="error-message">{{ errorMessage }}</p>
        <el-button type="primary" @click="goToLogin">返回登录</el-button>
      </div>
    </el-card>
  </div>
</template>

<script>
import { loginWithQyWxCode } from '@/utils/qywx-auth'
import { setToken } from '@/utils/auth'
import { resetRouter } from '@/router'

export default {
  name: 'QyWxCallback',
  data() {
    return {
      loading: true,
      error: false,
      percentage: 0,
      message: '正在处理企业微信登录...',
      errorMessage: '',
      timer: null,
      code: '',
      appid: ''
    }
  },
  created() {
    this.parseQueryParams()
    this.startProgressAnimation()
    this.handleCallback()
  },
  beforeDestroy() {
    if (this.timer) {
      clearInterval(this.timer)
    }
  },
  methods: {
    parseQueryParams() {
      const query = this.$route.query
      this.code = query.code
      this.appid = query.appid
      this.state = query.state
    },
    startProgressAnimation() {
      this.timer = setInterval(() => {
        if (this.percentage < 90) {
          this.percentage += 10
        }
      }, 200)
    },
    completeProgress() {
      this.percentage = 100
      if (this.timer) {
        clearInterval(this.timer)
      }
    },
    async handleCallback() {
      if (!this.code || !this.appid) {
        this.showError('无效的授权参数')
        return
      }

      try {
        const response = await loginWithQyWxCode({
          code: this.code,
          appid: this.appid
        })

        // 处理登录成功
        this.completeProgress()
        this.message = '登录成功，正在跳转...'

        // 保存token并重定向
        const { token, user } = response.data
        setToken(token)
        
        // 重置路由
        resetRouter()

        // 跳转到首页
        setTimeout(() => {
          this.$router.push({ path: '/' })
        }, 1000)
      } catch (error) {
        console.error('企业微信登录失败', error)
        this.showError(error.response?.data?.detail || '登录失败，请重试')
      }
    },
    showError(message) {
      this.loading = false
      this.error = true
      this.errorMessage = message
      if (this.timer) {
        clearInterval(this.timer)
      }
    },
    goToLogin() {
      this.$router.push('/login')
    }
  }
}
</script>

<style lang="scss" scoped>
.qywx-callback-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f0f2f5;

  .box-card {
    width: 400px;
    border-radius: 4px;
  }

  .callback-content {
    padding: 30px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
  }

  .message {
    margin-top: 20px;
    font-size: 16px;
    color: #606266;
  }

  .error-icon {
    font-size: 60px;
    color: #f56c6c;
    margin-bottom: 20px;
  }

  .error-message {
    margin-bottom: 20px;
    font-size: 16px;
    color: #f56c6c;
  }
}
</style> 