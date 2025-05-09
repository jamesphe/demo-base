<template>
  <div class="app-container">
    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span>面试准备</span>
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
            >
              {{ interviewer.name }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <!-- 面试准备表单 -->
        <el-form
          ref="preparationForm"
          :model="preparationForm"
          label-width="120px"
          class="preparation-form"
        >
          <!-- 面试关注点 -->
          <el-card class="preparation-card">
            <div slot="header">
              <span>面试关注点</span>
              <el-button
                style="float: right; padding: 3px 0"
                type="text"
                @click="handleSaveFocusPoints"
              >
                保存为模板
              </el-button>
            </div>
            <el-form-item label="技术能力">
              <el-input
                type="textarea"
                :rows="3"
                placeholder="请输入技术能力相关的关注点"
                v-model="preparationForm.technicalFocus"
              />
            </el-form-item>
            <el-form-item label="项目经验">
              <el-input
                type="textarea"
                :rows="3"
                placeholder="请输入项目经验相关的关注点"
                v-model="preparationForm.projectFocus"
              />
            </el-form-item>
            <el-form-item label="综合素质">
              <el-input
                type="textarea"
                :rows="3"
                placeholder="请输入综合素质相关的关注点"
                v-model="preparationForm.comprehensiveFocus"
              />
            </el-form-item>
          </el-card>

          <!-- 面试问题建议 -->
          <el-card class="preparation-card">
            <div slot="header">
              <span>面试问题建议</span>
              <el-button
                style="float: right; padding: 3px 0"
                type="text"
                @click="handleGenerateQuestions"
                :loading="generatingQuestions"
              >
                生成问题
              </el-button>
            </div>
            <div v-if="preparation.questions && preparation.questions.length > 0">
              <div
                v-for="(category, index) in preparation.questions"
                :key="index"
                class="question-category"
              >
                <h4>{{ category.title }}</h4>
                <el-collapse>
                  <el-collapse-item
                    v-for="(question, qIndex) in category.questions"
                    :key="qIndex"
                    :title="question.content"
                  >
                    <div class="question-detail">
                      <div class="reference-answer">
                        <h5>参考答案：</h5>
                        <p>{{ question.referenceAnswer }}</p>
                      </div>
                      <div class="evaluation-points">
                        <h5>评估要点：</h5>
                        <ul>
                          <li v-for="(point, pIndex) in question.evaluationPoints" :key="pIndex">
                            {{ point }}
                          </li>
                        </ul>
                      </div>
                    </div>
                  </el-collapse-item>
                </el-collapse>
              </div>
            </div>
            <div v-else class="empty-tip">
              <el-empty description="暂无面试问题建议" />
            </div>
          </el-card>

          <!-- 候选人背景分析 -->
          <el-card class="preparation-card">
            <div slot="header">
              <span>候选人背景分析</span>
              <el-button
                style="float: right; padding: 3px 0"
                type="text"
                @click="handleGenerateAnalysis"
                :loading="generatingAnalysis"
              >
                生成分析
              </el-button>
            </div>
            <div v-if="preparation.analysis" class="analysis-content">
              <div class="analysis-section">
                <h4>教育背景</h4>
                <p>{{ preparation.analysis.education }}</p>
              </div>
              <div class="analysis-section">
                <h4>工作经验</h4>
                <p>{{ preparation.analysis.experience }}</p>
              </div>
              <div class="analysis-section">
                <h4>技能特长</h4>
                <p>{{ preparation.analysis.skills }}</p>
              </div>
              <div class="analysis-section">
                <h4>潜在风险</h4>
                <p>{{ preparation.analysis.risks }}</p>
              </div>
            </div>
            <div v-else class="empty-tip">
              <el-empty description="暂无背景分析" />
            </div>
          </el-card>

          <!-- 操作按钮 -->
          <div class="form-actions">
            <el-button @click="handleCancel">取 消</el-button>
            <el-button type="primary" @click="handleSave" :loading="saving">保 存</el-button>
          </div>
        </el-form>
      </div>
    </el-card>
  </div>
</template>

<script>
import { mapActions } from 'vuex'
import {
  getInterviewDetail,
  getInterviewPreparation,
  generateInterviewPreparation,
  updateInterviewPreparation,
  getInterviewerFocusPoints,
  saveInterviewerFocusPoints
} from '@/api/interview'

export default {
  name: 'InterviewPreparation',
  data() {
    return {
      loading: false,
      saving: false,
      generatingQuestions: false,
      generatingAnalysis: false,
      interview: {},
      preparation: {},
      preparationForm: {
        technicalFocus: '',
        projectFocus: '',
        comprehensiveFocus: ''
      }
    }
  },
  created() {
    this.getInterviewInfo()
    this.getPreparationInfo()
    this.getFocusPoints()
  },
  methods: {
    ...mapActions('interview', [
      'getInterviewDetail',
      'getInterviewPreparation',
      'generateInterviewPreparation',
      'updateInterviewPreparation',
      'getInterviewerFocusPoints',
      'saveInterviewerFocusPoints'
    ]),
    ...mapActions('ai', [
      'generateQuestions',
      'generateAnalysis',
      'getSuggestions',
      'getEvaluationSuggestions'
    ]),
    async getInterviewInfo() {
      this.loading = true
      try {
        const interviewId = this.$route.params.id
        const interview = await this.getInterviewDetail(interviewId)
        this.interview = interview
      } catch (error) {
        console.error('获取面试信息失败:', error)
        this.$message.error('获取面试信息失败')
      } finally {
        this.loading = false
      }
    },
    async getPreparationInfo() {
      try {
        const interviewId = this.$route.params.id
        const preparation = await this.getInterviewPreparation(interviewId)
        this.preparation = preparation
        if (preparation.focusPoints) {
          this.preparationForm = {
            technicalFocus: preparation.focusPoints.technical || '',
            projectFocus: preparation.focusPoints.project || '',
            comprehensiveFocus: preparation.focusPoints.comprehensive || ''
          }
        }
      } catch (error) {
        console.error('获取面试准备信息失败:', error)
        this.$message.error('获取面试准备信息失败')
      }
    },
    async getFocusPoints() {
      try {
        const focusPoints = await this.getInterviewerFocusPoints()
        if (focusPoints) {
          this.preparationForm = {
            technicalFocus: focusPoints.technical || '',
            projectFocus: focusPoints.project || '',
            comprehensiveFocus: focusPoints.comprehensive || ''
          }
        }
      } catch (error) {
        console.error('获取关注点失败:', error)
      }
    },
    async handleGenerateQuestions() {
      this.generatingQuestions = true
      try {
        const interviewId = this.$route.params.id
        const data = {
          interviewId,
          candidateInfo: {
            name: this.interview.candidateName,
            position: this.interview.candidatePosition,
            resume: this.interview.resume
          },
          focusPoints: this.preparationForm
        }
        
        // 使用AI模块生成问题
        const questions = await this.generateQuestions(data)
        this.preparation.questions = questions
        
        // 获取问题建议
        const suggestions = await this.getSuggestions(data)
        if (suggestions) {
          this.preparation.questions = suggestions.questions
        }
        
        this.$message.success('面试问题生成成功')
      } catch (error) {
        console.error('生成面试问题失败:', error)
        this.$message.error('生成面试问题失败')
      } finally {
        this.generatingQuestions = false
      }
    },
    async handleGenerateAnalysis() {
      this.generatingAnalysis = true
      try {
        const interviewId = this.$route.params.id
        const data = {
          interviewId,
          candidateInfo: {
            name: this.interview.candidateName,
            position: this.interview.candidatePosition,
            resume: this.interview.resume
          },
          focusPoints: this.preparationForm
        }
        
        // 使用AI模块生成分析
        const analysis = await this.generateAnalysis(data)
        this.preparation.analysis = analysis
        
        // 获取评估建议
        const evaluationSuggestions = await this.getEvaluationSuggestions(data)
        if (evaluationSuggestions) {
          this.preparation.analysis = {
            ...this.preparation.analysis,
            evaluationSuggestions: evaluationSuggestions
          }
        }
        
        this.$message.success('背景分析生成成功')
      } catch (error) {
        console.error('生成背景分析失败:', error)
        this.$message.error('生成背景分析失败')
      } finally {
        this.generatingAnalysis = false
      }
    },
    async handleSaveFocusPoints() {
      try {
        await this.saveInterviewerFocusPoints(this.preparationForm)
        this.$message.success('关注点保存成功')
      } catch (error) {
        console.error('保存关注点失败:', error)
        this.$message.error('保存关注点失败')
      }
    },
    async handleSave() {
      this.saving = true
      try {
        const interviewId = this.$route.params.id
        await this.updateInterviewPreparation({
          interviewId,
          data: {
            focusPoints: this.preparationForm,
            questions: this.preparation.questions,
            analysis: this.preparation.analysis
          }
        })
        this.$message.success('保存成功')
        this.$router.push('/interview/schedule')
      } catch (error) {
        console.error('保存失败:', error)
        this.$message.error('保存失败')
      } finally {
        this.saving = false
      }
    },
    handleCancel() {
      this.$router.push('/interview/schedule')
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

.preparation-form {
  .preparation-card {
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

.question-category {
  margin-bottom: 20px;
  
  h4 {
    margin: 0 0 15px;
    padding-left: 10px;
    border-left: 4px solid #409EFF;
    font-size: 16px;
    color: #303133;
  }
  
  .question-detail {
    padding: 15px;
    background-color: #f8f9fa;
    border-radius: 4px;
    
    h5 {
      margin: 0 0 10px;
      color: #606266;
      font-size: 14px;
    }
    
    .reference-answer {
      margin-bottom: 15px;
      
      p {
        margin: 0;
        line-height: 1.6;
        color: #606266;
      }
    }
    
    .evaluation-points {
      ul {
        margin: 0;
        padding-left: 20px;
        
        li {
          margin-bottom: 5px;
          color: #606266;
          
          &:last-child {
            margin-bottom: 0;
          }
        }
      }
    }
  }
}

.analysis-content {
  .analysis-section {
    margin-bottom: 20px;
    
    &:last-child {
      margin-bottom: 0;
    }
    
    h4 {
      margin: 0 0 10px;
      color: #303133;
      font-size: 15px;
    }
    
    p {
      margin: 0;
      line-height: 1.6;
      color: #606266;
    }
  }
}

.empty-tip {
  padding: 30px 0;
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

::v-deep .el-descriptions {
  .el-descriptions-item__label {
    width: 120px;
    font-weight: 500;
  }
}
</style> 