<template>
  <div class="app-container">
    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span>面试评估</span>
      </div>

      <div v-loading="loading">
        <!-- 候选人基本信息 -->
        <el-descriptions :column="3" border class="candidate-info">
          <el-descriptions-item label="候选人">{{ interview.candidateName }}</el-descriptions-item>
          <el-descriptions-item label="应聘职位">{{ interview.candidatePosition }}</el-descriptions-item>
          <el-descriptions-item label="面试类型">
            <el-tag :type="getInterviewTypeTag(interview.type)">
              {{ getInterviewTypeText(interview.type) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="面试时间">{{ formatDateTime(interview.time) }}</el-descriptions-item>
          <el-descriptions-item label="面试地点">{{ interview.location }}</el-descriptions-item>
          <el-descriptions-item label="面试官">
            <el-tag
              v-for="interviewer in interview.interviewers"
              :key="interviewer.id"
              size="mini"
              class="interviewer-tag"
              style="margin-right: 5px;"
            >
              {{ interviewer.name || interviewer.username }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>

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
import { mapActions } from 'vuex'
import { getInterviewDetail, submitInterviewEvaluation } from '@/api/interview'

export default {
  name: 'InterviewEvaluation',
  data() {
    return {
      loading: false,
      submitting: false,
      interview: {},
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
  },
  methods: {
    ...mapActions('interview', [
      'updateInterview'
    ]),
    async getInterviewInfo() {
      this.loading = true
      try {
        const interviewId = this.$route.params.id
        const response = await getInterviewDetail(interviewId)
        this.interview = response.data
      } catch (error) {
        console.error('获取面试信息失败:', error)
        this.$message.error('获取面试信息失败')
      } finally {
        this.loading = false
      }
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
        await submitInterviewEvaluation(interviewId, this.evaluationForm)
        
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
      this.$router.push('/interview/record')
    }
  }
}
</script>

<style lang="scss" scoped>
.app-container {
  padding: 20px;
}

.candidate-info {
  margin-bottom: 20px;
  
  .interviewer-tag {
    margin: 2px;
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

::v-deep .el-descriptions {
  .el-descriptions-item__label {
    width: 120px;
    font-weight: 500;
  }
}
</style> 