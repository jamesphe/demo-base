<template>
  <div class="app-container">
    <div class="page-header">
      <el-page-header @back="goBack" title="返回面试列表" :content="pageTitle" />
    </div>
    
    <div v-loading="loading">
      <el-row :gutter="20">
        <el-col :span="24">
          <!-- 候选人基本信息 -->
          <el-card class="box-card">
            <div slot="header" class="clearfix">
              <span>面试信息</span>
              <el-tag :type="getInterviewStatusType" style="float: right">
                {{ getInterviewStatusText }}
              </el-tag>
            </div>
            
            <description-list :column="3" :border="true">
              <description-item label="候选人">{{ interview.candidateName }}</description-item>
              <description-item label="应聘职位">{{ interview.candidatePosition }}</description-item>
              <description-item label="面试类型">
                <el-tag :type="getInterviewTypeTag">
                  {{ getInterviewTypeText }}
                </el-tag>
              </description-item>
              <description-item label="面试时间">{{ formatDateTime(interview.schedule_time) }}</description-item>
              <description-item label="面试地点">{{ interview.location || '-' }}</description-item>
              <description-item label="面试官">
                <el-tag
                  v-for="interviewer in interview.interviewers"
                  :key="interviewer.id"
                  size="mini"
                  class="interviewer-tag"
                >
                  {{ interviewer.name || interviewer.username }}
                </el-tag>
              </description-item>
            </description-list>
          </el-card>
        </el-col>
      </el-row>
      
      <el-row :gutter="20" style="margin-top: 20px">
        <el-col :span="24">
          <!-- 评估结果展示 -->
          <evaluation-result 
            v-if="evaluation" 
            :evaluation="evaluation" 
          />
          <el-card v-else class="box-card">
            <div class="empty-evaluation">
              <el-empty description="暂无评估结果" />
              <el-button 
                type="primary" 
                @click="goToEvaluation" 
                v-if="canEvaluate"
              >
                进行评估
              </el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <el-row :gutter="20">
        <el-col :span="24">
          <!-- 下一步操作 -->
          <next-step-actions
            v-if="evaluation && userCanPerformActions"
            :interview-id="interviewId"
            :interview-type="interview.type"
            :evaluation="evaluation"
            :interviewers="allInterviewers"
            @action-completed="handleActionCompleted"
          />
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script>
import { mapActions, mapGetters } from 'vuex'
import { getInterviewDetail } from '@/api/interview'
import EvaluationResult from '@/components/Interview/EvaluationResult'
import NextStepActions from '@/components/Interview/NextStepActions'
import DescriptionList from '@/components/DescriptionList'
import DescriptionItem from '@/components/DescriptionList/Item'

export default {
  name: 'ViewInterviewEvaluation',
  components: {
    EvaluationResult,
    NextStepActions,
    DescriptionList,
    DescriptionItem
  },
  data() {
    return {
      loading: false,
      interviewId: this.$route.params.id,
      interview: {},
      allInterviewers: []
    }
  },
  computed: {
    ...mapGetters([
      'roles',
      'userId'
    ]),
    ...mapGetters('interview/evaluation', [
      'evaluation'
    ]),
    pageTitle() {
      return `面试评估 - ${this.interview.candidateName || ''}`
    },
    getInterviewTypeText() {
      const typeMap = {
        first: '初试',
        second: '复试',
        final: '终试'
      }
      return typeMap[this.interview.type] || '面试'
    },
    getInterviewTypeTag() {
      const tagMap = {
        first: 'primary',
        second: 'success',
        final: 'warning'
      }
      return tagMap[this.interview.type] || 'info'
    },
    getInterviewStatusText() {
      const statusMap = {
        scheduled: '待面试',
        in_progress: '进行中',
        completed: '已完成',
        evaluated: '已评估',
        cancelled: '已取消'
      }
      return statusMap[this.interview.status] || this.interview.status
    },
    getInterviewStatusType() {
      const typeMap = {
        scheduled: 'info',
        in_progress: 'warning',
        completed: 'success',
        evaluated: 'success',
        cancelled: 'danger'
      }
      return typeMap[this.interview.status] || 'info'
    },
    canEvaluate() {
      // 只有管理员和HR可以评估
      const allowedRoles = ['admin', 'tenant_admin', 'tenant_hr']
      return this.roles.some(role => allowedRoles.includes(role)) && 
        this.interview.status === 'completed'
    },
    userCanPerformActions() {
      // 只有管理员和HR可以执行下一步操作
      const allowedRoles = ['admin', 'tenant_admin', 'tenant_hr']
      return this.roles.some(role => allowedRoles.includes(role))
    }
  },
  created() {
    this.fetchData()
  },
  methods: {
    ...mapActions('interview/evaluation', [
      'getEvaluation'
    ]),
    ...mapActions('user', [
      'getInterviewers'
    ]),
    async fetchData() {
      this.loading = true
      try {
        // 获取面试详情
        const interviewResponse = await getInterviewDetail(this.interviewId)
        this.interview = interviewResponse.data
        
        // 获取评估结果
        await this.getEvaluation(this.interviewId)
        
        // 获取面试官列表
        const interviewersResponse = await this.getInterviewers()
        this.allInterviewers = interviewersResponse.data || []
      } catch (error) {
        console.error('获取面试评估数据失败:', error)
        this.$message.error('获取面试评估数据失败')
      } finally {
        this.loading = false
      }
    },
    formatDateTime(timestamp) {
      if (!timestamp) return '-'
      const date = new Date(timestamp)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    goBack() {
      this.$router.push('/interview/record')
    },
    goToEvaluation() {
      this.$router.push(`/interview/evaluation/${this.interviewId}`)
    },
    handleActionCompleted() {
      this.$message.success('操作已完成')
      this.fetchData()
    }
  }
}
</script>

<style lang="scss" scoped>
.app-container {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.interviewer-tag {
  margin: 0 5px 5px 0;
}

:deep(.description-list) {
  background-color: #fff;
  padding: 16px;
  
  .description-term {
    line-height: 1.5;
    padding-right: 10px;
    font-weight: 500;
  }
  
  .description-detail {
    line-height: 1.5;
    padding: 0 10px;
  }
}

.empty-evaluation {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px 0;
  
  .el-button {
    margin-top: 20px;
  }
}
</style> 