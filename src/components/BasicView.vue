<template>
  <div class="app-container">
    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span>{{ title }}</span>
      </div>
      <div class="content">
        <slot>该功能正在开发中...</slot>
      </div>
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'BasicView',
  props: {
    title: {
      type: String,
      required: true
    }
  }
}
</script>

<style lang="scss" scoped>
.app-container {
  padding: 20px;
}
</style> 