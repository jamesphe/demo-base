<template>
  <div>
    <el-dialog 
      :title="dialogTitle" 
      :visible="visible" 
      @close="$emit('update:visible', false)"
      width="800px" 
      class="feedback-detail-dialog"
      :close-on-click-modal="false"
    >
      <div v-if="feedback" class="feedback-content">
        <!-- 面试官信息 -->
        <div class="feedback-interviewer">
          <div class="interviewer-header">
            <el-avatar :size="40" icon="el-icon-user" class="interviewer-avatar"></el-avatar>
            <div class="interviewer-info">
              <h3 class="interviewer-name">{{ feedback.interviewer_name || '未知面试官' }}</h3>
              <p class="interviewer-title">面试官反馈</p>
            </div>
          </div>
          <div class="feedback-stats">
            <div class="stat-item">
              <div class="stat-label">综合评分</div>
              <div class="stat-value">
                <el-rate
                  v-model="feedback.evaluation_score"
                  disabled
                  show-score
                  text-color="#ff9900"
                  score-template="{value}"
                />
              </div>
            </div>
            <div class="stat-item">
              <div class="stat-label">招聘建议</div>
              <div class="stat-value">
                <el-tag 
                  :type="getRecommendationTagType(feedback.hiring_recommendation)" 
                  effect="dark"
                  class="recommendation-tag"
                >
                  {{ getRecommendationText(feedback.hiring_recommendation) }}
                </el-tag>
              </div>
            </div>
          </div>
        </div>

        <!-- 技术评估 -->
        <el-card class="feedback-detail-card" v-if="feedback.technical_evaluation" shadow="hover">
          <div slot="header" class="card-header">
            <i class="el-icon-cpu card-header-icon"></i>
            <span class="card-header-title">技术能力评估</span>
          </div>
          <div class="rating-grid">
            <div class="rating-item" v-for="(item, key) in technicalEvaluationItems" :key="key">
              <div class="rating-label">{{item.label}}</div>
              <el-rate 
                :value="getEvalValue(feedback.technical_evaluation, item.key1, item.key2)" 
                disabled 
                class="rating-stars"
              />
            </div>
          </div>
          <el-divider></el-divider>
          <div class="comments-section">
            <h4 class="comments-title">技术评价</h4>
            <div v-if="feedback.technical_evaluation.comments" class="comments-content">
              <div v-for="(comment, key) in formatTechnicalComments(feedback.technical_evaluation.comments)" :key="key" class="comment-item">
                <div class="comment-label">{{ comment.label }}</div>
                <div class="comment-text">{{ comment.text }}</div>
              </div>
            </div>
            <div v-else class="no-comments">暂无评价</div>
          </div>
        </el-card>

        <!-- 综合评估 -->
        <el-card class="feedback-detail-card" v-if="feedback.comprehensive_evaluation" shadow="hover">
          <div slot="header" class="card-header">
            <i class="el-icon-user card-header-icon"></i>
            <span class="card-header-title">综合能力评估</span>
          </div>
          <div class="rating-grid">
            <div class="rating-item" v-for="(item, key) in comprehensiveEvaluationItems" :key="key">
              <div class="rating-label">{{item.label}}</div>
              <el-rate 
                :value="getEvalValue(feedback.comprehensive_evaluation, item.key1, item.key2)" 
                disabled 
                class="rating-stars"
              />
            </div>
          </div>
          <el-divider></el-divider>
          <div class="comments-section">
            <h4 class="comments-title">综合评价</h4>
            <div v-if="feedback.comprehensive_evaluation.comments" class="comments-content">
              <div v-for="(comment, key) in formatComprehensiveComments(feedback.comprehensive_evaluation.comments)" :key="key" class="comment-item">
                <div class="comment-label">{{ comment.label }}</div>
                <div class="comment-text">{{ comment.text }}</div>
              </div>
            </div>
            <div v-else class="no-comments">暂无评价</div>
          </div>
        </el-card>

        <!-- 总体评价 -->
        <el-card class="feedback-detail-card" shadow="hover">
          <div slot="header" class="card-header">
            <i class="el-icon-document card-header-icon"></i>
            <span class="card-header-title">总体评价</span>
          </div>
          <div class="overall-feedback">
            <div class="overall-item">
              <div class="overall-label">
                <i class="el-icon-star-on"></i>
                <span>候选人优势</span>
              </div>
              <div class="overall-content">
                {{ feedback.strengths || '暂无记录' }}
              </div>
            </div>
            <div class="overall-item">
              <div class="overall-label">
                <i class="el-icon-warning-outline"></i>
                <span>候选人劣势</span>
              </div>
              <div class="overall-content">
                {{ feedback.weaknesses || '暂无记录' }}
              </div>
            </div>
            <div class="overall-item">
              <div class="overall-label">
                <i class="el-icon-chat-line-square"></i>
                <span>总体反馈</span>
              </div>
              <div class="overall-content">
                {{ feedback.feedback || '暂无记录' }}
              </div>
            </div>
          </div>
        </el-card>
      </div>
    </el-dialog>

    <!-- Markdown预览对话框 -->
    <el-dialog
      title="面试准备材料预览"
      :visible="markdownPreviewVisible"
      @close="markdownPreviewVisible = false"
      width="800px"
      class="markdown-preview-dialog"
    >
      <div class="markdown-content" v-html="markdownHtml"></div>
    </el-dialog>
  </div>
</template>

<script>
export default {
  name: 'FeedbackDetailDialog',
  components: {
    DescriptionList: () => import('@/components/DescriptionList'),
    DescriptionItem: () => import('@/components/DescriptionList/Item')
  },
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    feedback: {
      type: Object,
      default: null
    },
    title: {
      type: String,
      default: '面试官反馈详情'
    }
  },
  computed: {
    dialogTitle() {
      return this.title || '面试官反馈详情'
    },
    technicalEvaluationItems() {
      return [
        { label: '编码能力', key1: 'coding_ability', key2: 'codingAbility' },
        { label: '问题解决', key1: 'problem_solving', key2: 'problemSolving' },
        { label: '系统设计', key1: 'system_design', key2: 'systemDesign' },
        { label: '算法理解', key1: 'algorithm', key2: null },
        { label: '技术深度', key1: 'knowledge_depth', key2: 'knowledgeDepth' },
        { label: '技术广度', key1: 'knowledge_breadth', key2: 'knowledgeBreadth' }
      ]
    },
    comprehensiveEvaluationItems() {
      return [
        { label: '沟通能力', key1: 'communication', key2: null },
        { label: '团队协作', key1: 'teamwork', key2: null },
        { label: '学习能力', key1: 'learning_ability', key2: 'learningAbility' },
        { label: '抗压能力', key1: 'pressure_handling', key2: 'pressureHandling' },
        { label: '文化契合', key1: 'cultural_fit', key2: 'culturalFit' }
      ]
    }
  },
  data() {
    return {
      markdownPreviewVisible: false,
      markdownHtml: ''
    }
  },
  methods: {
    previewMarkdown(markdown) {
      if (!markdown) return
      
      // 这里简单处理，实际项目中应该使用markdown-it或marked等库解析markdown
      // 这里为简单实现，仅做一些基本转换
      let html = markdown
        .replace(/\n/g, '<br>')
        .replace(/^# (.*)/gm, '<h1>$1</h1>')
        .replace(/^## (.*)/gm, '<h2>$1</h2>')
        .replace(/^### (.*)/gm, '<h3>$1</h3>')
        .replace(/^\- (.*)/gm, '<ul><li>$1</li></ul>')
        .replace(/^\d\. (.*)/gm, '<ol><li>$1</li></ol>')
      
      this.markdownHtml = html
      this.markdownPreviewVisible = true
    },
    getRecommendationText(recommendation) {
      // 支持feedback页面的推荐格式
      const feedbackMap = {
        strong_recommend: '强烈推荐',
        recommend: '推荐',
        neutral: '中立',
        not_recommend: '不推荐',
        strong_not_recommend: '强烈不推荐'
      }
      
      // 支持evaluation页面的推荐格式
      const evaluationMap = {
        highly_recommended: '强烈推荐',
        recommended: '推荐',
        recommend_with_reservations: '有条件推荐',
        not_recommended: '不推荐',
        strongly_not_recommended: '强烈不推荐'
      }
      
      // 尝试从两种映射中获取文本
      return feedbackMap[recommendation] || evaluationMap[recommendation] || '未评价'
    },
    getRecommendationTagType(recommendation) {
      // 支持feedback页面的推荐类型
      const feedbackMap = {
        strong_recommend: 'success',
        recommend: 'success',
        neutral: 'info',
        not_recommend: 'warning',
        strong_not_recommend: 'danger'
      }
      
      // 支持evaluation页面的推荐类型
      const evaluationMap = {
        highly_recommended: 'success',
        recommended: 'success',
        recommend_with_reservations: 'warning',
        not_recommended: 'danger',
        strongly_not_recommended: 'danger'
      }
      
      // 尝试从两种映射中获取标签类型
      return feedbackMap[recommendation] || evaluationMap[recommendation] || 'info'
    },
    getTechnicalEvaluationLabel(key) {
      const labelMap = {
        coding_ability: '编码能力',
        problem_solving: '问题解决',
        system_design: '系统设计',
        algorithm: '算法理解',
        knowledge_depth: '技术深度',
        knowledge_breadth: '技术广度',
        codingAbility: '编码能力',
        problemSolving: '问题解决',
        systemDesign: '系统设计',
        knowledgeDepth: '技术深度',
        knowledgeBreadth: '技术广度'
      }
      return labelMap[key] || key
    },
    getComprehensiveEvaluationLabel(key) {
      const labelMap = {
        communication: '沟通能力',
        teamwork: '团队协作',
        learning_ability: '学习能力',
        pressure_handling: '抗压能力',
        cultural_fit: '文化契合',
        learningAbility: '学习能力',
        pressureHandling: '抗压能力',
        culturalFit: '文化契合'
      }
      return labelMap[key] || key
    },
    getEvalValue(obj, key1, key2) {
      if (!obj) return 0;
      if (obj[key1] != null) return obj[key1];
      if (key2 && obj[key2] != null) return obj[key2];
      return 0;
    },
    formatTechnicalComments(comments) {
      if (!comments) return [];
      
      // 处理可能的格式：对象或数组
      if (Array.isArray(comments)) {
        return comments.map((comment, index) => ({
          label: `评价 ${index + 1}`,
          text: comment
        }));
      }
      
      // 处理对象格式
      return Object.keys(comments).map(key => {
        // 排除非字符串或空值
        if (typeof comments[key] !== 'string' || !comments[key]) return null;
        
        return {
          label: this.getTechnicalEvaluationLabel(key),
          text: comments[key]
        };
      }).filter(item => item !== null);
    },
    formatComprehensiveComments(comments) {
      if (!comments) return [];
      
      // 处理可能的格式：对象或数组
      if (Array.isArray(comments)) {
        return comments.map((comment, index) => ({
          label: `评价 ${index + 1}`,
          text: comment
        }));
      }
      
      // 处理对象格式
      return Object.keys(comments).map(key => {
        // 排除非字符串或空值
        if (typeof comments[key] !== 'string' || !comments[key]) return null;
        
        return {
          label: this.getComprehensiveEvaluationLabel(key),
          text: comments[key]
        };
      }).filter(item => item !== null);
    }
  }
}
</script>

<style lang="scss" scoped>
.feedback-detail-dialog {
  ::v-deep .el-dialog {
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  }
  
  ::v-deep .el-dialog__header {
    background: linear-gradient(135deg, #4b6cb7 0%, #182848 100%);
    padding: 20px 24px;
    position: relative;
    
    .el-dialog__title {
      color: white;
      font-weight: 600;
      font-size: 18px;
    }
    
    .el-dialog__headerbtn {
      .el-dialog__close {
        color: rgba(255, 255, 255, 0.8);
        
        &:hover {
          color: white;
        }
      }
    }
  }
  
  ::v-deep .el-dialog__body {
    padding: 24px;
    max-height: 75vh;
    overflow-y: auto;
  }
}

.feedback-content {
  padding: 0 8px;
}

.feedback-interviewer {
  margin-bottom: 30px;
  padding: 0;
  
  .interviewer-header {
    display: flex;
    align-items: center;
    margin-bottom: 20px;
    
    .interviewer-avatar {
      background: linear-gradient(135deg, #4b6cb7 0%, #182848 100%);
      margin-right: 16px;
    }
    
    .interviewer-info {
      .interviewer-name {
        margin: 0 0 4px 0;
        font-size: 20px;
        font-weight: 600;
        color: #303133;
      }
      
      .interviewer-title {
        margin: 0;
        font-size: 14px;
        color: #909399;
      }
    }
  }
  
  .feedback-stats {
    display: flex;
    flex-wrap: wrap;
    margin: -8px;
    
    .stat-item {
      background-color: #f9fbfd;
      padding: 16px;
      border-radius: 10px;
      margin: 8px;
      flex: 1;
      min-width: 200px;
      box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.03);
      border: 1px solid #ebeef5;
      
      .stat-label {
        color: #606266;
        font-size: 14px;
        margin-bottom: 8px;
      }
      
      .stat-value {
        font-weight: 500;
        display: flex;
        align-items: center;
      }
    }
    
    .recommendation-tag {
      font-size: 14px;
      padding: 6px 12px;
      border-radius: 4px;
    }
  }
}

.feedback-detail-card {
  margin-bottom: 30px;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05) !important;
  border: none;
  
  ::v-deep .el-card__header {
    padding: 16px 20px;
    border-bottom: 1px solid #ebeef5;
  }
  
  ::v-deep .el-card__body {
    padding: 24px;
  }
  
  .card-header {
    display: flex;
    align-items: center;
    
    .card-header-icon {
      font-size: 18px;
      color: #409EFF;
      margin-right: 8px;
    }
    
    .card-header-title {
      font-size: 16px;
      font-weight: 600;
      color: #303133;
    }
  }
}

.rating-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 20px;
  
  .rating-item {
    .rating-label {
      margin-bottom: 8px;
      font-size: 14px;
      color: #606266;
    }
    
    .rating-stars {
      ::v-deep .el-rate__icon {
        font-size: 18px;
        margin-right: 4px;
      }
    }
  }
}

.comments-section {
  margin-top: 20px;
  
  .comments-title {
    font-size: 16px;
    font-weight: 600;
    color: #303133;
    margin: 0 0 16px 0;
  }
  
  .comments-content {
    .comment-item {
      margin-bottom: 16px;
      padding-bottom: 16px;
      border-bottom: 1px dashed #ebeef5;
      
      &:last-child {
        margin-bottom: 0;
        padding-bottom: 0;
        border-bottom: none;
      }
      
      .comment-label {
        font-weight: 600;
        color: #606266;
        margin-bottom: 8px;
      }
      
      .comment-text {
        color: #303133;
        line-height: 1.6;
      }
    }
  }
  
  .no-comments {
    color: #909399;
    font-style: italic;
  }
}

.overall-feedback {
  .overall-item {
    margin-bottom: 24px;
    
    &:last-child {
      margin-bottom: 0;
    }
    
    .overall-label {
      display: flex;
      align-items: center;
      margin-bottom: 12px;
      
      i {
        font-size: 16px;
        margin-right: 8px;
        color: #409EFF;
      }
      
      span {
        font-size: 15px;
        font-weight: 600;
        color: #303133;
      }
    }
    
    .overall-content {
      background-color: #f9fbfd;
      border-radius: 8px;
      padding: 16px;
      color: #303133;
      line-height: 1.6;
      border: 1px solid #ebeef5;
    }
  }
}

.markdown-preview-dialog {
  ::v-deep .el-dialog {
    border-radius: 8px;
    overflow: hidden;
  }
  
  ::v-deep .el-dialog__header {
    background-color: #f5f7fa;
    padding: 16px 20px;
  }
  
  ::v-deep .el-dialog__body {
    padding: 24px;
    max-height: 70vh;
    overflow-y: auto;
  }
  
  .markdown-content {
    line-height: 1.6;
    
    h1 {
      font-size: 24px;
      margin-top: 24px;
      margin-bottom: 16px;
      font-weight: 600;
      line-height: 1.25;
      color: #303133;
    }
    
    h2 {
      font-size: 20px;
      margin-top: 24px;
      margin-bottom: 16px;
      font-weight: 600;
      line-height: 1.25;
      color: #303133;
    }
    
    h3 {
      font-size: 16px;
      margin-top: 24px;
      margin-bottom: 16px;
      font-weight: 600;
      line-height: 1.25;
      color: #303133;
    }
    
    ul, ol {
      padding-left: 2em;
      margin-bottom: 16px;
      display: block;
      
      li {
        margin-bottom: 8px;
        background: none;
        padding: 0;
        box-shadow: none;
        min-width: auto;
      }
    }
  }
}
</style> 