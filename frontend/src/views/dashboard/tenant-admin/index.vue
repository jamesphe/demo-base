<template>
  <div class="dashboard-tenant-admin">
    <el-row :gutter="20">
      <el-col v-for="(item, index) in statItems" :key="index" :span="6">
        <el-card class="count-panel" shadow="hover">
          <div class="count-panel-content">
            <div class="count-panel-icon">
              <i :class="item.icon" />
            </div>
            <div class="count-panel-info">
              <div class="count-panel-title">{{ item.title }}</div>
              <div class="count-panel-value">{{ item.value }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :xs="24" :sm="24" :lg="12">
        <div class="chart-wrapper">
          <line-chart :chart-data="lineChartData" />
        </div>
      </el-col>
      <el-col :xs="24" :sm="24" :lg="12">
        <div class="chart-wrapper">
          <pie-chart />
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-card class="box-card">
          <div slot="header" class="clearfix">
            <span>最近活动</span>
          </div>
          <div v-if="activities.length === 0" class="empty-data">
            <i class="el-icon-chat-dot-square" />
            <p>暂无活动记录</p>
          </div>
          <div v-else class="activity-list">
            <div v-for="(activity, index) in activities" :key="index" class="activity-item">
              <span class="activity-time">{{ activity.time }}</span>
              <span class="activity-content">{{ activity.content }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="box-card">
          <div slot="header" class="clearfix">
            <span>待办事项</span>
          </div>
          <div v-if="todos.length === 0" class="empty-data">
            <i class="el-icon-check" />
            <p>暂无待办事项</p>
          </div>
          <div v-else class="todo-list">
            <div v-for="(todo, index) in todos" :key="index" class="todo-item">
              <el-checkbox v-model="todo.done">{{ todo.content }}</el-checkbox>
              <span class="todo-deadline">{{ todo.deadline }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import LineChart from '../admin/components/LineChart'
import PieChart from '../admin/components/PieChart'

export default {
  name: 'TenantAdminDashboard',
  components: {
    LineChart,
    PieChart
  },
  data() {
    return {
      stats: {
        totalResumes: 256,
        monthlyNewResumes: 42,
        activePositions: 15,
        monthlyInterviews: 28
      },
      lineChartData: {
        expectedData: [100, 120, 161, 134, 105, 160, 165],
        actualData: [120, 82, 91, 154, 162, 140, 145]
      },
      activities: [
        { time: '2023-05-18 10:30', content: '张三上传了5份新简历' },
        { time: '2023-05-17 14:20', content: '李四安排了3场面试' },
        { time: '2023-05-16 09:15', content: '王五发布了2个新职位' }
      ],
      todos: [
        { content: '审核高级前端开发简历', deadline: '今天 14:00', done: false },
        { content: '安排产品经理候选人面试', deadline: '明天 10:30', done: false },
        { content: '更新招聘计划文档', deadline: '后天', done: false }
      ]
    }
  },
  computed: {
    statItems() {
      return [
        { title: '总简历数', value: this.stats.totalResumes, icon: 'el-icon-document' },
        { title: '本月新增', value: this.stats.monthlyNewResumes, icon: 'el-icon-plus' },
        { title: '进行中职位', value: this.stats.activePositions, icon: 'el-icon-suitcase' },
        { title: '本月面试', value: this.stats.monthlyInterviews, icon: 'el-icon-date' }
      ]
    }
  }
}
</script>

<style lang="scss" scoped>
.dashboard-tenant-admin {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: calc(100vh - 84px);

  .chart-wrapper {
    background: #fff;
    padding: 16px;
    margin-bottom: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
    transition: all 0.3s ease;

    &:hover {
      transform: translateY(-5px);
      box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    }
  }

  .count-panel {
    margin-bottom: 20px;
    border-radius: 8px;
    overflow: hidden;
    transition: all 0.3s ease;

    &:hover {
      transform: translateY(-5px);
      box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    }

    .count-panel-content {
      display: flex;
      align-items: center;
      padding: 20px;
    }

    .count-panel-icon {
      font-size: 48px;
      margin-right: 20px;
      color: #409EFF;
      background-color: rgba(64, 158, 255, 0.1);
      width: 70px;
      height: 70px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.3s ease;
    }

    &:hover .count-panel-icon {
      transform: scale(1.1);
    }

    .count-panel-info {
      flex: 1;
    }

    .count-panel-title {
      font-size: 14px;
      color: #909399;
      margin-bottom: 10px;
    }

    .count-panel-value {
      font-size: 28px;
      font-weight: bold;
      color: #303133;
      line-height: 1;
    }
  }

  .box-card {
    margin-bottom: 20px;
    border-radius: 8px;
    transition: all 0.3s ease;

    &:hover {
      transform: translateY(-5px);
      box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    }

    .el-card__header {
      padding: 15px 20px;
      font-weight: bold;
      border-bottom: 1px solid #ebeef5;
      background-color: #fafafa;
    }
  }

  .empty-data {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 40px 0;
    color: #909399;

    i {
      font-size: 60px;
      margin-bottom: 20px;
      color: #dcdfe6;
    }

    p {
      font-size: 16px;
      margin: 0;
    }
  }

  .activity-list {
    .activity-item {
      padding: 15px 0;
      border-bottom: 1px solid #EBEEF5;
      display: flex;

      &:last-child {
        border-bottom: none;
      }

      .activity-time {
        color: #909399;
        font-size: 13px;
        width: 140px;
        flex-shrink: 0;
        position: relative;
        padding-left: 15px;

        &:before {
          content: '';
          position: absolute;
          left: 0;
          top: 50%;
          transform: translateY(-50%);
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background-color: #409EFF;
        }
      }

      .activity-content {
        flex: 1;
        font-size: 14px;
      }
    }
  }

  .todo-list {
    .todo-item {
      padding: 15px 0;
      border-bottom: 1px solid #EBEEF5;
      display: flex;
      justify-content: space-between;
      align-items: center;

      &:last-child {
        border-bottom: none;
      }

      .el-checkbox {
        font-size: 14px;
      }

      .todo-deadline {
        color: #909399;
        font-size: 13px;
        background-color: #f5f7fa;
        padding: 4px 8px;
        border-radius: 4px;
        display: inline-flex;
        align-items: center;

        &:before {
          content: '\e78f'; /* 使用 Element UI 的时钟图标 */
          font-family: 'element-icons';
          margin-right: 4px;
          font-size: 12px;
        }
      }
    }
  }

  /* 响应式调整 */
  @media (max-width: 768px) {
    padding: 10px;

    .count-panel {
      .count-panel-content {
        padding: 15px;
      }

      .count-panel-icon {
        font-size: 36px;
        width: 50px;
        height: 50px;
        margin-right: 15px;
      }

      .count-panel-value {
        font-size: 22px;
      }
    }

    .activity-time {
      width: 120px !important;
    }
  }
}
</style>
