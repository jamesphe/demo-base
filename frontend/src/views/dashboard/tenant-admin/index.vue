<template>
  <div class="tenant-dashboard">
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
      <!-- 左侧：招聘漏斗 -->
      <el-col :span="12">
        <el-card class="chart-card" shadow="hover">
          <div slot="header">
            <span>招聘漏斗分析</span>
            <el-select v-model="funnelTimeRange" size="small" style="float: right; width: 120px">
              <el-option label="最近7天" value="week" />
              <el-option label="最近30天" value="month" />
              <el-option label="最近90天" value="quarter" />
            </el-select>
          </div>
          <div class="chart-container">
            <v-chart :options="recruitmentFunnelChart" autoresize />
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：职位状态分布 -->
      <el-col :span="12">
        <el-card class="chart-card" shadow="hover">
          <div slot="header">
            <span>职位状态分布</span>
            <el-radio-group v-model="jobStatusType" size="small" style="float: right">
              <el-radio-button label="all">全部</el-radio-button>
              <el-radio-button label="active">进行中</el-radio-button>
            </el-radio-group>
          </div>
          <div class="chart-container">
            <v-chart :options="jobStatusChart" autoresize />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 下方区域 -->
    <el-row :gutter="20" class="bottom-container">
      <!-- 左侧：简历处理进度 -->
      <el-col :span="14">
        <el-card class="chart-card" shadow="hover">
          <div slot="header">
            <span>简历处理进度</span>
            <el-tooltip content="展示各职位的简历处理情况" placement="top">
              <i class="el-icon-info" style="margin-left: 8px" />
            </el-tooltip>
          </div>
          <el-table :data="resumeProgressData" style="width: 100%" :max-height="350">
            <el-table-column prop="jobTitle" label="职位名称" width="180" />
            <el-table-column prop="totalResumes" label="收到简历" width="100" align="center" />
            <el-table-column prop="reviewed" label="已筛选" width="100" align="center" />
            <el-table-column prop="interviewed" label="已面试" width="100" align="center" />
            <el-table-column prop="progress" label="处理进度" align="center">
              <template slot-scope="scope">
                <el-progress
                  :percentage="scope.row.progress"
                  :color="getProgressColor(scope.row.progress)"
                />
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100" align="center">
              <template slot-scope="scope">
                <el-tag :type="getJobStatusType(scope.row.status)">{{ scope.row.status }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <!-- 右侧：待办事项 -->
      <el-col :span="10">
        <el-card shadow="hover">
          <div slot="header">
            <span>待办事项</span>
            <el-button style="float: right" type="text" @click="refreshTodoList">
              <i class="el-icon-refresh" /> 刷新
            </el-button>
          </div>
          <div class="todo-list">
            <div v-for="(item, index) in todoList" :key="index" class="todo-item">
              <div class="todo-icon">
                <el-badge :value="item.count" :type="item.type">
                  <i :class="item.icon" />
                </el-badge>
              </div>
              <div class="todo-content">
                <div class="todo-title">{{ item.title }}</div>
                <div class="todo-desc">{{ item.description }}</div>
              </div>
              <div class="todo-action">
                <el-button type="text" @click="handleTodoAction(item)">处理</el-button>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import ECharts from 'vue-echarts'
import 'echarts/lib/chart/funnel'
import 'echarts/lib/chart/pie'
import 'echarts/lib/component/tooltip'
import 'echarts/lib/component/title'
import 'echarts/lib/component/legend'

export default {
  name: 'TenantDashboard',
  components: {
    'v-chart': ECharts
  },
  data() {
    return {
      funnelTimeRange: 'week',
      jobStatusType: 'all',
      loading: false,
      cardData: [
        {
          title: '在招职位',
          value: '42',
          trend: 8,
          icon: 'el-icon-suitcase'
        },
        {
          title: '本月简历',
          value: '256',
          trend: 15,
          icon: 'el-icon-document'
        },
        {
          title: '待处理',
          value: '15',
          trend: -5,
          icon: 'el-icon-time'
        },
        {
          title: '本月入职',
          value: '28',
          trend: 12,
          icon: 'el-icon-user'
        }
      ],
      resumeProgressData: [],
      todoList: []
    }
  },
  computed: {
    ...mapGetters(['name']),
    recruitmentFunnelChart() {
      return {
        tooltip: {
          trigger: 'item',
          formatter: '{b}: {c}'
        },
        legend: {
          data: ['投递简历', '初筛通过', '面试通过', '发放offer', '成功入职']
        },
        series: [
          {
            name: '招聘漏斗',
            type: 'funnel',
            left: '10%',
            top: 60,
            bottom: 60,
            width: '80%',
            min: 0,
            max: 100,
            minSize: '0%',
            maxSize: '100%',
            sort: 'descending',
            gap: 2,
            label: {
              show: true,
              position: 'inside'
            },
            labelLine: {
              length: 10,
              lineStyle: {
                width: 1,
                type: 'solid'
              }
            },
            itemStyle: {
              borderColor: '#fff',
              borderWidth: 1
            },
            emphasis: {
              label: {
                fontSize: 20
              }
            },
            data: [
              { value: 256, name: '投递简历', itemStyle: { color: '#409EFF' }},
              { value: 180, name: '初筛通过', itemStyle: { color: '#67C23A' }},
              { value: 90, name: '面试通过', itemStyle: { color: '#E6A23C' }},
              { value: 45, name: '发放offer', itemStyle: { color: '#F56C6C' }},
              { value: 28, name: '成功入职', itemStyle: { color: '#909399' }}
            ]
          }
        ]
      }
    },
    jobStatusChart() {
      return {
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'vertical',
          left: 10,
          data: ['招聘中', '已暂停', '已结束', '待开始']
        },
        series: [
          {
            name: '职位状态',
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
              { value: 25, name: '招聘中', itemStyle: { color: '#67C23A' }},
              { value: 8, name: '已暂停', itemStyle: { color: '#E6A23C' }},
              { value: 12, name: '已结束', itemStyle: { color: '#909399' }},
              { value: 5, name: '待开始', itemStyle: { color: '#409EFF' }}
            ]
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
        this.resumeProgressData = [
          {
            jobTitle: '高级焊工',
            totalResumes: 68,
            reviewed: 45,
            interviewed: 20,
            progress: 85,
            status: '进行中'
          },
          {
            jobTitle: '电工组长',
            totalResumes: 42,
            reviewed: 30,
            interviewed: 15,
            progress: 65,
            status: '进行中'
          },
          {
            jobTitle: '钳工',
            totalResumes: 35,
            reviewed: 15,
            interviewed: 8,
            progress: 45,
            status: '待处理'
          }
        ]

        this.todoList = [
          {
            title: '待筛选简历',
            description: '您有15份新简历待筛选',
            count: 15,
            type: 'warning',
            icon: 'el-icon-document'
          },
          {
            title: '待安排面试',
            description: '8位候选人等待面试安排',
            count: 8,
            type: 'danger',
            icon: 'el-icon-date'
          },
          {
            title: '待发送offer',
            description: '3位候选人待发送offer',
            count: 3,
            type: 'success',
            icon: 'el-icon-message'
          }
        ]
      } catch (error) {
        console.error('获取驾驶舱数据失败:', error)
        this.$message.error('获取数据失败，请稍后重试')
      } finally {
        this.loading = false
      }
    },
    refreshTodoList() {
      this.fetchDashboardData()
    },
    getJobStatusType(status) {
      const statusMap = {
        '进行中': 'success',
        '待处理': 'warning',
        '已暂停': 'info',
        '已结束': 'danger'
      }
      return statusMap[status] || 'info'
    },
    getProgressColor(progress) {
      if (progress >= 80) return '#67C23A'
      if (progress >= 50) return '#E6A23C'
      return '#F56C6C'
    },
    handleTodoAction(item) {
      // 处理待办事项的点击
      console.log('处理待办事项:', item)
    }
  }
}
</script>

<style lang="scss" scoped>
.tenant-dashboard {
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

  .charts-container {
    margin-bottom: 20px;
  }

  .bottom-container {
    margin-bottom: 20px;
  }

  .chart-card {
    .chart-container {
      height: 350px;
    }
  }

  .todo-list {
    .todo-item {
      display: flex;
      align-items: center;
      padding: 15px 0;
      border-bottom: 1px solid #EBEEF5;

      &:last-child {
        border-bottom: none;
      }

      .todo-icon {
        margin-right: 20px;
        font-size: 24px;
        color: #409EFF;
      }

      .todo-content {
        flex: 1;

        .todo-title {
          font-size: 16px;
          color: #303133;
          margin-bottom: 5px;
        }

        .todo-desc {
          font-size: 13px;
          color: #909399;
        }
      }

      .todo-action {
        margin-left: 20px;
      }
    }
  }
}
</style>
