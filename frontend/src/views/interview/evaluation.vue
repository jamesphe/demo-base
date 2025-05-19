<template>
  <div class="app-container">
    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span>面试评估</span>
      </div>

      <div v-loading="loading">
        <!-- 候选人基本信息 -->
        <interview-basic-info 
          :interview="interview"
          :current-user="currentUser"
          @show-contact-info="showContactInfo"
          @view-resume="viewResume"
        />

        <!-- 面试官反馈汇总 -->
        <el-card class="feedback-summary-card" v-if="feedbackSummary">
          <div slot="header" class="clearfix">
            <span>面试官反馈汇总</span>
            <el-button style="float: right; padding: 3px 0" type="text" @click="refreshFeedbackSummary">
              <i class="el-icon-refresh"></i> 刷新
            </el-button>
          </div>
          
          <!-- 评分概览 -->
          <div class="summary-stats">
            <div class="stat-item">
              <div class="stat-value">{{ feedbackSummary.average_score ? feedbackSummary.average_score.toFixed(1) : '0.0' }}</div>
              <div class="stat-label">平均评分</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ feedbackSummary.completed_count || 0 }}</div>
              <div class="stat-label">已提交</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ (feedbackSummary.interviewer_count || 0) - (feedbackSummary.completed_count || 0) }}</div>
              <div class="stat-label">待提交</div>
            </div>
          </div>
          
          <!-- 面试官详细反馈表格 -->
          <el-table :data="feedbackSummary.feedbacks || []" style="width: 100%; margin-top: 20px;" border>
            <el-table-column label="面试官" prop="interviewer_name" width="150">
              <template slot-scope="scope">
                <span>{{ scope.row.interviewer_name || '未知面试官' }}</span>
              </template>
            </el-table-column>
            <el-table-column label="综合评分">
              <template slot-scope="scope">
                <el-rate
                  v-model="scope.row.evaluation_score"
                  disabled
                  show-score
                  text-color="#ff9900"
                />
              </template>
            </el-table-column>
            <el-table-column label="招聘建议" width="150">
              <template slot-scope="scope">
                <el-tag :type="getRecommendationTagType(scope.row.hiring_recommendation)">
                  {{ getRecommendationText(scope.row.hiring_recommendation) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="反馈状态" width="100">
              <template slot-scope="scope">
                <el-tag :type="scope.row.status === 'completed' ? 'success' : 'warning'" size="mini">
                  {{ scope.row.status === 'completed' ? '已完成' : '待完成' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120" align="center">
              <template slot-scope="scope">
                <el-button 
                  type="primary" 
                  size="mini" 
                  @click="viewFeedbackDetail(scope.row)"
                  :disabled="scope.row.status !== 'completed'"
                  plain
                >
                  查看详情
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          
          <!-- 关键优势和劣势 -->
          <div class="key-points" v-if="feedbackSummary.key_strengths && feedbackSummary.key_strengths.length">
            <h4>关键优势</h4>
            <ul>
              <li v-for="(strength, index) in feedbackSummary.key_strengths" :key="'strength-' + index">
                {{ strength }}
              </li>
            </ul>
          </div>
          
          <div class="key-points" v-if="feedbackSummary.key_weaknesses && feedbackSummary.key_weaknesses.length">
            <h4>关键劣势</h4>
            <ul>
              <li v-for="(weakness, index) in feedbackSummary.key_weaknesses" :key="'weakness-' + index">
                {{ weakness }}
              </li>
            </ul>
          </div>
        </el-card>

        <!-- 使用FeedbackDetailDialog组件替换原来的反馈详情对话框 -->
        <feedback-detail-dialog
          :visible.sync="dialogVisible"
          :feedback="selectedFeedback"
          title="面试官反馈详情"
        />

        <!-- 评估表单 -->
        <el-form
          ref="evaluationForm"
          :model="evaluationForm"
          :rules="evaluationRules"
          label-width="120px"
          class="evaluation-form"
        >
          <!-- 技术能力评估 -->
          <el-card class="evaluation-card">
            <div slot="header">
              <span>技术能力评估</span>
            </div>
            <el-form-item label="专业技能" prop="technicalScore">
              <el-rate
                v-model="evaluationForm.technicalScore"
                :max="5"
                show-score
                text-color="#ff9900"
              />
            </el-form-item>
            <el-form-item label="技术深度" prop="technicalDepth">
              <el-rate
                v-model="evaluationForm.technicalDepth"
                :max="5"
                show-score
                text-color="#ff9900"
              />
            </el-form-item>
            <el-form-item label="技术广度" prop="technicalBreadth">
              <el-rate
                v-model="evaluationForm.technicalBreadth"
                :max="5"
                show-score
                text-color="#ff9900"
              />
            </el-form-item>
            <el-form-item label="技术评价" prop="technicalComments">
              <el-input
                type="textarea"
                :rows="3"
                placeholder="请详细评价候选人的技术能力"
                v-model="evaluationForm.technicalComments"
              />
            </el-form-item>
          </el-card>

          <!-- 沟通能力评估 -->
          <el-card class="evaluation-card">
            <div slot="header">
              <span>沟通能力评估</span>
            </div>
            <el-form-item label="表达能力" prop="communicationScore">
              <el-rate
                v-model="evaluationForm.communicationScore"
                :max="5"
                show-score
                text-color="#ff9900"
              />
            </el-form-item>
            <el-form-item label="团队协作" prop="teamworkScore">
              <el-rate
                v-model="evaluationForm.teamworkScore"
                :max="5"
                show-score
                text-color="#ff9900"
              />
            </el-form-item>
            <el-form-item label="沟通评价" prop="communicationComments">
              <el-input
                type="textarea"
                :rows="3"
                placeholder="请详细评价候选人的沟通能力"
                v-model="evaluationForm.communicationComments"
              />
            </el-form-item>
          </el-card>

          <!-- 项目经验评估 -->
          <el-card class="evaluation-card">
            <div slot="header">
              <span>项目经验评估</span>
            </div>
            <el-form-item label="项目经验" prop="projectExperienceScore">
              <el-rate
                v-model="evaluationForm.projectExperienceScore"
                :max="5"
                show-score
                text-color="#ff9900"
              />
            </el-form-item>
            <el-form-item label="问题解决" prop="problemSolvingScore">
              <el-rate
                v-model="evaluationForm.problemSolvingScore"
                :max="5"
                show-score
                text-color="#ff9900"
              />
            </el-form-item>
            <el-form-item label="经验评价" prop="projectComments">
              <el-input
                type="textarea"
                :rows="3"
                placeholder="请详细评价候选人的项目经验"
                v-model="evaluationForm.projectComments"
              />
            </el-form-item>
          </el-card>

          <!-- 综合评估 -->
          <el-card class="evaluation-card">
            <div slot="header">
              <span>综合评估</span>
            </div>
            <el-form-item label="综合评分" prop="overallScore">
              <el-rate
                v-model="evaluationForm.overallScore"
                :max="5"
                show-score
                text-color="#ff9900"
              />
            </el-form-item>
            <el-form-item label="评估结果" prop="result">
              <el-radio-group v-model="evaluationForm.result">
                <el-radio label="pass">通过</el-radio>
                <el-radio label="fail">不通过</el-radio>
                <el-radio label="pending">待定</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="综合意见" prop="comments">
              <el-input
                type="textarea"
                :rows="4"
                placeholder="请详细说明评估结果的理由和建议"
                v-model="evaluationForm.comments"
              />
            </el-form-item>
          </el-card>

          <!-- 提交按钮 -->
          <div class="form-actions">
            <el-button @click="handleCancel">取 消</el-button>
            <el-button type="primary" @click="handleSubmit" :loading="submitting">提 交</el-button>
          </div>
        </el-form>
      </div>
    </el-card>
  </div>
</template>

<script>
import { mapActions, mapGetters } from 'vuex'
import DescriptionList from '@/components/DescriptionList'
import DescriptionItem from '@/components/DescriptionList/Item'
import InterviewBasicInfo from '@/components/InterviewBasicInfo'
import FeedbackDetailDialog from '@/components/FeedbackDetailDialog'

export default {
  name: 'InterviewEvaluation',
  components: {
    DescriptionList,
    DescriptionItem,
    InterviewBasicInfo,
    FeedbackDetailDialog
  },
  data() {
    return {
      loading: false,
      submitting: false,
      interview: {},
      feedbackSummary: null,
      dialogVisible: false,
      selectedFeedback: null,
      currentUser: null,
      evaluationForm: {
        technicalScore: 0,
        technicalDepth: 0,
        technicalBreadth: 0,
        technicalComments: '',
        communicationScore: 0,
        teamworkScore: 0,
        communicationComments: '',
        projectExperienceScore: 0,
        problemSolvingScore: 0,
        projectComments: '',
        overallScore: 0,
        result: '',
        comments: ''
      },
      evaluationRules: {
        technicalScore: [
          { required: true, message: '请评价专业技能', trigger: 'change' }
        ],
        communicationScore: [
          { required: true, message: '请评价表达能力', trigger: 'change' }
        ],
        projectExperienceScore: [
          { required: true, message: '请评价项目经验', trigger: 'change' }
        ],
        overallScore: [
          { required: true, message: '请给出综合评分', trigger: 'change' }
        ],
        result: [
          { required: true, message: '请选择评估结果', trigger: 'change' }
        ],
        comments: [
          { required: true, message: '请填写综合意见', trigger: 'blur' }
        ]
      }
    }
  },
  created() {
    this.getInterviewInfo()
    this.getCurrentUser()
  },
  methods: {
    ...mapActions('interview', [
      'updateInterview',
      'getInterviewDetail',
      'submitInterviewEvaluation',
      'getInterviewFeedbackSummary'
    ]),
    async getCurrentUser() {
      // 从store中获取当前用户信息
      try {
        this.currentUser = this.$store.getters.user
      } catch (error) {
        console.error('获取当前用户信息失败:', error)
      }
    },
    async getInterviewInfo() {
      this.loading = true
      try {
        const interviewId = this.$route.params.id
        const response = await this.getInterviewDetail(interviewId)
        
        // 修复映射逻辑，确保将API响应正确映射到组件数据结构
        this.interview = {
          id: response.data?.id || response.id,
          candidateName: response.data?.resume?.name || response.resume?.name || response.resumeTitle || '-',
          candidatePosition: response.data?.job?.title || response.job?.title || response.jobTitle || '-',
          type: response.data?.interviewType || response.interviewType || 'first',
          time: response.data?.scheduleTime || response.scheduleTime,
          location: response.data?.location || response.location || '-',
          interviewers: response.data?.interviewers || response.interviewers || [],
          resumeId: response.data?.resume?.id || response.resume?.id || null
        }
        
        // 获取面试反馈汇总
        await this.getFeedbackSummary()
      } catch (error) {
        console.error('获取面试信息失败:', error)
        this.$message.error('获取面试信息失败')
      } finally {
        this.loading = false
      }
    },
    async getFeedbackSummary() {
      try {
        const interviewId = this.$route.params.id
        const response = await this.getInterviewFeedbackSummary(interviewId)
        this.feedbackSummary = response.data || response
      } catch (error) {
        console.error('获取面试反馈汇总失败:', error)
        // 这里不显示错误消息，因为可能尚无反馈
      }
    },
    async refreshFeedbackSummary() {
      try {
        await this.getFeedbackSummary()
        this.$message.success('反馈数据已刷新')
      } catch (error) {
        this.$message.error('刷新反馈数据失败')
      }
    },
    viewFeedbackDetail(feedback) {
      this.selectedFeedback = feedback
      this.dialogVisible = true
    },
    getRecommendationText(recommendation) {
      const map = {
        highly_recommended: '强烈推荐',
        recommended: '推荐',
        recommend_with_reservations: '有条件推荐',
        not_recommended: '不推荐',
        strongly_not_recommended: '强烈不推荐'
      }
      return map[recommendation] || '未评价'
    },
    getRecommendationTagType(recommendation) {
      const map = {
        highly_recommended: 'success',
        recommended: 'success',
        recommend_with_reservations: 'warning',
        not_recommended: 'danger',
        strongly_not_recommended: 'danger'
      }
      return map[recommendation] || 'info'
    },
    getInterviewTypeText(type) {
      const typeMap = {
        first: '初试',
        second: '复试',
        final: '终试'
      }
      return typeMap[type] || '面试'
    },
    getInterviewTypeTag(type) {
      const tagMap = {
        first: 'primary',
        second: 'success',
        final: 'warning'
      }
      return tagMap[type] || 'info'
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
    async handleSubmit() {
      try {
        await this.$refs.evaluationForm.validate()
        
        this.submitting = true
        const interviewId = this.$route.params.id
        
        // 提交评估结果
        await this.submitInterviewEvaluation({ id: interviewId, data: this.evaluationForm })
        
        // 更新面试状态
        await this.updateInterview({
          id: interviewId,
          data: { status: 'completed' }
        })
        
        this.$message.success('评估提交成功')
        this.$router.push('/interview/record')
      } catch (error) {
        if (error !== 'cancel') {
          console.error('提交评估失败:', error)
          this.$message.error('提交评估失败')
        }
      } finally {
        this.submitting = false
      }
    },
    handleCancel() {
      this.$router.push('/interview/evaluation-list')
    },
    showContactInfo() {
      this.$message.info('显示候选人联系方式功能待实现')
      // 这里可以实现显示候选人联系方式的逻辑，如弹出对话框等
    },
    viewResume() {
      // 如果有简历ID，可以跳转到简历详情页面
      if (this.interview && this.interview.resumeId) {
        this.$router.push(`/resume/detail/${this.interview.resumeId}`)
      } else {
        this.$message.info('暂无简历信息')
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.app-container {
  padding: 20px;
}

:deep(.description-list) {
  background-color: #fff;
  border: 1px solid #ebeef5;
  border-radius: 4px;
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

.evaluation-form {
  .evaluation-card {
    margin-bottom: 20px;
    
    ::v-deep .el-card__header {
      padding: 15px 20px;
      font-weight: 500;
      background-color: #f5f7fa;
    }
    
    ::v-deep .el-form-item {
      margin-bottom: 22px;
      
      &:last-child {
        margin-bottom: 0;
      }
    }
  }
}

.form-actions {
  text-align: center;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
  
  .el-button {
    min-width: 120px;
  }
}

::v-deep .el-rate {
  margin-top: 8px;
}

.feedback-summary-card {
  margin-bottom: 20px;
}

.summary-stats {
  display: flex;
  justify-content: space-around;
  margin-bottom: 20px;
  
  .stat-item {
    text-align: center;
    
    .stat-value {
      font-size: 24px;
      font-weight: bold;
      color: #409EFF;
    }
    
    .stat-label {
      font-size: 14px;
      color: #909399;
      margin-top: 5px;
    }
  }
}

.key-points {
  margin-top: 20px;
  
  h4 {
    font-size: 16px;
    margin-bottom: 10px;
    color: #303133;
  }
  
  ul {
    padding-left: 20px;
    
    li {
      margin-bottom: 5px;
    }
  }
}

.feedback-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  
  h4 {
    margin: 0;
  }
}

.feedback-card {
  margin-bottom: 15px;
  
  .feedback-content {
    padding: 5px 0;
    
    .feedback-item {
      margin-bottom: 15px;
      
      h5 {
        margin: 0 0 5px 0;
        font-size: 14px;
        color: #606266;
      }
      
      p {
        margin: 0;
        color: #303133;
      }
    }
  }
}
</style> 