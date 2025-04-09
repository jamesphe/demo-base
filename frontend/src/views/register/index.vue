<template>
  <div class="register-container">
    <el-form
      ref="registerForm"
      :model="registerForm"
      :rules="registerRules"
      class="register-form"
      label-position="left"
    >
      <div class="title-container">
        <h3 class="title">注册账号</h3>
      </div>

      <el-form-item prop="username">
        <el-input
          ref="username"
          v-model="registerForm.username"
          placeholder="用户名"
          name="username"
          type="text"
          prefix-icon="el-icon-user"
        />
      </el-form-item>

      <el-form-item prop="email">
        <el-input
          ref="email"
          v-model="registerForm.email"
          placeholder="邮箱"
          name="email"
          type="email"
          prefix-icon="el-icon-message"
        />
      </el-form-item>

      <el-form-item prop="password">
        <el-input
          ref="password"
          v-model="registerForm.password"
          placeholder="密码"
          name="password"
          :type="passwordType"
          prefix-icon="el-icon-lock"
        />
        <span class="show-pwd" @click="showPwd">
          <i :class="passwordType === 'password' ? 'el-icon-view' : 'el-icon-view'" />
        </span>
      </el-form-item>

      <el-form-item prop="confirmPassword">
        <el-input
          ref="confirmPassword"
          v-model="registerForm.confirmPassword"
          placeholder="确认密码"
          name="confirmPassword"
          :type="passwordType"
          prefix-icon="el-icon-lock"
        />
      </el-form-item>

      <el-button
        :loading="loading"
        type="primary"
        style="width: 100%; margin-bottom: 30px"
        @click.native.prevent="handleRegister"
      >
        注册
      </el-button>

      <div class="tips">
        <span>已有账号? </span>
        <router-link to="/login">立即登录</router-link>
      </div>
    </el-form>
  </div>
</template>

<script>
export default {
  name: 'Register',
  data() {
    // 确认密码的验证规则
    const validateConfirmPassword = (rule, value, callback) => {
      if (value !== this.registerForm.password) {
        callback(new Error('两次输入的密码不一致'))
      } else {
        callback()
      }
    }
    return {
      registerForm: {
        username: '',
        email: '',
        password: '',
        confirmPassword: ''
      },
      registerRules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' },
          { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
        ],
        email: [
          { required: true, message: '请输入邮箱地址', trigger: 'blur' },
          { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' },
          { min: 6, message: '密码长度至少为 6 个字符', trigger: 'blur' }
        ],
        confirmPassword: [
          { required: true, message: '请再次输入密码', trigger: 'blur' },
          { validator: validateConfirmPassword, trigger: 'blur' }
        ]
      },
      loading: false,
      passwordType: 'password'
    }
  },
  methods: {
    showPwd() {
      this.passwordType = this.passwordType === 'password' ? '' : 'password'
      this.$nextTick(() => {
        this.$refs.password.focus()
      })
    },
    handleRegister() {
      this.$refs.registerForm.validate(async valid => {
        if (valid) {
          this.loading = true
          try {
            // 调用注册 API
            await this.$store.dispatch('user/register', this.registerForm)
            this.$message.success('注册成功')
            this.$router.push('/login')
          } catch (error) {
            console.error('注册失败:', error)
            this.$message.error(error.message || '注册失败，请重试')
          } finally {
            this.loading = false
          }
        }
      })
    }
  }
}
</script>

<style lang="scss" scoped>
$bg: #2d3a4b;
$dark_gray: #889aa4;
$light_gray: #eee;

.register-container {
  min-height: 100vh;
  width: 100%;
  background-color: $bg;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;

  .register-form {
    position: relative;
    width: 420px;
    max-width: 100%;
    padding: 35px;
    margin: 0 auto;
    overflow: hidden;
    background: #fff;
    border-radius: 6px;
  }

  .title-container {
    position: relative;
    .title {
      font-size: 26px;
      color: #333;
      margin: 0 auto 40px auto;
      text-align: center;
      font-weight: bold;
    }
  }

  .show-pwd {
    position: absolute;
    right: 10px;
    top: 7px;
    font-size: 16px;
    color: $dark_gray;
    cursor: pointer;
    user-select: none;
  }

  .tips {
    font-size: 14px;
    color: #666;
    text-align: center;

    a {
      color: #1890ff;
      text-decoration: none;

      &:hover {
        text-decoration: underline;
      }
    }
  }
}

.el-form-item {
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(0, 0, 0, 0.1);
  border-radius: 5px;
  color: #454545;
}
</style>
