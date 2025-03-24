<template>
  <div class="dashboard-tenant-user">
    <el-row :gutter="20">
      <el-col :span="16">
        <div class="main-content">
          <div class="welcome-section">
            <h2>欢迎回来，{{ userInfo.name }}</h2>
            <p>{{ getGreeting() }}</p>
            <div class="welcome-date">{{ getCurrentDate() }}</div>
          </div>
          
          <div class="task-section">
            <div class="section-header">
              <h3><i class="el-icon-s-claim"></i> 我的待办</h3>
              <el-button type="text" size="small">查看全部</el-button>
            </div>
            <el-card shadow="hover">
              <div v-for="task in myTasks" :key="task.id" class="task-item">
                <el-tag :type="task.priority">{{ task.type }}</el-tag>
                <span class="task-title">{{ task.title }}</span>
                <span class="task-time"><i class="el-icon-time"></i> {{ task.deadline }}</span>
                <el-button type="text" size="small" class="task-action">处理</el-button>
              </div>
              <div v-if="myTasks.length === 0" class="empty-placeholder">
                <i class="el-icon-check"></i>
                <p>暂无待办任务</p>
              </div>
            </el-card>
          </div>

          <div class="interview-section">
            <div class="section-header">
              <h3><i class="el-icon-s-cooperation"></i> 近期面试安排</h3>
              <el-button type="text" size="small">安排面试</el-button>
            </div>
            <el-timeline>
              <el-timeline-item
                v-for="interview in recentInterviews"
                :key="interview.id"
                :timestamp="interview.time"
                :type="interview.status">
                <el-card shadow="hover" class="interview-card">
                  <div class="interview-info">
                    <div class="candidate-info">
                      <strong class="candidate-name">{{ interview.candidateName }}</strong>
                      <span class="position-name">{{ interview.position }}</span>
                    </div>
                    <div class="interview-location" v-if="interview.location">
                      <i class="el-icon-location"></i> {{ interview.location }}
                    </div>
                    <div class="interview-actions">
                      <el-button type="primary" size="mini" icon="el-icon-view">查看详情</el-button>
                      <el-button type="info" size="mini" icon="el-icon-edit">编辑</el-button>
                    </div>
                  </div>
                </el-card>
              </el-timeline-item>
              <div v-if="recentInterviews.length === 0" class="empty-placeholder">
                <i class="el-icon-date"></i>
                <p>暂无面试安排</p>
              </div>
            </el-timeline>
          </div>
        </div>
      </el-col>
      
      <el-col :span="8">
        <div class="side-content">
          <el-card class="user-info-card" shadow="hover">
            <div class="user-profile">
              <el-avatar :size="80" :src="userInfo.avatar"></el-avatar>
              <div class="user-details">
                <h3>{{ userInfo.name }}</h3>
                <p class="user-department">{{ userInfo.department }}</p>
                <p class="user-position">{{ userInfo.position }}</p>
                <el-button type="text" icon="el-icon-edit">编辑资料</el-button>
              </div>
            </div>
            <div class="user-status">
              <div class="status-item">
                <span class="status-value">{{ userInfo.daysActive }}</span>
                <span class="status-label">活跃天数</span>
              </div>
              <div class="status-item">
                <span class="status-value">{{ userInfo.completedTasks }}</span>
                <span class="status-label">已完成任务</span>
              </div>
            </div>
          </el-card>

          <el-card class="statistics-card" shadow="hover">
            <div class="card-header">
              <h4><i class="el-icon-data-analysis"></i> 本月工作统计</h4>
              <el-dropdown size="small">
                <span class="el-dropdown-link">
                  <i class="el-icon-more"></i>
                </span>
                <el-dropdown-menu slot="dropdown">
                  <el-dropdown-item>查看详细报表</el-dropdown-item>
                  <el-dropdown-item>导出数据</el-dropdown-item>
                </el-dropdown-menu>
              </el-dropdown>
            </div>
            <div class="stat-items">
              <div class="stat-item">
                <div class="stat-icon">
                  <i class="el-icon-document"></i>
                </div>
                <div class="stat-content">
                  <div class="stat-value">{{ monthlyStats.processedResumes }}</div>
                  <div class="stat-label">处理简历</div>
                </div>
              </div>
              <div class="stat-item">
                <div class="stat-icon">
                  <i class="el-icon-user"></i>
                </div>
                <div class="stat-content">
                  <div class="stat-value">{{ monthlyStats.interviews }}</div>
                  <div class="stat-label">面试场数</div>
                </div>
              </div>
            </div>
            <div class="stat-progress">
              <div class="progress-item">
                <div class="progress-label">
                  <span>本月目标完成度</span>
                  <span>{{ monthlyStats.completionRate }}%</span>
                </div>
                <el-progress :percentage="monthlyStats.completionRate" :color="progressColor"></el-progress>
              </div>
            </div>
          </el-card>
          
          <el-card class="quick-actions-card" shadow="hover">
            <div class="card-header">
              <h4><i class="el-icon-s-tools"></i> 快捷操作</h4>
            </div>
            <div class="quick-actions">
              <el-button type="primary" icon="el-icon-plus">新建面试</el-button>
              <el-button type="success" icon="el-icon-upload">上传简历</el-button>
              <el-button type="info" icon="el-icon-message">发送通知</el-button>
            </div>
          </el-card>
          
          <el-card class="calendar-card" shadow="hover">
            <div class="card-header">
              <h4><i class="el-icon-date"></i> 日程提醒</h4>
            </div>
            <div class="upcoming-events">
              <div class="event-item" v-for="event in upcomingEvents" :key="event.id">
                <div class="event-date">
                  <div class="event-day">{{ event.day }}</div>
                  <div class="event-month">{{ event.month }}</div>
                </div>
                <div class="event-content">
                  <div class="event-title">{{ event.title }}</div>
                  <div class="event-time"><i class="el-icon-time"></i> {{ event.time }}</div>
                </div>
              </div>
            </div>
          </el-card>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script>
export default {
  name: 'TenantUserDashboard',
  data() {
    return {
      userInfo: {
        name: '张三',
        avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
        department: '人力资源部',
        position: '招聘专员',
        daysActive: 128,
        completedTasks: 56
      },
      myTasks: [
        { id: 1, type: '简历筛选', title: '审核高级前端开发简历', deadline: '今天 14:00', priority: 'danger' },
        { id: 2, type: '面试', title: '产品经理候选人面试', deadline: '明天 10:30', priority: 'warning' },
        { id: 3, type: '反馈', title: '提交面试评价', deadline: '后天', priority: 'info' }
      ],
      recentInterviews: [
        { id: 1, candidateName: '李四', position: 'UI设计师', time: '2023-05-20 09:30', status: 'primary', location: '总部 3楼会议室A' },
        { id: 2, candidateName: '王五', position: '后端工程师', time: '2023-05-21 14:00', status: 'success', location: '线上会议' },
        { id: 3, candidateName: '赵六', position: '产品经理', time: '2023-05-22 16:30', status: 'warning', location: '分部 2楼会议室B' }
      ],
      monthlyStats: {
        processedResumes: 42,
        interviews: 15,
        completionRate: 78
      },
      upcomingEvents: [
        { id: 1, day: '15', month: '5月', title: '部门周会', time: '10:00 - 11:30' },
        { id: 2, day: '18', month: '5月', title: '招聘计划讨论', time: '14:00 - 15:00' }
      ]
    }
  },
  computed: {
    progressColor() {
      const rate = this.monthlyStats.completionRate
      if (rate < 30) return '#F56C6C'
      if (rate < 70) return '#E6A23C'
      return '#67C23A'
    }
  },
  methods: {
    getGreeting() {
      const hour = new Date().getHours()
      if (hour < 12) return '早上好！开始新的一天吧'
      if (hour < 18) return '下午好！继续加油'
      return '晚上好！记得及时休息'
    },
    getCurrentDate() {
      const options = { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' }
      return new Date().toLocaleDateString('zh-CN', options)
    }
  }
}
</script>

<style scoped>
/* 全局样式和字体设置 */
.dashboard-tenant-user {
  padding: 20px;
  font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "微软雅黑", Arial, sans-serif;
  color: #303133;
  line-height: 1.5;
}

.main-content, .side-content {
  margin-bottom: 20px;
}

/* 欢迎区域样式 */
.welcome-section {
  margin-bottom: 24px;
  background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
  color: white;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  position: relative;
}

.welcome-section h2 {
  margin: 0 0 8px 0;
  font-size: 26px;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.welcome-section p {
  margin: 0;
  font-size: 16px;
  opacity: 0.9;
  font-weight: 300;
}

.welcome-date {
  position: absolute;
  top: 24px;
  right: 24px;
  font-size: 14px;
  opacity: 0.8;
}

/* 区块标题样式 */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
}

h3 i {
  margin-right: 8px;
  color: #409EFF;
}

/* 任务列表样式 */
.task-section, .interview-section {
  margin-bottom: 24px;
}

.task-item {
  display: flex;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #ebeef5;
}

.task-item:last-child {
  border-bottom: none;
}

.task-title {
  flex: 1;
  margin: 0 12px;
  font-weight: 500;
  font-size: 15px;
}

.task-time {
  color: #909399;
  margin-right: 12px;
  font-size: 13px;
  display: flex;
  align-items: center;
}

.task-time i {
  margin-right: 4px;
}

/* 面试卡片样式 */
.interview-card {
  margin-bottom: 8px;
  border-radius: 6px;
}

.interview-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.candidate-info {
  display: flex;
  align-items: center;
}

.candidate-name {
  font-size: 16px;
  margin-right: 8px;
}

.position-name {
  color: #606266;
  font-size: 14px;
}

.interview-location {
  font-size: 13px;
  color: #606266;
  display: flex;
  align-items: center;
}

.interview-location i {
  margin-right: 4px;
  color: #909399;
}

.interview-actions {
  margin-top: 12px;
  display: flex;
  gap: 8px;
}

/* 用户信息卡片样式 */
.user-info-card, .statistics-card, .quick-actions-card, .calendar-card {
  margin-bottom: 20px;
  border-radius: 8px;
  overflow: hidden;
}

.user-profile {
  display: flex;
  align-items: center;
  padding: 16px 0;
}

.user-details {
  margin-left: 16px;
}

.user-details h3 {
  margin: 0 0 4px 0;
  font-size: 18px;
  font-weight: 600;
}

.user-department {
  margin: 0 0 4px 0;
  color: #606266;
  font-size: 14px;
}

.user-position {
  margin: 0 0 8px 0;
  color: #909399;
  font-size: 13px;
}

.user-status {
  display: flex;
  justify-content: space-around;
  border-top: 1px solid #ebeef5;
  padding-top: 16px;
  margin-top: 8px;
}

.status-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.status-value {
  font-size: 20px;
  font-weight: bold;
  color: #409EFF;
}

.status-label {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

/* 卡片标题样式 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
}

h4 i {
  margin-right: 8px;
  color: #409EFF;
}

/* 统计数据样式 */
.stat-items {
  display: flex;
  justify-content: space-around;
  margin-top: 16px;
}

.stat-item {
  display: flex;
  align-items: center;
  padding: 8px 0;
}

.stat-icon {
  font-size: 28px;
  color: #409EFF;
  margin-right: 12px;
  background-color: rgba(64, 158, 255, 0.1);
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-value {
  font-size: 26px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #606266;
  margin-top: 4px;
}

.stat-progress {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px dashed #ebeef5;
}

.progress-item {
  padding: 0 12px;
}

.progress-label {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
  color: #606266;
}

/* 快捷操作样式 */
.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 16px;
}

.quick-actions button {
  width: 100%;
  font-size: 14px;
  font-weight: 500;
  letter-spacing: 0.5px;
  padding: 12px 0;
}

/* 日程卡片样式 */
.upcoming-events {
  margin-top: 16px;
}

.event-item {
  display: flex;
  padding: 12px 0;
  border-bottom: 1px solid #ebeef5;
}

.event-item:last-child {
  border-bottom: none;
}

.event-date {
  width: 50px;
  height: 50px;
  background-color: #f5f7fa;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
}

.event-day {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

.event-month {
  font-size: 12px;
  color: #909399;
}

.event-content {
  flex: 1;
}

.event-title {
  font-size: 15px;
  font-weight: 500;
  margin-bottom: 4px;
}

.event-time {
  font-size: 13px;
  color: #909399;
  display: flex;
  align-items: center;
}

.event-time i {
  margin-right: 4px;
}

/* 空状态样式 */
.empty-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px 0;
  color: #909399;
}

.empty-placeholder i {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-placeholder p {
  font-size: 14px;
  margin: 0;
}
</style>