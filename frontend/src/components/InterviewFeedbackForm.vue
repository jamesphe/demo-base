<template>
  <div class="interview-feedback-form">
    <!-- 顶部标题栏 -->
    <div class="page-header">
      <div class="title">
        <i class="el-icon-document"></i> 面试记录
      </div>
      <div class="header-actions">
        <el-button type="primary" icon="el-icon-back" size="medium" @click="goBack">返回汇总页面</el-button>
      </div>
    </div>

    <!-- 顶部按钮栏 -->
    <div class="action-toolbar">
      <div class="action-buttons">
        <el-button size="small" icon="el-icon-time" @click="addTimestamp">添加时间戳</el-button>
        <el-button size="small" icon="el-icon-star-on" @click="saveKeyPoint">记录关键点</el-button>
        <el-button size="small" icon="el-icon-document" @click="recordQuestion">记录题目不足</el-button>
        <el-button size="small" icon="el-icon-mic" @click="recordDifficulity">记录难题</el-button>
      </div>
      <div class="timer-control">
        <span class="timer">{{ formatTime(recordingTime) }}</span>
        <el-button v-if="!isRecording" type="primary" size="small" icon="el-icon-video-play" @click="startRecording">开始</el-button>
        <el-button v-else type="danger" size="small" icon="el-icon-video-pause" @click="stopRecording">停止</el-button>
      </div>
    </div>

    <el-form
      ref="feedbackForm"
      :model="feedbackForm"
      :rules="feedbackRules"
      label-width="0"
    >
      <!-- 面试记录文本框 -->
      <el-form-item prop="process_record">
        <el-input
          type="textarea"
          :rows="12"
          placeholder="在此记录面试过程中的问题与答案..."
          v-model="feedbackForm.process_record"
          class="record-textarea"
        />
      </el-form-item>

      <!-- 快速评分 -->
      <div class="quick-scores-section">
        <div class="section-title">快速评分</div>
        <div class="score-items">
          <div class="score-item">
            <div class="score-label">技术能力</div>
            <el-rate v-model="feedbackForm.technical_evaluation.coding_ability" :max="5" />
          </div>
          <div class="score-item">
            <div class="score-label">沟通能力</div>
            <el-rate v-model="feedbackForm.comprehensive_evaluation.communication" :max="5" />
          </div>
          <div class="score-item">
            <div class="score-label">解决问题</div>
            <el-rate v-model="feedbackForm.technical_evaluation.problem_solving" :max="5" />
          </div>
          <div class="score-item">
            <div class="score-label">文化契合</div>
            <el-rate v-model="feedbackForm.comprehensive_evaluation.culture_fit" :max="5" />
          </div>
          <div class="score-item">
            <div class="score-label">综合评价</div>
            <el-rate v-model="feedbackForm.evaluation_score" :max="5" />
          </div>
        </div>
      </div>

      <!-- 面试总结 -->
      <div class="summary-section">
        <div class="section-title">面试总结</div>
        <el-form-item prop="feedback">
          <el-input
            type="textarea"
            :rows="6"
            placeholder="请总结候选人的整体表现，优势，劣势..."
            v-model="feedbackForm.feedback"
          />
        </el-form-item>
      </div>

      <!-- 招聘建议 -->
      <div class="recommendation-section">
        <div class="section-title">招聘建议</div>
        <el-form-item prop="hiring_recommendation">
          <div class="recommendation-options">
            <el-radio v-model="feedbackForm.hiring_recommendation" label="strong_recommend">强烈推荐</el-radio>
            <el-radio v-model="feedbackForm.hiring_recommendation" label="recommend">推荐</el-radio>
            <el-radio v-model="feedbackForm.hiring_recommendation" label="neutral">中立</el-radio>
            <el-radio v-model="feedbackForm.hiring_recommendation" label="not_recommend">不推荐</el-radio>
            <el-radio v-model="feedbackForm.hiring_recommendation" label="strong_not_recommend">强烈不推荐</el-radio>
          </div>
        </el-form-item>
      </div>

      <!-- 提交按钮 -->
      <div class="form-actions">
        <el-button type="primary" @click="handleSubmit" :loading="submitting">提交面试记录</el-button>
      </div>
    </el-form>
  </div>
</template>

<script>
export default {
  name: 'InterviewFeedbackForm',
  props: {
    interview: {
      type: Object,
      required: true
    },
    interviewer: {
      type: Object,
      required: true,
      default: () => ({
        id: '',
        name: '',
        username: ''
      })
    },
    existingFeedback: {
      type: Object,
      default: null
    },
    submitting: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      feedbackForm: {
        interview_id: null,
        interviewer_id: null,
        process_record: '',
        technical_evaluation: {
          coding_ability: 0,
          problem_solving: 0,
          system_design: 0,
          algorithm_understanding: 0,
          knowledge_depth: 0,
          knowledge_breadth: 0,
          comments: {
            codingAbility: '',
            problemSolving: ''
          }
        },
        comprehensive_evaluation: {
          communication: 0,
          teamwork: 0,
          learning_ability: 0,
          pressure_handling: 0,
          culture_fit: 0,
          comments: {
            communication: '',
            culturalFit: ''
          }
        },
        evaluation_score: 0,
        strengths: '',
        weaknesses: '',
        hiring_recommendation: '',
        feedback: '',
        preparation_notes: ''
      },
      timer: null,
      recordingTime: 0,
      isRecording: false,
      feedbackRules: {
        process_record: [
          { required: true, message: '请填写面试记录', trigger: 'blur' }
        ],
        evaluation_score: [
          { required: true, message: '请给出综合得分', trigger: 'change' }
        ],
        hiring_recommendation: [
          { required: true, message: '请选择招聘建议', trigger: 'change' }
        ]
      }
    }
  },
  created() {
    this.initFormData()
  },
  methods: {
    // 确保值是字符串类型
    ensureString(value) {
      if (value === undefined || value === null) return ''
      if (typeof value === 'string') return value
      if (typeof value === 'object') return JSON.stringify(value)
      return String(value)
    },
    
    // 确保值是数字类型
    ensureNumber(value) {
      if (value === undefined || value === null) return 0
      if (typeof value === 'number') return value
      if (typeof value === 'string') {
        const num = parseFloat(value)
        return isNaN(num) ? 0 : num
      }
      return 0
    },
    
    // 初始化comments对象
    ensureCommentsObject(commentsObj, defaultFields) {
      if (!commentsObj || typeof commentsObj !== 'object') {
        return defaultFields
      }
      
      // 如果comments是字符串类型，尝试转换为对象
      if (typeof commentsObj === 'string') {
        try {
          const parsed = JSON.parse(commentsObj)
          if (typeof parsed === 'object') {
            // 确保有所有必要的字段
            return { ...defaultFields, ...parsed }
          }
        } catch (e) {
          // 如果解析失败，返回默认对象
          console.warn('无法解析comments字符串:', commentsObj)
          return defaultFields
        }
      }
      
      // 确保有所有必要的字段
      return { ...defaultFields, ...commentsObj }
    },
    
    initFormData() {
      // 设置面试和面试官ID
      this.feedbackForm.interview_id = this.interview.id
      this.feedbackForm.interviewer_id = this.interviewer?.id || ''

      // 如果有现有的反馈数据，填充表单
      if (this.existingFeedback) {
        // 复制评估数据 - 确保类型正确
        this.feedbackForm.evaluation_score = this.ensureNumber(this.existingFeedback.evaluation_score)
        this.feedbackForm.strengths = this.ensureString(this.existingFeedback.strengths)
        this.feedbackForm.weaknesses = this.ensureString(this.existingFeedback.weaknesses)
        this.feedbackForm.hiring_recommendation = this.ensureString(this.existingFeedback.hiring_recommendation)
        this.feedbackForm.feedback = this.ensureString(this.existingFeedback.feedback)
        this.feedbackForm.preparation_notes = this.ensureString(this.existingFeedback.preparation_notes)
        this.feedbackForm.process_record = this.ensureString(this.existingFeedback.process_record || '')
        
        // 复制技术评估 - 确保类型正确
        if (this.existingFeedback.technical_evaluation) {
          const techEval = this.existingFeedback.technical_evaluation
          
          // 确保数值字段是数字
          this.feedbackForm.technical_evaluation.coding_ability = this.ensureNumber(techEval.coding_ability)
          this.feedbackForm.technical_evaluation.problem_solving = this.ensureNumber(techEval.problem_solving)
          this.feedbackForm.technical_evaluation.system_design = this.ensureNumber(techEval.system_design)
          this.feedbackForm.technical_evaluation.algorithm_understanding = this.ensureNumber(techEval.algorithm_understanding)
          this.feedbackForm.technical_evaluation.knowledge_depth = this.ensureNumber(techEval.knowledge_depth)
          this.feedbackForm.technical_evaluation.knowledge_breadth = this.ensureNumber(techEval.knowledge_breadth)
          
          // 确保comments字段是对象
          const defaultTechComments = { 
            codingAbility: '', 
            problemSolving: '' 
          }
          this.feedbackForm.technical_evaluation.comments = 
            this.ensureCommentsObject(techEval.comments, defaultTechComments)
        }

        // 复制综合评估 - 确保类型正确
        if (this.existingFeedback.comprehensive_evaluation) {
          const compEval = this.existingFeedback.comprehensive_evaluation
          
          // 确保数值字段是数字
          this.feedbackForm.comprehensive_evaluation.communication = this.ensureNumber(compEval.communication)
          this.feedbackForm.comprehensive_evaluation.teamwork = this.ensureNumber(compEval.teamwork)
          this.feedbackForm.comprehensive_evaluation.learning_ability = this.ensureNumber(compEval.learning_ability)
          this.feedbackForm.comprehensive_evaluation.pressure_handling = this.ensureNumber(compEval.pressure_handling)
          this.feedbackForm.comprehensive_evaluation.culture_fit = this.ensureNumber(compEval.culture_fit)
          
          // 确保comments字段是对象
          const defaultCompComments = { 
            communication: '', 
            culturalFit: '' 
          }
          this.feedbackForm.comprehensive_evaluation.comments = 
            this.ensureCommentsObject(compEval.comments, defaultCompComments)
        }
      }
    },
    async handleSubmit() {
      try {
        await this.$refs.feedbackForm.validate()
        this.$emit('submit', this.feedbackForm)
      } catch (error) {
        // 验证失败
      }
    },
    handleCancel() {
      this.$emit('cancel')
    },
    resetForm() {
      this.$refs.feedbackForm.resetFields()
      this.initFormData()
    },
    // 添加时间戳
    addTimestamp() {
      const now = new Date()
      const timestamp = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`
      this.feedbackForm.process_record += `\n[${timestamp}] `
    },
    
    // 记录关键点
    saveKeyPoint() {
      this.feedbackForm.process_record += '\n【关键点】 '
    },
    
    // 记录面试题目
    recordQuestion() {
      this.feedbackForm.process_record += '\n【题目不足】 '
    },
    
    // 记录难题
    recordDifficulity() {
      this.feedbackForm.process_record += '\n【难题】 '
    },
    
    // 开始记录
    startRecording() {
      if (!this.isRecording) {
        this.isRecording = true
        this.recordingTime = 0
        this.timer = setInterval(() => {
          this.recordingTime++
        }, 1000)
      }
    },
    
    // 停止记录
    stopRecording() {
      if (this.isRecording) {
        this.isRecording = false
        clearInterval(this.timer)
      }
    },
    
    // 格式化时间
    formatTime(seconds) {
      const hours = Math.floor(seconds / 3600)
      const minutes = Math.floor((seconds % 3600) / 60)
      const secs = seconds % 60
      return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
    },
    
    // 返回上一页
    goBack() {
      this.$emit('back')
      // 或者使用路由返回
      // this.$router.back()
    }
  }
}
</script>

<style lang="scss" scoped>
.interview-feedback-form {
  background-color: #f5f7fa;
  min-height: 100vh;
  padding: 0 0 20px 0;
  
  .page-header {
    background-color: white;
    padding: 15px 20px;
    margin-bottom: 15px;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    .title {
      font-size: 18px;
      font-weight: 500;
      color: #303133;
      
      i {
        margin-right: 5px;
      }
    }
    
    .header-actions {
      display: flex;
      gap: 10px;
      
      .el-button {
        font-weight: 500;
        padding: 10px 15px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
      }
    }
  }
  
  .action-toolbar {
    background-color: white;
    padding: 10px 15px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
    
    .action-buttons {
      display: flex;
      gap: 10px;
    }
    
    .timer-control {
      display: flex;
      align-items: center;
      gap: 10px;
      
      .timer {
        font-family: monospace;
        font-size: 18px;
        background: #f0f9eb;
        padding: 5px 10px;
        border-radius: 4px;
        min-width: 80px;
        text-align: center;
      }
    }
  }
  
  .record-textarea {
    margin-bottom: 15px;
    
    ::v-deep .el-textarea__inner {
      font-family: 'Courier New', monospace;
      font-size: 14px;
      line-height: 1.6;
      background-color: white;
      border-radius: 4px;
      box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
    }
  }
  
  .section-title {
    font-size: 16px;
    font-weight: 500;
    color: #303133;
    margin-bottom: 15px;
    padding-left: 10px;
    border-left: 3px solid #409EFF;
  }
  
  .quick-scores-section, .summary-section, .recommendation-section {
    background-color: white;
    padding: 15px 20px;
    margin-bottom: 15px;
    border-radius: 4px;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  }
  
  .score-items {
    display: flex;
    flex-wrap: wrap;
    gap: 10px 30px;
    
    .score-item {
      flex-basis: calc(20% - 30px);
      min-width: 150px;
      
      .score-label {
        margin-bottom: 8px;
        font-size: 14px;
        color: #606266;
      }
    }
  }
  
  .recommendation-options {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    margin-top: 10px;
  }
  
  .form-actions {
    text-align: center;
    margin-top: 30px;
    
    .el-button {
      min-width: 150px;
    }
  }
}
</style>