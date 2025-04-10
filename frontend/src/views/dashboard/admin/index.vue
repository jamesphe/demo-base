<template>
  <div class="admin-dashboard">
    <!-- 顶部数据卡片 -->
    <el-row :gutter="20" class="data-cards">
      <el-col v-for="(item, index) in cardData" :key="index" :span="6">
        <el-card shadow="hover">
          <div class="data-item">
            <div class="data-icon">
              <i :class="item.icon" />
            </div>
            <div class="data-content">
              <div class="data-title">{{ item.title }}</div>
              <div class="data-value">{{ item.value }}</div>
              <div class="data-trend" :class="{ 'up': item.trend > 0, 'down': item.trend < 0 }">
                <span>较上月</span>
                <span>{{ item.trend > 0 ? '+' : '' }}{{ item.trend }}%</span>
                <i :class="item.trend > 0 ? 'el-icon-top' : 'el-icon-bottom'" />
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" class="charts-container">
      <!-- 左侧图表：租户活跃度趋势 -->
      <el-col :span="16">
        <el-card class="chart-card" shadow="hover">
          <div slot="header">
            <span>租户活跃度趋势</span>
            <el-radio-group v-model="timeRange" size="small" style="float: right">
              <el-radio-button label="week">本周</el-radio-button>
              <el-radio-button label="month">本月</el-radio-button>
              <el-radio-button label="quarter">本季度</el-radio-button>
            </el-radio-group>
          </div>
          <div class="chart-container">
            <v-chart class="chart" :options="activityTrendChart" autoresize />
          </div>
        </el-card>
      </el-col>

      <!-- 右侧图表：人才分布 -->
      <el-col :span="8">
        <el-card class="chart-card" shadow="hover">
          <div slot="header">
            <span>人才分布</span>
            <el-select v-model="distributionType" size="small" style="float: right; width: 120px">
              <el-option label="工种分布" value="jobType" />
              <el-option label="地区分布" value="location" />
              <el-option label="年龄分布" value="age" />
            </el-select>
          </div>
          <div class="chart-container">
            <v-chart class="chart" :options="talentDistributionChart" autoresize />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 下方图表和表格 -->
    <el-row :gutter="20" class="bottom-container">
      <!-- 左侧：招聘效果分析 -->
      <el-col :span="12">
        <el-card class="chart-card" shadow="hover">
          <div slot="header">
            <span>招聘效果分析</span>
            <el-tooltip content="展示各工种的招聘转化率" placement="top">
              <i class="el-icon-info" style="margin-left: 8px" />
            </el-tooltip>
          </div>
          <div class="chart-container">
            <v-chart class="chart" :options="recruitmentChart" autoresize />
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：租户运营状况 -->
      <el-col :span="12">
        <el-card shadow="hover">
          <div slot="header">
            <span>租户运营状况</span>
            <el-button style="float: right" type="text" @click="refreshTenantData">
              <i class="el-icon-refresh" /> 刷新
            </el-button>
          </div>
          <el-table :data="tenantOperationData" style="width: 100%" :max-height="400">
            <el-table-column prop="tenantName" label="租户名称" width="180" />
            <el-table-column prop="activeUsers" label="活跃用户" width="100" align="center" />
            <el-table-column prop="totalJobs" label="发布职位" width="100" align="center" />
            <el-table-column prop="totalApplications" label="收到简历" width="100" align="center" />
            <el-table-column prop="conversionRate" label="转化率" align="center">
              <template slot-scope="scope">
                <el-progress
                  :percentage="scope.row.conversionRate"
                  :color="getConversionColor(scope.row.conversionRate)"
                />
              </template>
            </el-table-column>
            <el-table-column label="状态" width="100" align="center">
              <template slot-scope="scope">
                <el-tag :type="getStatusType(scope.row.status)">{{ scope.row.status }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import ECharts from 'vue-echarts'
import 'echarts/lib/chart/line'
import 'echarts/lib/chart/pie'
import 'echarts/lib/chart/bar'
import 'echarts/lib/component/tooltip'
import 'echarts/lib/component/title'
import 'echarts/lib/component/legend'
import 'echarts/lib/component/grid'

export default {
  name: 'AdminDashboard',
  components: {
    'v-chart': ECharts
  },
  data() {
    return {
      timeRange: 'month',
      distributionType: 'jobType',
      loading: false,
      cardData: [
        {
          title: '总租户数',
          value: '89',
          trend: 15,
          icon: 'el-icon-office-building'
        },
        {
          title: '总人才数',
          value: '13,600',
          trend: 8,
          icon: 'el-icon-user'
        },
        {
          title: '本月新增职位',
          value: '256',
          trend: 12,
          icon: 'el-icon-suitcase'
        },
        {
          title: '本月成功招聘',
          value: '128',
          trend: -5,
          icon: 'el-icon-connection'
        }
      ],
      tenantOperationData: []
    }
  },
  computed: {
    ...mapGetters(['name']),
    activityTrendChart() {
      return {
        tooltip: {
          trigger: 'axis'
        },
        legend: {
          data: ['活跃租户', '新增职位', '完成招聘']
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        },
        yAxis: {
          type: 'value'
        },
        series: [
          {
            name: '活跃租户',
            type: 'line',
            smooth: true,
            data: [120, 132, 101, 134, 90, 230, 210],
            itemStyle: {
              color: '#409EFF'
            },
            areaStyle: {
              color: {
                type: 'linear',
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [{
                  offset: 0,
                  color: 'rgba(64,158,255,0.3)'
                }, {
                  offset: 1,
                  color: 'rgba(64,158,255,0.1)'
                }]
              }
            }
          },
          {
            name: '新增职位',
            type: 'line',
            smooth: true,
            data: [220, 182, 191, 234, 290, 330, 310],
            itemStyle: {
              color: '#67C23A'
            }
          },
          {
            name: '完成招聘',
            type: 'line',
            smooth: true,
            data: [150, 232, 201, 154, 190, 330, 410],
            itemStyle: {
              color: '#E6A23C'
            }
          }
        ]
      }
    },
    talentDistributionChart() {
      return {
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'vertical',
          left: 10,
          data: ['焊工', '电工', '钳工', '车工', '其他']
        },
        series: [
          {
            name: '人才分布',
            type: 'pie',
            radius: ['50%', '70%'],
            avoidLabelOverlap: false,
            label: {
              show: false,
              position: 'center'
            },
            emphasis: {
              label: {
                show: true,
                fontSize: '30',
                fontWeight: 'bold'
              }
            },
            labelLine: {
              show: false
            },
            data: [
              { value: 335, name: '焊工', itemStyle: { color: '#409EFF' }},
              { value: 310, name: '电工', itemStyle: { color: '#67C23A' }},
              { value: 234, name: '钳工', itemStyle: { color: '#E6A23C' }},
              { value: 135, name: '车工', itemStyle: { color: '#F56C6C' }},
              { value: 89, name: '其他', itemStyle: { color: '#909399' }}
            ]
          }
        ]
      }
    },
    recruitmentChart() {
      return {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        legend: {
          data: ['投递简历', '面试', '录用']
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'value',
          boundaryGap: [0, 0.01]
        },
        yAxis: {
          type: 'category',
          data: ['焊工', '电工', '钳工', '车工', '其他']
        },
        series: [
          {
            name: '投递简历',
            type: 'bar',
            data: [400, 350, 300, 200, 150],
            itemStyle: { color: '#409EFF' }
          },
          {
            name: '面试',
            type: 'bar',
            data: [200, 180, 150, 100, 70],
            itemStyle: { color: '#67C23A' }
          },
          {
            name: '录用',
            type: 'bar',
            data: [100, 90, 70, 40, 30],
            itemStyle: { color: '#E6A23C' }
          }
        ]
      }
    }
  },
  created() {
    this.fetchDashboardData()
  },
  methods: {
    async fetchDashboardData() {
      this.loading = true
      try {
        // 模拟数据
        this.tenantOperationData = [
          {
            tenantName: '某某科技有限公司',
            activeUsers: 56,
            totalJobs: 12,
            totalApplications: 245,
            conversionRate: 32,
            status: '良好'
          },
          {
            tenantName: '某某制造有限公司',
            activeUsers: 43,
            totalJobs: 8,
            totalApplications: 180,
            conversionRate: 28,
            status: '良好'
          },
          {
            tenantName: '某某工程有限公司',
            activeUsers: 21,
            totalJobs: 5,
            totalApplications: 89,
            conversionRate: 15,
            status: '一般'
          }
        ]
      } catch (error) {
        console.error('获取驾驶舱数据失败:', error)
        this.$message.error('获取数据失败，请稍后重试')
      } finally {
        this.loading = false
      }
    },
    refreshTenantData() {
      this.fetchDashboardData()
    },
    getStatusType(status) {
      const statusMap = {
        '良好': 'success',
        '一般': 'warning',
        '异常': 'danger'
      }
      return statusMap[status] || 'info'
    },
    getConversionColor(rate) {
      if (rate >= 30) return '#67C23A'
      if (rate >= 20) return '#E6A23C'
      return '#F56C6C'
    }
  }
}
</script>

<style lang="scss" scoped>
.admin-dashboard {
  padding: 20px;

  .data-cards {
    margin-bottom: 20px;

    .data-item {
      display: flex;
      align-items: center;

      .data-icon {
        font-size: 48px;
        color: #409EFF;
        margin-right: 20px;
      }

      .data-content {
        flex: 1;

        .data-title {
          font-size: 14px;
          color: #909399;
        }

        .data-value {
          font-size: 24px;
          font-weight: bold;
          margin: 8px 0;
        }

        .data-trend {
          font-size: 12px;
          color: #909399;

          &.up {
            color: #67C23A;
          }

          &.down {
            color: #F56C6C;
          }

          span:last-child {
            margin-left: 5px;
          }
        }
      }
    }
  }

  .charts-container, .bottom-container {
    margin-bottom: 20px;

    .chart-card {
      height: 100%;
    }
  }

  .chart-container {
    height: 350px;
    position: relative;
    width: 100%;

    .chart {
      position: absolute;
      top: 0;
      left: 0;
      width: 100% !important;
      height: 100% !important;
    }
  }
}
</style>
