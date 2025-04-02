<template>
  <div class="security-settings">
    <el-form label-width="120px">
      <el-form-item label="修改密码">
        <el-button type="primary" @click="showPasswordDialog">修改密码</el-button>
      </el-form-item>

      <el-form-item label="双因素认证">
        <el-switch v-model="twoFactorEnabled" />
      </el-form-item>

      <el-form-item label="登录日志">
        <div class="login-info">
          <p>上次登录时间：{{ user.lastLoginTime }}</p>
          <p>上次登录IP：{{ user.lastLoginIp }}</p>
        </div>
      </el-form-item>
    </el-form>

    <el-dialog title="修改密码" :visible.sync="passwordDialogVisible">
      <el-form :model="passwordForm" label-width="100px">
        <el-form-item label="原密码">
          <el-input v-model="passwordForm.oldPassword" type="password" />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="passwordForm.newPassword" type="password" />
        </el-form-item>
        <el-form-item label="确认密码">
          <el-input v-model="passwordForm.confirmPassword" type="password" />
        </el-form-item>
      </el-form>
      <div slot="footer">
        <el-button @click="passwordDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="changePassword">确认</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
export default {
  name: 'SecuritySettings',
  props: {
    user: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      twoFactorEnabled: false,
      passwordDialogVisible: false,
      passwordForm: {
        oldPassword: '',
        newPassword: '',
        confirmPassword: ''
      }
    }
  },
  methods: {
    showPasswordDialog() {
      this.passwordDialogVisible = true
    },
    changePassword() {
      // 实现密码修改逻辑
      this.$message.success('密码修改成功')
      this.passwordDialogVisible = false
    }
  }
}
</script>
