<template>
  <div class="app-container">
    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span>ComponentTitle</span>
      </div>
      <div class="content">
        // 页面内容
      </div>
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'ComponentName',
  data() {
    return {}
  },
  methods: {}
}
</script>

<style lang="scss" scoped>
.app-container {
  padding: 20px;
}
</style>
