<template>
  <el-card class="system-info-card">
    <div slot="header" class="clearfix">
      <span>系统状态</span>
      <el-button style="float: right; padding: 3px 0" type="text" @click="refreshStatus">
        刷新
      </el-button>
    </div>

    <div class="status-overview">
      <div class="status-item">
        <span class="label">运行状态</span>
        <el-tag :type="systemStatus.status === 'normal' ? 'success' : 'danger'">
          {{ systemStatus.status === 'normal' ? '正常' : '异常' }}
        </el-tag>
      </div>

      <div class="status-item">
        <span class="label">运行时间</span>
        <span class="value">{{ systemStatus.uptime }}</span>
      </div>
    </div>

    <div class="resource-usage">
      <div class="usage-item">
        <span class="label">CPU使用率</span>
        <el-progress
          :percentage="systemStatus.cpu"
          :color="getProgressColor(systemStatus.cpu)"
        />
      </div>

      <div class="usage-item">
        <span class="label">内存使用率</span>
        <el-progress
          :percentage="systemStatus.memory"
          :color="getProgressColor(systemStatus.memory)"
        />
      </div>

      <div class="usage-item">
        <span class="label">存储使用率</span>
        <el-progress
          :percentage="systemStatus.storage"
          :color="getProgressColor(systemStatus.storage)"
        />
      </div>
    </div>
  </el-card>
</template>

<script>
export default {
  name: 'SystemInfo',
  data() {
    return {
      systemStatus: {
        status: 'normal',
        uptime: '15天4小时',
        cpu: 45,
        memory: 68,
        storage: 72
      }
    }
  },
  methods: {
    refreshStatus() {
      // 模拟刷新系统状态
    },
    getProgressColor(value) {
      if (value < 70) return '#67C23A'
      if (value < 90) return '#E6A23C'
      return '#F56C6C'
    }
  }
}
</script>

<style lang="scss" scoped>
.system-info-card {
  .status-overview {
    margin-bottom: 20px;

    .status-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;

      .label {
        color: #606266;
      }
    }
  }

  .resource-usage {
    .usage-item {
      margin-bottom: 15px;

      .label {
        display: block;
        margin-bottom: 5px;
        color: #606266;
      }
    }
  }
}
</style>
