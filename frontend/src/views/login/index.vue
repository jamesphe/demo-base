<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-left">
        <div class="login-banner">
          <h2 class="platform-name">企业招聘管理系统</h2>
          <p class="platform-slogan">高效、智能的一站式招聘解决方案</p>
          <div class="platform-features">
            <div class="feature-item">
              <svg-icon icon-class="chart" class="feature-icon" />
              <span>数据分析</span>
            </div>
            <div class="feature-item">
              <svg-icon icon-class="peoples" class="feature-icon" />
              <span>人才管理</span>
            </div>
            <div class="feature-item">
              <svg-icon icon-class="message" class="feature-icon" />
              <span>沟通协作</span>
            </div>
          </div>
          <div class="platform-image">
            <img src="@/assets/login-illustration.svg" alt="登录插图">
          </div>
        </div>
      </div>

      <div class="login-right">
        <div class="login-form-container">
          <div class="login-header">
            <h3 class="welcome-text">欢迎回来</h3>
            <p class="login-tip">请登录您的账号继续使用</p>
          </div>

          <el-form ref="loginForm" :model="loginForm" :rules="loginRules" class="login-form" autocomplete="on" label-position="left">
            <el-form-item prop="username">
              <el-input
                ref="username"
                v-model="loginForm.username"
                placeholder="用户名/邮箱"
                name="username"
                type="text"
                prefix-icon="el-icon-user"
                autocomplete="on"
              />
            </el-form-item>

            <el-form-item prop="password">
              <el-input
                ref="password"
                v-model="loginForm.password"
                :type="passwordType"
                placeholder="密码"
                name="password"
                prefix-icon="el-icon-lock"
                autocomplete="on"
                @keyup.enter.native="handleLogin"
              />
              <span class="show-pwd" @click="showPwd">
                <svg-icon :icon-class="passwordType === 'password' ? 'eye' : 'eye-open'" />
              </span>
            </el-form-item>

            <div class="login-options">
              <el-checkbox v-model="rememberMe">记住我</el-checkbox>
              <a href="#" class="forget-password">忘记密码?</a>
            </div>

            <el-button
              :loading="loading"
              type="primary"
              style="width: 100%; margin-bottom: 30px"
              @click.native.prevent="handleLogin"
            >
              {{ $t('login.logIn') }}
            </el-button>

            <!-- 企业微信登录按钮 -->
            <el-button
              type="primary"
              style="width: 100%; margin-bottom: 30px; background-color: #2e75b5;"
              @click.native.prevent="handleQyWxLogin"
            >
              <img src="@/assets/qywx-logo.svg" alt="企业微信" style="width: 20px; margin-right: 8px; vertical-align: middle;">
              企业微信登录
            </el-button>

            <div class="other-login-methods">
              <div class="divider">
                <span>或使用以下方式登录</span>
              </div>
              <div class="social-login">
                <div class="social-icon" @click="socialLogin('wechat')">
                  <svg-icon icon-class="wechat" />
                </div>
                <div class="social-icon" @click="socialLogin('qq')">
                  <svg-icon icon-class="qq" />
                </div>
                <div class="social-icon" @click="socialLogin('dingtalk')">
                  <svg-icon icon-class="international" />
                </div>
              </div>
            </div>

            <div class="register-link">
              <span>还没有账号?</span>
              <a href="#">立即注册</a>
            </div>
          </el-form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { validUsername } from '@/utils/validate'
import LangSelect from '@/components/LangSelect'
import SocialSign from './components/SocialSignin'
import { getQyWxAuthUrl } from '@/utils/qywx-auth'

export default {
  name: 'Login',
  components: { LangSelect, SocialSign },
  data() {
    const validateUsername = (rule, value, callback) => {
      if (!validUsername(value)) {
        callback(new Error('请输入正确的用户名'))
      } else {
        callback()
      }
    }
    const validatePassword = (rule, value, callback) => {
      if (value.length < 6) {
        callback(new Error('密码不能少于6位'))
      } else {
        callback()
      }
    }
    return {
      loginForm: {
        username: '',
        password: ''
      },
      loginRules: {
        username: [{ required: true, trigger: 'blur', validator: validateUsername }],
        password: [{ required: true, trigger: 'blur', validator: validatePassword }]
      },
      passwordType: 'password',
      loading: false,
      showDialog: false,
      redirect: undefined,
      otherQuery: {},
      rememberMe: false
    }
  },
  watch: {
    $route: {
      handler: function(route) {
        const query = route.query
        if (query) {
          this.redirect = query.redirect
          this.otherQuery = this.getOtherQuery(query)
        }
      },
      immediate: true
    }
  },
  mounted() {
    if (this.loginForm.username === '') {
      this.$refs.username.focus()
    } else if (this.loginForm.password === '') {
      this.$refs.password.focus()
    }
  },
  methods: {
    showPwd() {
      if (this.passwordType === 'password') {
        this.passwordType = ''
      } else {
        this.passwordType = 'password'
      }
      this.$nextTick(() => {
        this.$refs.password.focus()
      })
    },
    handleLogin() {
      this.$refs.loginForm.validate(async valid => {
        if (valid) {
          try {
            await this.$store.dispatch('user/login', this.loginForm)
            // 登录成功后跳转到 dashboard
            this.$router.push('/dashboard')
          } catch (error) {
            console.error('登录失败:', error)
          }
        }
      })
    },
    getOtherQuery(query) {
      return Object.keys(query).reduce((acc, cur) => {
        if (cur !== 'redirect') {
          acc[cur] = query[cur]
        }
        return acc
      }, {})
    },
    socialLogin(type) {
      this.$message.info(`${type}登录功能正在开发中`)
    },
    // 企业微信登录
    async handleQyWxLogin() {
      try {
        // 加载中状态
        this.loading = true;
        
        // 从后端获取企业微信登录URL
        const { data } = await getQyWxAuthUrl();
        
        if (data.auth_url) {
          // 跳转到企业微信授权页面
          window.location.href = data.auth_url;
        } else {
          this.$message.error('获取企业微信登录链接失败');
          this.loading = false;
        }
      } catch (error) {
        console.error('企业微信登录错误:', error);
        this.$message.error('企业微信登录失败');
        this.loading = false;
      }
    }
  }
}
</script>

<style lang="scss">
/* 全局样式 */
$bg-color: #f5f7fa;
$primary-color: #1890ff;
$text-color: #333;
$light-text: #909399;
$border-color: #e4e7ed;
$card-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);

body {
  margin: 0;
  padding: 0;
  height: 100%;
  -moz-osx-font-smoothing: grayscale;
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
  font-family: "Helvetica Neue", Helvetica, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", Arial, sans-serif;
}

/* 登录页样式 */
.login-container {
  height: 100vh;
  width: 100%;
  background-color: $bg-color;
  overflow: hidden;
  display: flex;
  justify-content: center;
  align-items: center;

  .login-box {
    width: 1000px;
    height: 600px;
    display: flex;
    border-radius: 8px;
    box-shadow: $card-shadow;
    overflow: hidden;
  }

  .login-left {
    flex: 1;
    background: linear-gradient(135deg, #1890ff 0%, #36cfc9 100%);
    color: white;
    padding: 40px;
    position: relative;
    overflow: hidden;

    .login-banner {
      height: 100%;
      display: flex;
      flex-direction: column;
      justify-content: flex-start;
      z-index: 1;
      position: relative;
    }

    .platform-name {
      font-size: 28px;
      font-weight: bold;
      margin-bottom: 10px;
    }

    .platform-slogan {
      font-size: 16px;
      margin-bottom: 40px;
      opacity: 0.9;
    }

    .platform-features {
      display: flex;
      flex-wrap: wrap;
      margin-bottom: 40px;

      .feature-item {
        display: flex;
        align-items: center;
        margin-right: 20px;
        margin-bottom: 15px;

        .feature-icon {
          font-size: 18px;
          margin-right: 8px;
        }
      }
    }

    .platform-image {
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;

      img {
        max-width: 100%;
        max-height: 250px;
      }
    }
  }

  .login-right {
    width: 450px;
    background-color: white;
    padding: 40px;
    display: flex;
    flex-direction: column;
    justify-content: center;

    .login-form-container {
      width: 100%;
    }

    .login-header {
      text-align: center;
      margin-bottom: 40px;

      .welcome-text {
        font-size: 24px;
        color: $text-color;
        margin-bottom: 10px;
      }

      .login-tip {
        font-size: 14px;
        color: $light-text;
        margin: 0;
      }
    }

    .login-form {
      .el-form-item {
        margin-bottom: 25px;
      }

      .el-input {
        height: 40px;

        input {
          height: 40px;
          padding-left: 40px !important;
          background-color: #f5f7fa;
          border: 1px solid #e4e7ed;
          border-radius: 4px;
          transition: all 0.3s;

          &:hover {
            border-color: #c0c4cc;
          }

          &:focus {
            border-color: $primary-color;
            background-color: white;
            box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.1);
          }
        }
      }

      .el-input__prefix {
        left: 12px;
        height: 40px;
        line-height: 40px;

        .el-input__icon {
          line-height: 40px;
          color: #909399;
        }
      }

      .show-pwd {
        position: absolute;
        right: 10px;
        top: 0;
        font-size: 16px;
        color: #909399;
        cursor: pointer;
        height: 40px;
        display: flex;
        align-items: center;
        transition: all 0.3s;

        &:hover {
          color: $primary-color;
        }
      }
    }

    .login-options {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 25px;

      .forget-password {
        color: $primary-color;
        font-size: 14px;
        text-decoration: none;

        &:hover {
          text-decoration: underline;
        }
      }
    }

    .login-button {
      width: 100%;
      height: 40px;
      border-radius: 4px;
      font-size: 16px;
      font-weight: 500;
      margin-bottom: 25px;
    }

    .other-login-methods {
      margin-bottom: 25px;

      .divider {
        display: flex;
        align-items: center;
        color: $light-text;
        font-size: 14px;
        margin: 20px 0;

        &:before,
        &:after {
          content: "";
          flex: 1;
          border-top: 1px solid $border-color;
        }

        span {
          padding: 0 10px;
        }
      }

      .social-login {
        display: flex;
        justify-content: center;

        .social-icon {
          width: 40px;
          height: 40px;
          border-radius: 50%;
          background-color: #f5f7fa;
          display: flex;
          align-items: center;
          justify-content: center;
          margin: 0 10px;
          cursor: pointer;
          transition: all 0.3s;

          &:hover {
            background-color: #e6f7ff;
            color: $primary-color;
          }

          svg {
            font-size: 20px;
          }
        }
      }
    }

    .register-link {
      text-align: center;
      font-size: 14px;
      color: $light-text;

      a {
        color: $primary-color;
        text-decoration: none;
        margin-left: 5px;

        &:hover {
          text-decoration: underline;
        }
      }
    }
  }
}

@media (max-width: 1000px) {
  .login-container {
    .login-box {
      width: 90%;
      height: auto;
      flex-direction: column;
    }

    .login-left {
      display: none;
    }

    .login-right {
      width: auto;
      padding: 30px;
    }
  }
}
</style>
