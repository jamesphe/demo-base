<template>
  <div class="basic-info">
    <el-form label-width="120px">
      <el-form-item label="用户名">
        <el-input v-model="userInfo.username" disabled />
      </el-form-item>

      <el-form-item label="部门">
        <el-input v-model="userInfo.department" />
      </el-form-item>

      <el-form-item label="职位">
        <el-input v-model="userInfo.position" />
      </el-form-item>

      <el-form-item label="手机号码">
        <el-input v-model="userInfo.phone" />
      </el-form-item>

      <el-form-item label="邮箱">
        <el-input v-model="userInfo.email" />
      </el-form-item>

      <el-form-item>
        <el-button type="primary" @click="updateInfo">保存修改</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script>
export default {
  name: 'BasicInfo',
  props: {
    user: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      userInfo: { ...this.user }
    }
  },
  methods: {
    updateInfo() {
      // 实现更新用户信息的逻辑
      this.$message.success('信息更新成功')
    }
  }
}
</script>
