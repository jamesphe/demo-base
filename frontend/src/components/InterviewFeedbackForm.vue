<template>
  <div class="interview-feedback-form">
    <el-form
      ref="feedbackForm"
      :model="feedbackForm"
      :rules="feedbackRules"
      label-width="120px"
    >
      <!-- 技术能力评估 -->
      <el-card class="feedback-card">
        <div slot="header">
          <span>技术能力评估</span>
        </div>
        <el-form-item label="编码能力" prop="technical_evaluation.coding_ability">
          <el-rate
            v-model="feedbackForm.technical_evaluation.coding_ability"
            :max="5"
            show-score
            text-color="#ff9900"
          />
        </el-form-item>
        <el-form-item label="问题解决" prop="technical_evaluation.problem_solving">
          <el-rate
            v-model="feedbackForm.technical_evaluation.problem_solving"
            :max="5"
            show-score
            text-color="#ff9900"
          />
        </el-form-item>
        <el-form-item label="系统设计" prop="technical_evaluation.system_design">
          <el-rate
            v-model="feedbackForm.technical_evaluation.system_design"
            :max="5"
            show-score
            text-color="#ff9900"
          />
        </el-form-item>
        <el-form-item label="算法理解" prop="technical_evaluation.algorithm_understanding">
          <el-rate
            v-model="feedbackForm.technical_evaluation.algorithm_understanding"
            :max="5"
            show-score
            text-color="#ff9900"
          />
        </el-form-item>
        <el-form-item label="技术深度" prop="technical_evaluation.knowledge_depth">
          <el-rate
            v-model="feedbackForm.technical_evaluation.knowledge_depth"
            :max="5"
            show-score
            text-color="#ff9900"
          />
        </el-form-item>
        <el-form-item label="技术广度" prop="technical_evaluation.knowledge_breadth">
          <el-rate
            v-model="feedbackForm.technical_evaluation.knowledge_breadth"
            :max="5"
            show-score
            text-color="#ff9900"
          />
        </el-form-item>
        <el-form-item label="技术评价" prop="technical_evaluation.comments">
          <el-input
            type="textarea"
            :rows="3"
            placeholder="请详细评价候选人的技术能力"
            v-model="feedbackForm.technical_evaluation.comments"
          />
        </el-form-item>
      </el-card>

      <!-- 综合能力评估 -->
      <el-card class="feedback-card">
        <div slot="header">
          <span>综合能力评估</span>
        </div>
        <el-form-item label="沟通能力" prop="comprehensive_evaluation.communication">
          <el-rate
            v-model="feedbackForm.comprehensive_evaluation.communication"
            :max="5"
            show-score
            text-color="#ff9900"
          />
        </el-form-item>
        <el-form-item label="团队协作" prop="comprehensive_evaluation.teamwork">
          <el-rate
            v-model="feedbackForm.comprehensive_evaluation.teamwork"
            :max="5"
            show-score
            text-color="#ff9900"
          />
        </el-form-item>
        <el-form-item label="学习能力" prop="comprehensive_evaluation.learning_ability">
          <el-rate
            v-model="feedbackForm.comprehensive_evaluation.learning_ability"
            :max="5"
            show-score
            text-color="#ff9900"
          />
        </el-form-item>
        <el-form-item label="抗压能力" prop="comprehensive_evaluation.pressure_handling">
          <el-rate
            v-model="feedbackForm.comprehensive_evaluation.pressure_handling"
            :max="5"
            show-score
            text-color="#ff9900"
          />
        </el-form-item>
        <el-form-item label="文化契合" prop="comprehensive_evaluation.culture_fit">
          <el-rate
            v-model="feedbackForm.comprehensive_evaluation.culture_fit"
            :max="5"
            show-score
            text-color="#ff9900"
          />
        </el-form-item>
        <el-form-item label="综合评价" prop="comprehensive_evaluation.comments">
          <el-input
            type="textarea"
            :rows="3"
            placeholder="请详细评价候选人的综合素质"
            v-model="feedbackForm.comprehensive_evaluation.comments"
          />
        </el-form-item>
      </el-card>

      <!-- 总体评价 -->
      <el-card class="feedback-card">
        <div slot="header">
          <span>总体评价</span>
        </div>
        <el-form-item label="综合得分" prop="evaluation_score">
          <el-rate
            v-model="feedbackForm.evaluation_score"
            :max="5"
            show-score
            text-color="#ff9900"
          />
        </el-form-item>
        <el-form-item label="候选人优势" prop="strengths">
          <el-input
            type="textarea"
            :rows="3"
            placeholder="请列出候选人的主要优势，多个优势用逗号分隔"
            v-model="feedbackForm.strengths"
          />
        </el-form-item>
        <el-form-item label="候选人劣势" prop="weaknesses">
          <el-input
            type="textarea"
            :rows="3"
            placeholder="请列出候选人的主要劣势，多个劣势用逗号分隔"
            v-model="feedbackForm.weaknesses"
          />
        </el-form-item>
        <el-form-item label="招聘建议" prop="hiring_recommendation">
          <el-select v-model="feedbackForm.hiring_recommendation" placeholder="请选择招聘建议">
            <el-option label="强烈推荐" value="strong_recommend" />
            <el-option label="推荐" value="recommend" />
            <el-option label="中立" value="neutral" />
            <el-option label="不推荐" value="not_recommend" />
            <el-option label="强烈不推荐" value="strong_not_recommend" />
          </el-select>
        </el-form-item>
        <el-form-item label="总体反馈" prop="feedback">
          <el-input
            type="textarea"
            :rows="4"
            placeholder="请提供详细的面试总结和招聘建议"
            v-model="feedbackForm.feedback"
          />
        </el-form-item>
      </el-card>

      <!-- 面试准备材料 -->
      <el-card class="feedback-card">
        <div slot="header">
          <span>面试准备材料</span>
        </div>
        <el-form-item label="准备笔记" prop="preparation_notes">
          <el-input
            type="textarea"
            :rows="6"
            placeholder="面试准备材料，支持Markdown格式"
            v-model="feedbackForm.preparation_notes"
          />
        </el-form-item>
        <div class="form-actions">
          <el-button type="primary" size="small" @click="generatePreparationNotes">
            AI生成面试准备材料
          </el-button>
        </div>
      </el-card>

      <!-- 提交按钮 -->
      <div class="form-actions">
        <el-button @click="handleCancel">取 消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">提 交</el-button>
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
        technical_evaluation: {
          coding_ability: 0,
          problem_solving: 0,
          system_design: 0,
          algorithm_understanding: 0,
          knowledge_depth: 0,
          knowledge_breadth: 0,
          comments: ''
        },
        comprehensive_evaluation: {
          communication: 0,
          teamwork: 0,
          learning_ability: 0,
          pressure_handling: 0,
          culture_fit: 0,
          comments: ''
        },
        evaluation_score: 0,
        strengths: '',
        weaknesses: '',
        hiring_recommendation: '',
        feedback: '',
        preparation_notes: ''
      },
      feedbackRules: {
        evaluation_score: [
          { required: true, message: '请给出综合得分', trigger: 'change' }
        ],
        hiring_recommendation: [
          { required: true, message: '请选择招聘建议', trigger: 'change' }
        ],
        feedback: [
          { required: true, message: '请填写总体反馈', trigger: 'blur' }
        ]
      }
    }
  },
  created() {
    this.initFormData()
  },
  methods: {
    initFormData() {
      // 设置面试和面试官ID
      this.feedbackForm.interview_id = this.interview.id
      this.feedbackForm.interviewer_id = this.interviewer?.id || ''

      // 如果有现有的反馈数据，填充表单
      if (this.existingFeedback) {
        // 复制评估数据
        this.feedbackForm.evaluation_score = this.existingFeedback.evaluation_score || 0
        this.feedbackForm.strengths = this.existingFeedback.strengths || ''
        this.feedbackForm.weaknesses = this.existingFeedback.weaknesses || ''
        this.feedbackForm.hiring_recommendation = this.existingFeedback.hiring_recommendation || ''
        this.feedbackForm.feedback = this.existingFeedback.feedback || ''

        // 复制技术评估
        if (this.existingFeedback.technical_evaluation) {
          Object.keys(this.feedbackForm.technical_evaluation).forEach(key => {
            if (this.existingFeedback.technical_evaluation[key] !== undefined) {
              this.feedbackForm.technical_evaluation[key] = this.existingFeedback.technical_evaluation[key]
            }
          })
        }

        // 复制综合评估
        if (this.existingFeedback.comprehensive_evaluation) {
          Object.keys(this.feedbackForm.comprehensive_evaluation).forEach(key => {
            if (this.existingFeedback.comprehensive_evaluation[key] !== undefined) {
              this.feedbackForm.comprehensive_evaluation[key] = this.existingFeedback.comprehensive_evaluation[key]
            }
          })
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
    async generatePreparationNotes() {
      try {
        this.$confirm('确定要使用AI生成面试准备材料吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'info'
        }).then(async () => {
          this.$message({
            type: 'info',
            message: '正在生成准备材料...'
          });
          
          // 这里可以调用后端API生成面试准备材料
          // 简单模拟一下AI生成过程
          setTimeout(() => {
            const candidateName = this.interview.candidateName || '候选人';
            const position = this.interview.candidatePosition || '该职位';
            
            this.feedbackForm.preparation_notes = 
`# ${candidateName}面试准备材料

## 职位要求分析
- 分析${position}所需的关键技能和经验
- 准备针对性的技术问题
- 关注候选人简历中的技能匹配度

## 技术评估要点
1. 编码能力评估
   - 算法基础
   - 代码质量和规范
   - 问题解决思路

2. 系统设计能力
   - 架构设计原则
   - 性能和可扩展性考量
   - 微服务vs单体应用的权衡

3. 技术广度和深度
   - 对技术栈的熟悉程度
   - 对新技术的学习能力
   - 技术选型的判断力

## 行为面试问题
- 描述一个您克服的技术挑战
- 如何处理项目中的冲突
- 团队协作经历分享

## 候选人背景调研
- 之前公司的技术栈和项目规模
- 行业经验和领域知识
- 职业发展轨迹分析

## 准备的问题清单
1. 技术问题：...
2. 项目经验问题：...
3. 团队协作问题：...
4. 职业发展问题：...`;
            
            this.$message({
              type: 'success',
              message: '面试准备材料生成成功'
            });
          }, 1500);
        });
      } catch (error) {
        console.error('生成准备材料失败:', error);
        this.$message.error('生成准备材料失败');
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.interview-feedback-form {
  .feedback-card {
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
}
</style> 