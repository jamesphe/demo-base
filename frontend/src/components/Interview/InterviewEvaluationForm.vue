<template>
  <div class="interview-evaluation-form">
    <!-- 面试记录编辑区 -->
    <div class="record-content">
      <div class="section-title">
        <i class="el-icon-edit"></i> 面试过程记录
      </div>
      <el-input
        type="textarea"
        :rows="rows.processRecord"
        placeholder="在此记录面试过程的问答内容、候选人表现等..."
        v-model="formData.processRecord"
        @input="handleContentChange"
      />
    </div>

    <!-- 候选人优势和劣势 -->
    <div class="candidate-evaluation">
      <el-row :gutter="20">
        <el-col :span="12">
          <div class="evaluation-block">
            <div class="block-title">
              <i class="el-icon-star-on"></i> 候选人优势
            </div>
            <el-input
              type="textarea"
              :rows="rows.strengths"
              placeholder="请列出候选人的主要优势..."
              v-model="formData.strengths"
              @input="handleContentChange"
            />
          </div>
        </el-col>
        <el-col :span="12">
          <div class="evaluation-block">
            <div class="block-title">
              <i class="el-icon-warning"></i> 候选人劣势
            </div>
            <el-input
              type="textarea"
              :rows="rows.weaknesses"
              placeholder="请列出候选人的主要劣势..."
              v-model="formData.weaknesses"
              @input="handleContentChange"
            />
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 技术评估详情 -->
    <div class="technical-evaluation">
      <div class="evaluation-title">
        <i class="el-icon-cpu"></i> 技术能力评估
      </div>
      <el-form label-position="top" size="small">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="编码能力">
              <el-rate v-model="formData.technicalEvaluation.coding_ability" @change="handleRatingChange" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="问题解决能力">
              <el-rate v-model="formData.technicalEvaluation.problem_solving" @change="handleRatingChange" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="技术知识水平">
              <el-rate v-model="formData.technicalEvaluation.knowledge" @change="handleRatingChange" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="技术评估备注">
          <el-input 
            type="textarea" 
            :rows="rows.technicalComments" 
            placeholder="技术能力相关备注..." 
            v-model="formData.technicalEvaluation.comments"
            @input="handleContentChange"
          />
        </el-form-item>
      </el-form>
    </div>

    <!-- 综合素质评估 -->
    <div class="comprehensive-evaluation">
      <div class="evaluation-title">
        <i class="el-icon-user"></i> 综合素质评估
      </div>
      <el-form label-position="top" size="small">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="沟通能力">
              <el-rate v-model="formData.comprehensiveEvaluation.communication" @change="handleRatingChange" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="文化契合度">
              <el-rate v-model="formData.comprehensiveEvaluation.cultural_fit" @change="handleRatingChange" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="团队协作">
              <el-rate v-model="formData.comprehensiveEvaluation.teamwork" @change="handleRatingChange" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="综合素质备注">
          <el-input 
            type="textarea" 
            :rows="rows.comprehensiveComments" 
            placeholder="综合素质相关备注..." 
            v-model="formData.comprehensiveEvaluation.comments"
            @input="handleContentChange"
          />
        </el-form-item>
      </el-form>
    </div>

    <!-- 面试官总结 -->
    <div class="record-summary">
      <div class="summary-title">面试总结</div>
      <el-input
        type="textarea"
        :rows="rows.summary"
        placeholder="请总结候选人的整体表现、优势和不足..."
        v-model="formData.summary"
        @input="handleContentChange"
      />
    </div>

    <!-- 招聘建议 -->
    <div class="record-recommendation">
      <div class="recommendation-title">录用建议</div>
      <el-radio-group v-model="formData.recommendation" @change="handleContentChange">
        <el-radio label="strongly_recommend">强烈推荐</el-radio>
        <el-radio label="recommend">推荐</el-radio>
        <el-radio label="neutral">中立</el-radio>
        <el-radio label="not_recommend">不推荐</el-radio>
        <el-radio label="strongly_not_recommend">强烈不推荐</el-radio>
      </el-radio-group>
    </div>

    <!-- 操作按钮（真实使用） -->
    <div class="record-actions">
      <el-button type="primary" @click="handleSaveDraft" :disabled="!isModified">保存草稿</el-button>
      <el-button type="success" @click="handleSubmitRecord" :disabled="!hasContent">完成记录</el-button>
      <el-button @click="handleGoBack">返回</el-button>
    </div>
  </div>
</template>

<script>
import { submitInterviewerFeedback } from '@/api/interview'

export default {
  name: 'InterviewEvaluationForm',
  props: {
    initialData: {
      type: Object,
      default: () => ({})
    },
    showActions: {
      type: Boolean,
      default: true
    },
    rowConfig: {
      type: Object,
      default: () => ({})
    },
    interviewId: {
      type: [String, Number],
      default: ''
    },
    currentUser: {
      type: Object,
      default: () => ({
        id: '',
        name: ''
      })
    }
  },
  data() {
    // 默认表单数据
    const defaultData = {
      processRecord: '',
      summary: '',
      recommendation: 'neutral',
      strengths: '',
      weaknesses: '',
      technicalEvaluation: {
        coding_ability: 3,
        problem_solving: 3,
        knowledge: 3,
        comments: ''
      },
      comprehensiveEvaluation: {
        communication: 3,
        cultural_fit: 3,
        teamwork: 3,
        comments: ''
      }
    }

    // 默认文本域行数
    const defaultRows = {
      processRecord: 15,
      strengths: 4,
      weaknesses: 4,
      technicalComments: 2,
      comprehensiveComments: 2,
      summary: 4
    }

    return {
      formData: { ...defaultData },
      isModified: false,
      rows: { ...defaultRows, ...this.rowConfig },
      loading: false
    }
  },
  computed: {
    hasContent() {
      const processRecordFilled = this.formData.processRecord.trim() !== '';
      const summaryFilled = this.formData.summary.trim() !== '';
      const strengthsFilled = this.formData.strengths.trim() !== '';
      const weaknessesFilled = this.formData.weaknesses.trim() !== '';
      
      return processRecordFilled || summaryFilled || strengthsFilled || weaknessesFilled;
    },
    exportData() {
      const techEval = { ...this.formData.technicalEvaluation }
      const compEval = { ...this.formData.comprehensiveEvaluation }
      
      // 确保comments字段是对象而不是字符串
      if (typeof techEval.comments === 'string') {
        techEval.comments = {
          content: techEval.comments
        }
      }
      
      if (typeof compEval.comments === 'string') {
        compEval.comments = {
          content: compEval.comments
        }
      }
      
      return {
        process_record: this.formData.processRecord,
        summary: this.formData.summary,
        hiring_recommendation: this.formData.recommendation,
        evaluation_score: this.getAverageScore(),
        strengths: this.formData.strengths,
        weaknesses: this.formData.weaknesses,
        technical_evaluation: techEval,
        comprehensive_evaluation: compEval
      }
    }
  },
  created() {
    // 合并初始数据
    if (this.initialData) {
      // 处理顶层属性
      Object.keys(this.formData).forEach(key => {
        if (key in this.initialData && this.initialData[key] !== undefined) {
          if (typeof this.formData[key] === 'object' && !Array.isArray(this.formData[key])) {
            this.formData[key] = { ...this.formData[key], ...this.initialData[key] }
          } else {
            this.formData[key] = this.initialData[key]
          }
        }
      })
    }
  },
  methods: {
    handleContentChange() {
      this.isModified = true
      this.$emit('content-change', this.exportData)
    },
    handleRatingChange() {
      this.isModified = true
      this.$emit('rating-change', this.exportData)
    },
    getAverageScore() {
      // 计算所有评分的平均值作为综合评分
      const scores = [
        this.formData.technicalEvaluation.coding_ability,
        this.formData.technicalEvaluation.problem_solving,
        this.formData.technicalEvaluation.knowledge,
        this.formData.comprehensiveEvaluation.communication,
        this.formData.comprehensiveEvaluation.cultural_fit,
        this.formData.comprehensiveEvaluation.teamwork
      ]
      
      const sum = scores.reduce((acc, score) => acc + score, 0)
      return (sum / scores.length).toFixed(1)
    },
    handleSave() {
      this.$emit('save', this.exportData)
    },
    handleSubmit() {
      this.$emit('submit', this.exportData)
    },
    reset() {
      // 重置为默认值
      this.formData = {
        processRecord: '',
        summary: '',
        recommendation: 'neutral',
        strengths: '',
        weaknesses: '',
        technicalEvaluation: {
          coding_ability: 3,
          problem_solving: 3,
          knowledge: 3,
          comments: ''
        },
        comprehensiveEvaluation: {
          communication: 3,
          cultural_fit: 3,
          teamwork: 3,
          comments: ''
        }
      }
      this.isModified = false
    },
    // 向外暴露获取表单数据的方法
    getFormData() {
      return this.exportData
    },
    // 设置表单数据
    setFormData(data) {
      if (!data) return

      // 处理顶层属性
      if (data.processRecord !== undefined) this.formData.processRecord = data.processRecord
      if (data.summary !== undefined) this.formData.summary = data.summary
      if (data.recommendation !== undefined) this.formData.recommendation = data.recommendation
      if (data.strengths !== undefined) this.formData.strengths = data.strengths
      if (data.weaknesses !== undefined) this.formData.weaknesses = data.weaknesses
      
      // 处理嵌套对象
      if (data.technicalEvaluation) {
        Object.keys(data.technicalEvaluation).forEach(key => {
          if (key in this.formData.technicalEvaluation) {
            this.formData.technicalEvaluation[key] = data.technicalEvaluation[key]
          }
        })
      }
      
      if (data.comprehensiveEvaluation) {
        Object.keys(data.comprehensiveEvaluation).forEach(key => {
          if (key in this.formData.comprehensiveEvaluation) {
            this.formData.comprehensiveEvaluation[key] = data.comprehensiveEvaluation[key]
          }
        })
      }
      
      // 如果传入的数据使用了snake_case，需要特殊处理
      if (data.process_record !== undefined) this.formData.processRecord = data.process_record
      if (data.hiring_recommendation !== undefined) this.formData.recommendation = data.hiring_recommendation
      if (data.technical_evaluation) {
        Object.keys(data.technical_evaluation).forEach(key => {
          if (key in this.formData.technicalEvaluation) {
            this.formData.technicalEvaluation[key] = data.technical_evaluation[key]
          }
        })
      }
      if (data.comprehensive_evaluation) {
        Object.keys(data.comprehensive_evaluation).forEach(key => {
          if (key in this.formData.comprehensiveEvaluation) {
            this.formData.comprehensiveEvaluation[key] = data.comprehensive_evaluation[key]
          }
        })
      }
      
      this.isModified = false
    },
    handleSaveDraft() {
      if (!this.interviewId) {
        this.$emit('save-draft', this.exportData)
        return
      }
      
      this.loading = true
      try {
        const formData = this.exportData
        
        const draft = {
          processRecord: formData.process_record,
          summary: formData.summary,
          recommendation: formData.hiring_recommendation,
          strengths: formData.strengths,
          weaknesses: formData.weaknesses,
          technicalEvaluation: formData.technical_evaluation,
          comprehensiveEvaluation: formData.comprehensive_evaluation,
          timestamp: new Date().getTime()
        }
        
        localStorage.setItem(`interview_draft_${this.interviewId}_${this.currentUser.id}`, JSON.stringify(draft))
        
        this.$message.success('草稿已保存')
        this.isModified = false
        this.$emit('save-draft-success')
      } catch (error) {
        console.error('保存草稿失败:', error)
        this.$message.error('保存草稿失败')
      } finally {
        this.loading = false
        this.$emit('loading-change', false)
      }
    },
    async handleSubmitRecord() {
      if (!this.hasContent) {
        this.$message.warning('请先记录面试内容或总结')
        return
      }

      if (!this.interviewId) {
        this.$emit('submit-record', this.exportData)
        return
      }
      
      this.loading = true
      try {
        const feedbackData = { ...this.exportData }
        
        // 确保comments字段是对象而不是字符串
        if (typeof feedbackData.technical_evaluation.comments === 'string') {
          feedbackData.technical_evaluation.comments = {
            content: feedbackData.technical_evaluation.comments
          }
        }
        
        if (typeof feedbackData.comprehensive_evaluation.comments === 'string') {
          feedbackData.comprehensive_evaluation.comments = {
            content: feedbackData.comprehensive_evaluation.comments
          }
        }
        
        await submitInterviewerFeedback(this.interviewId, feedbackData)
        
        localStorage.removeItem(`interview_draft_${this.interviewId}_${this.currentUser.id}`)
        
        this.$emit('submit-record-success')
      } catch (error) {
        console.error('提交面试记录失败:', error)
        this.$message.error('提交面试记录失败: ' + (error.response?.data?.message || error.message))
      } finally {
        this.loading = false
        this.$emit('loading-change', false)
      }
    },
    handleGoBack() {
      this.$emit('go-back')
    }
  }
}
</script>

<style lang="scss" scoped>
.interview-evaluation-form {
  margin-bottom: 20px;
}

.section-title, 
.block-title,
.evaluation-title,
.summary-title,
.recommendation-title {
  font-weight: 500;
  font-size: 16px;
  margin-bottom: 10px;
  color: #303133;
  display: flex;
  align-items: center;
  
  i {
    margin-right: 8px;
    color: #409EFF;
  }
}

.record-content,
.record-summary, 
.record-recommendation {
  margin-bottom: 20px;
}

.technical-evaluation, 
.comprehensive-evaluation {
  margin: 20px 0;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 4px;
  
  .evaluation-title {
    font-weight: 500;
    font-size: 16px;
    margin-bottom: 15px;
    color: #303133;
    
    i {
      color: #409EFF;
      margin-right: 5px;
    }
  }
}

.candidate-evaluation {
  margin: 20px 0;
  
  .evaluation-block {
    background-color: #f8f9fa;
    border-radius: 4px;
    padding: 15px;
    height: 100%;
    
    .block-title {
      font-weight: 500;
      font-size: 16px;
      margin-bottom: 10px;
      color: #303133;
      
      i {
        margin-right: 5px;
      }
    }
    
    .el-icon-star-on {
      color: #E6A23C;
    }
    
    .el-icon-warning {
      color: #F56C6C;
    }
  }
}

.form-actions {
  margin-top: 30px;
  display: flex;
  justify-content: center;
  
  .el-button {
    min-width: 100px;
    margin: 0 10px;
  }
}

.record-actions {
  margin-top: 30px;
  display: flex;
  justify-content: center;
  
  .el-button {
    min-width: 100px;
    margin: 0 10px;
  }
}
</style> 