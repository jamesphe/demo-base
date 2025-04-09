<template>
  <div class="trial-status-container">
    <h1>试用状态</h1>

    <el-card v-if="trialInfo.status === 'pending'" class="status-card pending">
      <div class="status-icon"><i class="el-icon-time" /></div>
      <h2>申请审核中</h2>
      <p>您的试用申请正在审核中，请耐心等待。我们将在1-2个工作日内完成审核。</p>
      <p class="application-date">申请时间：{{ formatDate(trialInfo.createdAt) }}</p>
    </el-card>

    <el-card v-else-if="trialInfo.status === 'active'" class="status-card active">
      <div class="status-icon"><i class="el-icon-success" /></div>
      <h2>试用中</h2>
      <p>您的试用已经开始，可以体验所有功能。</p>
      <p class="trial-period">
        试用期限：{{ formatDate(trialInfo.trialStartDate) }} 至 {{ formatDate(trialInfo.trialEndDate) }}
      </p>
      <p class="trial-remaining">剩余天数：{{ remainingDays }}天</p>
      <el-button type="primary" @click="$router.push('/dashboard')">进入系统</el-button>
    </el-card>

    <el-card v-else-if="trialInfo.status === 'expired'" class="status-card expired">
      <div class="status-icon"><i class="el-icon-warning" /></div>
      <h2>试用已结束</h2>
      <p>您的试用期已结束，如需继续使用，请升级为付费用户。</p>
      <p class="trial-period">
        试用期限：{{ formatDate(trialInfo.trialStartDate) }} 至 {{ formatDate(trialInfo.trialEndDate) }}
      </p>
      <el-button type="primary" @click="$router.push('/pricing')">查看套餐</el-button>
    </el-card>

    <el-card v-else-if="trialInfo.status === 'rejected'" class="status-card rejected">
      <div class="status-icon"><i class="el-icon-error" /></div>
      <h2>申请未通过</h2>
      <p>很抱歉，您的试用申请未通过审核。</p>
      <p v-if="trialInfo.rejectReason" class="reject-reason">
        原因：{{ trialInfo.rejectReason }}
      </p>
      <el-button @click="$router.push('/trial-application')">重新申请</el-button>
    </el-card>
  </div>
</template>

<script>
import { getTrialStatus } from '@/api/user'
import { mapGetters } from 'vuex'

export default {
  name: 'TrialStatus',
  data() {
    return {
      trialInfo: {
        status: '',
        createdAt: '',
        trialStartDate: '',
        trialEndDate: '',
        rejectReason: ''
      }
    }
  },
  computed: {
    ...mapGetters([
      'userId'
    ]),
    remainingDays() {
      if (!this.trialInfo.trialEndDate) return 0
      const endDate = new Date(this.trialInfo.trialEndDate)
      const today = new Date()
      const diffTime = endDate - today
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
      return diffDays > 0 ? diffDays : 0
    }
  },
  created() {
    this.fetchTrialStatus()
  },
  methods: {
    async fetchTrialStatus() {
      try {
        const response = await getTrialStatus()
        this.trialInfo = response.data
      } catch (error) {
        this.$message.error('获取试用状态失败')
      }
    },
    formatDate(dateString) {
      if (!dateString) return '未设置'
      const date = new Date(dateString)
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
    }
  }
}
</script>

<style scoped>
.trial-status-container {
  max-width: 600px;
  margin: 40px auto;
  padding: 20px;
}

h1 {
  text-align: center;
  margin-bottom: 30px;
}

.status-card {
  padding: 30px;
  text-align: center;
  margin-bottom: 20px;
}

.status-icon {
  font-size: 48px;
  margin-bottom: 20px;
}

.pending .status-icon {
  color: #e6a23c;
}

.active .status-icon {
  color: #67c23a;
}

.expired .status-icon {
  color: #909399;
}

.rejected .status-icon {
  color: #f56c6c;
}

h2 {
  margin-bottom: 15px;
}

.application-date, .trial-period, .trial-remaining, .reject-reason {
  margin: 15px 0;
  font-size: 14px;
}

.trial-remaining {
  font-weight: bold;
}
</style>
