<template>
  <div class="dashboard-container">
    <!-- 欢迎信息 -->
    <div class="welcome-section">
      <div class="welcome-info">
        <img class="avatar" :src="userAvatar" alt="avatar">
        <div class="welcome-text">
          <h2>{{ greeting }}，{{ userName }}</h2>
          <p>{{ welcomeMessage }}</p>
        </div>
      </div>
      <div class="weather-info">
        <i class="el-icon-sunny" />
        <span>{{ weather.temp }}°C</span>
        <span>{{ weather.city }}</span>
      </div>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="20">
      <el-col v-for="(item, index) in statCards" :key="index" :span="6">
        <el-card shadow="hover" class="stat-card" :class="item.class">
          <div class="card-header">
            <i :class="item.icon" />
            <count-to
              :start-val="0"
              :end-val="item.value"
              :duration="2000"
              class="card-number"
              separator=","
            />
            <div class="card-title">{{ item.title }}</div>
          </div>
          <div class="card-footer">
            <span>{{ item.footerLabel }}</span>
            <span :class="['change-rate', item.trend]">
              {{ item.footerValue }}
              <i :class="item.trendIcon" />
            </span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 快捷入口 -->
    <el-row :gutter="20" class="quick-access">
      <el-col :span="16">
        <el-card class="todo-card">
          <div slot="header" class="clearfix">
            <span class="card-title"><i class="el-icon-tickets" /> 待办事项</span>
            <el-button type="primary" size="small" plain style="float: right">
              查看全部
            </el-button>
          </div>
          <el-table
            :data="todoList"
            style="width: 100%"
            :show-header="false"
            @row-click="handleTodo"
          >
            <el-table-column width="80">
              <template slot-scope="scope">
                <el-tag
                  :type="scope.row.type"
                  size="mini"
                  effect="dark"
                >{{ scope.row.typeText }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column>
              <template slot-scope="scope">
                <div class="todo-item">
                  <span class="todo-title">{{ scope.row.title }}</span>
                  <span class="todo-time">{{ scope.row.time }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column width="100" align="right">
              <template slot-scope="scope">
                <el-button
                  type="text"
                  size="small"
                  @click.stop="handleTodo(scope.row)"
                >处理</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="schedule-card">
          <div slot="header" class="clearfix">
            <span class="card-title"><i class="el-icon-date" /> 本月日程</span>
            <el-button type="primary" size="small" plain style="float: right">
              添加日程
            </el-button>
          </div>
          <el-calendar :range="[new Date(), new Date()]">
            <template slot="dateCell" slot-scope="{date, data}">
              <div class="calendar-day" :class="{ 'has-schedule': hasSchedule(date) }">
                {{ data.day.split('-').slice(2).join('') }}
                <div v-if="hasSchedule(date)" class="schedule-info">
                  {{ getScheduleInfo(date) }}
                </div>
              </div>
            </template>
          </el-calendar>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import CountTo from 'vue-count-to'

export default {
  name: 'HrmsDashboard',
  components: {
    CountTo
  },
  data() {
    return {
      userName: '管理员',
      userAvatar: 'https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif',
      weather: {
        temp: 26,
        city: '深圳市'
      },
      statCards: [
        {
          title: '在职员工',
          value: 256,
          icon: 'el-icon-user',
          footerLabel: '较上月',
          footerValue: '2.5%',
          trend: 'up',
          trendIcon: 'el-icon-top',
          class: 'blue-card'
        },
        {
          title: '本月入职',
          value: 15,
          icon: 'el-icon-plus',
          footerLabel: '计划招聘',
          footerValue: '20人',
          trend: 'normal',
          class: 'green-card'
        },
        {
          title: '本月离职',
          value: 3,
          icon: 'el-icon-minus',
          footerLabel: '离职率',
          footerValue: '1.2%',
          trend: 'normal',
          class: 'orange-card'
        },
        {
          title: '培训计划',
          value: 5,
          icon: 'el-icon-reading',
          footerLabel: '完成率',
          footerValue: '80%',
          trend: 'up',
          trendIcon: 'el-icon-top',
          class: 'purple-card'
        }
      ],
      todoList: [
        { type: 'warning', typeText: '审批', title: '张三的请假申请', time: '10:30' },
        { type: 'info', typeText: '培训', title: '新员工入职培训', time: '14:00' },
        { type: 'success', typeText: '招聘', title: '面试候选人安排', time: '16:30' },
        { type: 'danger', typeText: '考核', title: '月度考核评定', time: '明天' }
      ],
      schedules: {
        // 模拟数据
        '2024-03-15': '部门会议',
        '2024-03-20': '员工培训'
      }
    }
  },
  computed: {
    greeting() {
      const hour = new Date().getHours()
      if (hour < 6) return '凌晨好'
      if (hour < 9) return '早上好'
      if (hour < 12) return '上午好'
      if (hour < 14) return '中午好'
      if (hour < 17) return '下午好'
      if (hour < 19) return '傍晚好'
      return '晚上好'
    },
    welcomeMessage() {
      const now = new Date()
      return `今天是${now.getFullYear()}年${now.getMonth() + 1}月${now.getDate()}日，欢迎使用人事管理系统`
    }
  },
  methods: {
    handleTodo(item) {
      this.$message({
        message: `正在处理：${item.title}`,
        type: 'info'
      })
    },
    hasSchedule(date) {
      const dateStr = this.formatDate(date)
      return !!this.schedules[dateStr]
    },
    getScheduleInfo(date) {
      const dateStr = this.formatDate(date)
      return this.schedules[dateStr]
    },
    formatDate(date) {
      const d = new Date(date)
      return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
    }
  }
}
</script>

<style lang="scss" scoped>
.dashboard-container {
  padding: 20px;
  background-color: #f0f2f5;
  min-height: calc(100vh - 84px);

  .welcome-section {
    background: linear-gradient(to right, #1890ff, #36cfc9);
    padding: 20px;
    border-radius: 8px;
    color: white;
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);

    .welcome-info {
      display: flex;
      align-items: center;

      .avatar {
        width: 64px;
        height: 64px;
        border-radius: 50%;
        margin-right: 20px;
        border: 2px solid rgba(255,255,255,0.8);
      }

      .welcome-text {
        h2 {
          margin: 0;
          font-size: 24px;
          font-weight: normal;
        }
        p {
          margin: 8px 0 0;
          opacity: 0.8;
        }
      }
    }

    .weather-info {
      text-align: right;
      font-size: 16px;
      i {
        font-size: 24px;
        margin-right: 8px;
      }
      span {
        margin-left: 8px;
      }
    }
  }

  .stat-card {
    transition: all 0.3s;
    margin-bottom: 20px;

    &:hover {
      transform: translateY(-4px);
      box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }

    .card-header {
      text-align: center;
      padding: 20px 0;
      position: relative;

      i {
        font-size: 24px;
        position: absolute;
        left: 20px;
        top: 20px;
        opacity: 0.8;
      }

      .card-number {
        font-size: 36px;
        font-weight: bold;
        color: #303133;
        line-height: 1;
      }

      .card-title {
        font-size: 14px;
        color: #909399;
        margin-top: 12px;
      }
    }

    .card-footer {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 15px;
      margin-top: 10px;
      border-top: 1px solid rgba(0,0,0,0.05);
      color: #909399;
      font-size: 13px;

      .change-rate {
        &.up {
          color: #67C23A;
          i { margin-left: 4px; }
        }
        &.down {
          color: #F56C6C;
          i { margin-left: 4px; }
        }
      }
    }

    &.blue-card { .card-header i { color: #409EFF; }}
    &.green-card { .card-header i { color: #67C23A; }}
    &.orange-card { .card-header i { color: #E6A23C; }}
    &.purple-card { .card-header i { color: #909399; }}
  }

  .quick-access {
    .todo-card, .schedule-card {
      margin-bottom: 20px;

      .card-title {
        font-size: 16px;
        font-weight: 500;
        i {
          margin-right: 8px;
        }
      }
    }

    .todo-item {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .todo-title {
        color: #303133;
      }

      .todo-time {
        color: #909399;
        font-size: 13px;
      }
    }

    .calendar-day {
      height: 32px;
      text-align: center;
      position: relative;
      padding: 4px;
      font-size: 13px;

      &.has-schedule {
        background-color: #ecf5ff;
        border-radius: 4px;
        color: #409EFF;
      }

      .schedule-info {
        position: absolute;
        bottom: 2px;
        left: 50%;
        transform: translateX(-50%);
        font-size: 10px;
        color: #409EFF;
        white-space: nowrap;
      }
    }
  }

  .el-table {
    .el-button--text {
      padding: 0;
    }
    &::before {
      display: none;
    }
  }
}
</style>
