<template>
  <div class="dashboard-admin" @wheel.passive="handleScroll">
    <!-- 顶部统计卡片 -->
    <panel-group @handleSetLineChartData="handleSetLineChartData" />

    <!-- 第一行：租户概览 -->
    <el-row :gutter="24" class="chart-row">
      <el-col :xs="24" :sm="24" :lg="16">
        <div class="chart-wrapper">
          <line-chart
            :chart-data="lineChartData"
            title="租户增长趋势"
          />
        </div>
      </el-col>
      <el-col :xs="24" :sm="24" :lg="8">
        <div class="chart-wrapper">
          <pie-chart title="租户类型分布" />
        </div>
      </el-col>
    </el-row>

    <!-- 第二行：租户管理 -->
    <el-row :gutter="24" class="content-row">
      <el-col :xs="24" :sm="24" :lg="12">
        <tenant-overview />
      </el-col>
      <el-col :xs="24" :sm="24" :lg="12">
        <trial-management />
      </el-col>
    </el-row>

    <!-- 第三行：系统监控 -->
    <el-row :gutter="24" class="content-row">
      <el-col :xs="24" :sm="24" :lg="12">
        <system-info />
      </el-col>
      <el-col :xs="24" :sm="24" :lg="12">
        <alert-list />
      </el-col>
    </el-row>
  </div>
</template>

<script>
import PanelGroup from './components/PanelGroup'
import LineChart from './components/LineChart'
import PieChart from './components/PieChart'
import TenantOverview from './components/TenantOverview'
import TrialManagement from './components/TrialManagement'
import SystemInfo from './components/SystemInfo'
import AlertList from './components/AlertList'

const lineChartData = {
  tenantGrowth: {
    expectedData: [100, 120, 161, 134, 105, 160, 165],
    actualData: [120, 82, 91, 154, 162, 140, 145],
    xAxisData: ['1月', '2月', '3月', '4月', '5月', '6月', '7月']
  },
  trialConversion: {
    expectedData: [80, 100, 121, 104, 105, 90, 100],
    actualData: [70, 90, 110, 95, 100, 85, 95],
    xAxisData: ['1月', '2月', '3月', '4月', '5月', '6月', '7月']
  }
}

export default {
  name: 'AdminDashboard',
  components: {
    PanelGroup,
    LineChart,
    PieChart,
    TenantOverview,
    TrialManagement,
    SystemInfo,
    AlertList
  },
  data() {
    return {
      lineChartData: lineChartData.tenantGrowth,
      msgConfig: {
        isVisible: false,
        msgType: 'info',
        content: '',
        closable: true,
        isCentered: false,
        className: '',
        icon: '',
        useHTML: false
      }
    }
  },
  watch: {
    '$route'(to, from) {
      console.log('路由变化:', {
        to: to.path,
        from: from.path
      })
    }
  },
  created() {
    this.initDashboard().catch(error => {
      console.error('Dashboard initialization failed:', error)
      this.$message.error('加载仪表板数据失败')
    })
  },
  mounted() {
    console.log('组件 mounted')
    // 为所有可滚动元素添加 passive 事件监听
    const scrollElements = this.$el.querySelectorAll('.chart-wrapper')
    console.log('找到滚动元素数量:', scrollElements.length)

    scrollElements.forEach(element => {
      element.addEventListener('wheel', () => {
        console.log('wheel event triggered')
      }, { passive: true })
    })
  },
  beforeDestroy() {
    console.log('组件即将销毁')
    const scrollElements = this.$el.querySelectorAll('.chart-wrapper')
    scrollElements.forEach(element => {
      element.removeEventListener('wheel', () => {})
    })
  },
  methods: {
    async initDashboard() {
      try {
        await this.handleSetLineChartData('tenantGrowth')
        console.log('Dashboard initialized successfully')
      } catch (error) {
        throw new Error('Failed to initialize dashboard: ' + error.message)
      }
    },
    handleSetLineChartData(type) {
      console.log('切换图表数据:', type)
      this.lineChartData = lineChartData[type]
    },
    handleScroll(e) {
      console.log('handleScroll triggered', e)
      // wheel事件处理保持不变
    }
  }
}
</script>

<style lang="scss" scoped>
.dashboard-admin {
  padding: 24px;
  background-color: #f0f2f5;

  .chart-row {
    margin-bottom: 24px;
  }

  .content-row {
    margin-bottom: 24px;
  }

  .chart-wrapper {
    background: #fff;
    padding: 16px;
    border-radius: 4px;
    box-shadow: 0 1px 4px rgba(0,21,41,.08);
    margin-bottom: 24px;
  }

  .right-panel {
    .chart-wrapper {
      margin-top: 24px;
    }
  }
}

@media (max-width:1024px) {
  .dashboard-admin {
    padding: 12px;
  }

  .chart-wrapper {
    padding: 12px;
    margin-bottom: 12px;
  }
}
</style>
