<template>
  <el-card class="alert-list">
    <div slot="header" class="clearfix">
      <span>系统告警</span>
      <el-button style="float: right; padding: 3px 0" type="text" @click="refreshAlerts">
        刷新
      </el-button>
    </div>

    <el-table
      v-loading="loading"
      :data="alerts"
      style="width: 100%"
      :header-cell-style="{background:'#f5f7fa'}"
    >
      <el-table-column
        prop="level"
        label="级别"
        width="100"
      >
        <template slot-scope="{row}">
          <el-tag :type="getAlertLevelType(row.level)">
            {{ row.level }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column
        prop="title"
        label="告警内容"
      />

      <el-table-column
        prop="time"
        label="时间"
        width="180"
      />

      <el-table-column
        label="操作"
        width="120"
        align="center"
      >
        <template slot-scope="{row}">
          <el-button
            size="mini"
            type="text"
            @click="handleAlert(row)"
          >
            处理
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<script>
export default {
  name: 'AlertList',
  data() {
    return {
      loading: false,
      alerts: [
        {
          level: '严重',
          title: '数据库连接池使用率超过90%',
          time: '2024-03-21 10:23:45'
        },
        {
          level: '警告',
          title: '系统存储空间使用率达到85%',
          time: '2024-03-21 09:15:30'
        },
        {
          level: '提示',
          title: '新增异常登录尝试',
          time: '2024-03-21 08:45:12'
        }
      ]
    }
  },
  methods: {
    getAlertLevelType(level) {
      const typeMap = {
        '严重': 'danger',
        '警告': 'warning',
        '提示': 'info'
      }
      return typeMap[level]
    },
    refreshAlerts() {
      this.loading = true
      setTimeout(() => {
        this.loading = false
      }, 800)
    },
    handleAlert(alert) {
      this.$message.info(`处理告警: ${alert.title}`)
    }
  }
}
</script>

<style lang="scss" scoped>
.alert-list {
  .el-card__header {
    padding: 12px 20px;
    border-bottom: 1px solid #ebeef5;
  }
}
</style>
