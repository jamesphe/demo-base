<template>
  <el-card class="system-info-card">
    <div slot="header" class="clearfix">
      <span>系统信息</span>
    </div>
    <div class="info-item">
      <span class="label">系统版本：</span>
      <span class="value">v{{ version }}</span>
    </div>
    <div class="info-item">
      <span class="label">服务器状态：</span>
      <span class="value">
        <el-tag :type="serverStatus === 'normal' ? 'success' : 'danger'">
          {{ serverStatus === 'normal' ? '正常' : '异常' }}
        </el-tag>
      </span>
    </div>
    <div class="info-item">
      <span class="label">CPU使用率：</span>
      <el-progress :percentage="cpuUsage" :color="cpuUsage > 80 ? '#F56C6C' : '#67C23A'"></el-progress>
    </div>
    <div class="info-item">
      <span class="label">内存使用率：</span>
      <el-progress :percentage="memoryUsage" :color="memoryUsage > 80 ? '#F56C6C' : '#67C23A'"></el-progress>
    </div>
  </el-card>
</template>

<script>
export default {
  name: 'SystemInfo',
  data() {
    return {
      version: '1.0.0',
      serverStatus: 'normal',
      cpuUsage: 45,
      memoryUsage: 60
    }
  }
}
</script>

<style scoped>
.system-info-card {
  margin-bottom: 20px;
}
.info-item {
  margin-bottom: 15px;
}
.label {
  font-weight: bold;
  margin-right: 10px;
}
</style> 