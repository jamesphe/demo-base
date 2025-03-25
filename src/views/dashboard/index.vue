<template>
  <div class="dashboard-container">
    <!-- 顶部数据卡片 -->
    <el-row :gutter="20" class="data-cards">
      <el-col v-for="card in dataCards" :key="card.title" :span="6">
        <el-card shadow="hover" class="data-card">
          <div class="card-content">
            <div class="card-icon">
              <i :class="card.icon" />
            </div>
            <div class="card-info">
              <div class="card-value">{{ card.value }}</div>
              <div class="card-title">{{ card.title }}</div>
            </div>
            <div class="card-trend" :class="card.trend">
              {{ card.trend === 'up' ? '+' : '-' }}{{ card.change }}%
              <i :class="card.trend === 'up' ? 'el-icon-top' : 'el-icon-bottom'" />
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 主要内容区 -->
    <el-row :gutter="20" class="main-content">
      <!-- 左侧图表区域 -->
      <el-col :span="16">
        <el-card class="chart-card">
          <div slot="header" class="chart-header">
            <span>招聘漏斗分析</span>
            <el-radio-group v-model="timeRange" size="small">
              <el-radio-button label="week">本周</el-radio-button>
              <el-radio-button label="month">本月</el-radio-button>
              <el-radio-button label="year">全年</el-radio-button>
            </el-radio-group>
          </div>
          <div ref="funnelChart" class="chart-container" />
        </el-card>

        <el-card class="chart-card">
          <div slot="header" class="chart-header">
            <span>AI 匹配分析</span>
            <el-select v-model="jobType" size="small" placeholder="选择职位">
              <el-option
                v-for="item in jobTypes"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </el-select>
          </div>
          <div ref="matchChart" class="chart-container" />
        </el-card>
      </el-col>

      <!-- 右侧信息区 -->
      <el-col :span="8">
        <!-- 快捷操作 -->
        <el-card class="quick-actions">
          <div slot="header">
            <span>快捷操作</span>
          </div>
          <div class="action-list">
            <el-button type="primary" icon="el-icon-plus" @click="createJob">发布新职位</el-button>
            <el-button type="success" icon="el-icon-upload" @click="importResumes">导入简历</el-button>
            <el-button type="warning" icon="el-icon-date" @click="scheduleInterview">安排面试</el-button>
          </div>
        </el-card>

        <!-- 待办事项 -->
        <el-card class="todo-card">
          <div slot="header">
            <span>待办事项</span>
            <el-button type="text" @click="viewAllTodos">查看全部</el-button>
          </div>
          <el-timeline>
            <el-timeline-item
              v-for="todo in todoList"
              :key="todo.id"
              :timestamp="todo.time"
              :type="todo.type"
            >
              {{ todo.content }}
            </el-timeline-item>
          </el-timeline>
        </el-card>

        <!-- AI 助手建议 -->
        <el-card class="ai-suggestions">
          <div slot="header">
            <span>AI 助手建议</span>
          </div>
          <div class="suggestion-list">
            <div
              v-for="suggestion in aiSuggestions"
              :key="suggestion.id"
              class="suggestion-item"
            >
              <i class="el-icon-magic-stick" />
              <span>{{ suggestion.content }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'Dashboard',
  data() {
    return {
      timeRange: 'week',
      jobType: 'all',
      dataCards: [
        {
          title: '在招职位',
          value: '28',
          icon: 'el-icon-suitcase',
          trend: 'up',
          change: '15'
        },
        {
          title: '新简历数',
          value: '158',
          icon: 'el-icon-document',
          trend: 'up',
          change: '23'
        },
        {
          title: '待处理',
          value: '36',
          icon: 'el-icon-time',
          trend: 'down',
          change: '8'
        },
        {
          title: 'AI匹配度',
          value: '92%',
          icon: 'el-icon-cpu',
          trend: 'up',
          change: '5'
        }
      ],
      jobTypes: [
        { label: '全部职位', value: 'all' },
        { label: '技术岗位', value: 'tech' },
        { label: '市场营销', value: 'marketing' },
        { label: '行政人事', value: 'hr' }
      ],
      todoList: [
        {
          id: 1,
          content: '3位候选人待初筛',
          time: '09:30',
          type: 'warning'
        },
        {
          id: 2,
          content: '技术总监面试',
          time: '14:00',
          type: 'primary'
        },
        {
          id: 3,
          content: '新简历待审核',
          time: '16:30',
          type: 'info'
        }
      ],
      aiSuggestions: [
        {
          id: 1,
          content: '建议优化Java开发职位描述，当前匹配度偏低'
        },
        {
          id: 2,
          content: '发现3份高匹配度简历，建议优先处理'
        },
        {
          id: 3,
          content: '本周面试通过率低于平均值，建议复查面试流程'
        }
      ]
    }
  },
  mounted() {
    this.initFunnelChart()
    this.initMatchChart()
  },
  methods: {
    initFunnelChart() {
      const chart = echarts.init(this.$refs.funnelChart)
      // 配置漏斗图
      chart.setOption({
        series: [{
          type: 'funnel',
          data: [
            { value: 100, name: '简历投递' },
            { value: 80, name: '初筛通过' },
            { value: 60, name: '面试通过' },
            { value: 40, name: 'Offer发放' },
            { value: 30, name: '入职' }
          ]
        }]
      })
    },
    initMatchChart() {
      const chart = echarts.init(this.$refs.matchChart)
      // 配置匹配分析图
      chart.setOption({
        xAxis: { type: 'category', data: ['技术', '沟通', '经验', '学历', '技能'] },
        yAxis: { type: 'value' },
        series: [{
          type: 'bar',
          data: [90, 85, 78, 95, 88]
        }]
      })
    },
    createJob() {
      this.$router.push('/job/create')
    },
    importResumes() {
      this.$router.push('/resume/import')
    },
    scheduleInterview() {
      this.$router.push('/interview/schedule')
    },
    viewAllTodos() {
      this.$router.push('/todo')
    },
    async initChartData() {
      try {
        const response = await this.$api.getChartData()
        // 使用获取到的数据更新图表
        this.updateCharts(response.data)
      } catch (error) {
        console.error('获取图表数据失败:', error)
      }
    },
    async initLineChart() {
      try {
        const response = await this.$api.getLineChartData()
        // 使用获取到的数据更新折线图
        this.updateLineChart(response.data)
      } catch (error) {
        console.error('获取折线图数据失败:', error)
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.dashboard-container {
  padding: 20px;
  background: #f0f2f5;

  .data-cards {
    margin-bottom: 20px;
  }

  .data-card {
    .card-content {
      display: flex;
      align-items: center;
    }

    .card-icon {
      font-size: 48px;
      color: #1890ff;
      margin-right: 16px;
    }

    .card-info {
      flex: 1;
    }

    .card-value {
      font-size: 24px;
      font-weight: bold;
      margin-bottom: 4px;
    }

    .card-title {
      font-size: 14px;
      color: #666;
    }

    .card-trend {
      font-size: 12px;

      &.up {
        color: #67c23a;
      }

      &.down {
        color: #f56c6c;
      }
    }
  }

  .chart-card {
    margin-bottom: 20px;

    .chart-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .chart-container {
      height: 300px;
    }
  }

  .quick-actions {
    margin-bottom: 20px;

    .action-list {
      display: flex;
      flex-direction: column;
      gap: 10px;

      .el-button {
        width: 100%;
      }
    }
  }

  .todo-card {
    margin-bottom: 20px;
  }

  .ai-suggestions {
    .suggestion-item {
      padding: 10px 0;
      border-bottom: 1px solid #eee;
      display: flex;
      align-items: center;
      gap: 10px;

      &:last-child {
        border-bottom: none;
      }

      i {
        color: #1890ff;
      }
    }
  }
}
</style>
