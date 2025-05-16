<template>
  <div class="app-container">
    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span>面试官反馈</span>
      </div>

      <div v-loading="loading">
        <!-- 候选人基本信息 -->
        <el-card v-if="interview && interview.candidateName" class="candidate-profile-card">
          <div class="candidate-profile-header">
            <div class="candidate-avatar">
              <el-avatar :size="64" icon="el-icon-user-solid"></el-avatar>
            </div>
            <div class="candidate-main-info">
              <h2 class="candidate-name">{{ interview.candidateName }}</h2>
              <div class="candidate-position">
                <i class="el-icon-suitcase"></i> {{ interview.candidatePosition }}
              </div>
              <div class="interview-type">
                <el-tag :type="getInterviewTypeTag(interview.type)" effect="dark" size="medium">
                  {{ getInterviewTypeText(interview.type) }}
                </el-tag>
              </div>
            </div>
          </div>
          
          <el-divider content-position="center">面试详情</el-divider>
          
          <div class="candidate-details">
            <div class="detail-item">
              <div class="detail-icon">
                <i class="el-icon-time"></i>
              </div>
              <div class="detail-content">
                <div class="detail-label">面试时间</div>
                <div class="detail-value">{{ formatDateTime(interview.time) }}</div>
              </div>
            </div>
            
            <div class="detail-item">
              <div class="detail-icon">
                <i class="el-icon-location"></i>
              </div>
              <div class="detail-content">
                <div class="detail-label">面试地点</div>
                <div class="detail-value">{{ interview.location }}</div>
              </div>
            </div>
            
            <div class="detail-item interviewers-container">
              <div class="detail-icon">
                <i class="el-icon-user"></i>
              </div>
              <div class="detail-content">
                <div class="detail-label">面试官</div>
                <div class="interviewers-list">
                  <el-tag
                    v-for="interviewer in interview.interviewers"
                    :key="interviewer.id"
                    size="small"
                    class="interviewer-tag"
                    :type="interviewer.id === (currentUser && currentUser.id ? currentUser.id : '') ? 'success' : ''"
                    effect="plain"
                  >
                    {{ interviewer.name || interviewer.username }}
                  </el-tag>
                </div>
              </div>
            </div>
          </div>
          
          <div class="candidate-actions">
            <el-button type="primary" size="small" icon="el-icon-phone" @click="showContactInfo" plain>
              查看候选人联系方式
            </el-button>
            <el-button type="info" size="small" icon="el-icon-document" plain>
              查看简历
            </el-button>
          </div>
        </el-card>
        
        <!-- 候选人联系方式按钮 - 已移动到个人资料卡中 -->

        <!-- 面试官反馈表单 -->
        <interview-feedback-form
          v-if="!showSummary && interview && interview.id"
          :interview="interview"
          :interviewer="currentUser"
          :existing-feedback="existingFeedback"
          :submitting="submitting"
          @submit="handleSubmitFeedback"
          @cancel="handleCancel"
        />

        <!-- 反馈汇总 -->
        <div v-if="showSummary">
          <div class="summary-header">
            <h3>面试反馈汇总</h3>
            <div>
              <el-button type="primary" size="small" icon="el-icon-refresh" @click="refreshSummary" plain>
                刷新数据
              </el-button>
              <el-button type="info" size="small" icon="el-icon-back" @click="showSummary = false" plain>
                返回我的评价
              </el-button>
            </div>
          </div>

          <!-- 评分概览 -->
          <el-card class="summary-card">
            <div slot="header">
              <span>评分概览</span>
            </div>
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

            <!-- 推荐结果 -->
            <div class="recommendation-stats">
              <h4>招聘建议统计</h4>
              <div class="recommendation-summary">
                <div class="recommendation-total">
                  <span class="total-label">面试官总数: {{ feedbackSummary.interviewer_count || 0 }}人</span>
                  <span class="total-label">已完成反馈: {{ feedbackSummary.completed_count || 0 }}人</span>
                  <el-progress 
                    :percentage="feedbackSummary.interviewer_count > 0 ? Math.round(feedbackSummary.completed_count / feedbackSummary.interviewer_count * 100) : 0"
                    :format="percent => `完成率: ${percent}%`"
                    :stroke-width="12"
                  ></el-progress>
                </div>
                
                <div class="recommendation-legend">
                  <div class="legend-item" v-for="(color, type) in {
                    'strong_recommend': '#67c23a',
                    'recommend': '#85ce61',
                    'neutral': '#909399',
                    'not_recommend': '#e6a23c',
                    'strong_not_recommend': '#f56c6c'
                  }" :key="type">
                    <div class="legend-color" :style="{ backgroundColor: color }"></div>
                    <div class="legend-text">{{ getRecommendationText(type) }}</div>
                  </div>
                </div>
              </div>
              
              <div class="recommendation-description">
                <i class="el-icon-info"></i>
                <span>下方显示各类招聘建议所占比例，百分比基于已完成反馈的面试官人数</span>
              </div>
              
              <div v-if="Object.keys(feedbackSummary.recommendation_summary || {}).length > 0" class="recommendation-progress-list">
                <div v-for="(count, type) in feedbackSummary.recommendation_summary" :key="type" class="recommendation-progress-item">
                  <div class="recommendation-label">
                    <el-tag :type="getRecommendationTagType(type)" effect="plain" size="small">
                      {{ getRecommendationText(type) }}
                    </el-tag>
                  </div>
                  <div class="recommendation-progress">
                    <el-progress 
                      :percentage="feedbackSummary.completed_count > 0 ? Math.round(count / feedbackSummary.completed_count * 100) : 0"
                      :color="getRecommendationColor(type)"
                      :stroke-width="16"
                      :format="percent => `${percent}% (${count}人)`"
                    >
                    </el-progress>
                  </div>
                </div>
              </div>
              <div v-else>
                <el-empty description="暂无推荐数据" :image-size="80"></el-empty>
              </div>
            </div>
          </el-card>

          <!-- 关键优势/不足 -->
          <div class="strengths-weaknesses">
            <el-card class="strength-card">
              <div slot="header">
                <span>关键优势</span>
              </div>
              <ul class="strength-list">
                <li v-for="(strength, index) in feedbackSummary.key_strengths" :key="index">
                  <i class="el-icon-check" style="color: #67c23a; margin-right: 5px;"></i> {{ strength }}
                </li>
                <li v-if="feedbackSummary.key_strengths.length === 0">暂无数据</li>
              </ul>
            </el-card>
            <el-card class="weakness-card">
              <div slot="header">
                <span>关键不足</span>
              </div>
              <ul class="weakness-list">
                <li v-for="(weakness, index) in feedbackSummary.key_weaknesses" :key="index">
                  <i class="el-icon-close" style="color: #f56c6c; margin-right: 5px;"></i> {{ weakness }}
                </li>
                <li v-if="feedbackSummary.key_weaknesses.length === 0">暂无数据</li>
              </ul>
            </el-card>
          </div>

          <!-- 技术/综合平均分 -->
          <div>
            <h4><i class="el-icon-cpu" style="margin-right: 8px;"></i>技术能力平均分</h4>
            <ul>
              <li v-for="(score, key) in feedbackSummary.technical_averages" :key="key">
                {{ getTechnicalEvaluationLabel(key) }}: <span style="color: #409eff; font-weight: bold;">{{ score }}</span>
              </li>
            </ul>
            <h4><i class="el-icon-user" style="margin-right: 8px;"></i>综合能力平均分</h4>
            <ul>
              <li v-for="(score, key) in feedbackSummary.comprehensive_averages" :key="key">
                {{ getComprehensiveEvaluationLabel(key) }}: <span style="color: #409eff; font-weight: bold;">{{ score }}</span>
              </li>
            </ul>
          </div>

          <!-- 详细反馈 -->
          <el-card class="detailed-feedback">
            <div slot="header">
              <span>详细反馈</span>
            </div>
            <el-table :data="feedbackSummary.feedbacks" style="width: 100%" border>
              <el-table-column label="面试官" prop="interviewer_name" width="150">
                <template slot-scope="scope">
                  <el-avatar :size="24" icon="el-icon-user" style="margin-right: 8px; vertical-align: middle;"></el-avatar>
                  {{ scope.row.interviewer_name || '未知面试官' }}
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
                  <el-tag :type="getRecommendationTagType(scope.row.hiring_recommendation)" effect="dark">
                    {{ getRecommendationText(scope.row.hiring_recommendation) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="反馈状态" width="100">
                <template slot-scope="scope">
                  <el-tag :type="scope.row.status === 'completed' ? 'success' : 'warning'" effect="plain">
                    {{ scope.row.status === 'completed' ? '已完成' : '待完成' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="120" align="center">
                <template slot-scope="scope">
                  <el-button 
                    type="primary" 
                    size="mini" 
                    icon="el-icon-view"
                    @click="handleViewFeedback(scope.row)"
                    :disabled="scope.row.status !== 'completed'"
                    plain
                  >
                    查看详情
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </div>
      </div>
    </el-card>

    <!-- 详细反馈对话框 -->
    <el-dialog title="反馈详情" :visible.sync="dialogVisible" width="750px">
      <div v-if="selectedFeedback">
        <!-- 面试官信息 -->
        <div class="feedback-interviewer">
          <h4>
            <el-avatar :size="28" icon="el-icon-user" style="margin-right: 10px; vertical-align: middle;"></el-avatar>
            {{ selectedFeedback.interviewer_name || '未知面试官' }} 的反馈
          </h4>
          <div class="feedback-stats">
            <span>
              综合评分: 
              <el-rate
                v-model="selectedFeedback.evaluation_score"
                disabled
                show-score
                text-color="#ff9900"
              />
            </span>
            <span>
              招聘建议: 
              <el-tag :type="getRecommendationTagType(selectedFeedback.hiring_recommendation)" effect="dark">
                {{ getRecommendationText(selectedFeedback.hiring_recommendation) }}
              </el-tag>
            </span>
          </div>
        </div>

        <!-- 技术评估 -->
        <el-card class="feedback-detail-card" v-if="selectedFeedback.technical_evaluation">
          <div slot="header">
            <span><i class="el-icon-cpu" style="margin-right: 5px;"></i>技术能力评估</span>
          </div>
          <description-list :column="3" :border="true">
            <description-item label="编码能力">
              <el-rate :value="getEvalValue(selectedFeedback.technical_evaluation, 'coding_ability', 'codingAbility')" disabled />
            </description-item>
            <description-item label="问题解决">
              <el-rate :value="getEvalValue(selectedFeedback.technical_evaluation, 'problem_solving', 'problemSolving')" disabled />
            </description-item>
            <description-item label="系统设计">
              <el-rate :value="getEvalValue(selectedFeedback.technical_evaluation, 'system_design', 'systemDesign')" disabled />
            </description-item>
            <description-item label="算法理解">
              <el-rate :value="getEvalValue(selectedFeedback.technical_evaluation, 'algorithm')" disabled />
            </description-item>
            <description-item label="技术深度">
              <el-rate :value="getEvalValue(selectedFeedback.technical_evaluation, 'knowledge_depth', 'knowledgeDepth')" disabled />
            </description-item>
            <description-item label="技术广度">
              <el-rate :value="getEvalValue(selectedFeedback.technical_evaluation, 'knowledge_breadth', 'knowledgeBreadth')" disabled />
            </description-item>
            <description-item :span="3" label="技术评价">
              <div v-if="selectedFeedback.technical_evaluation.comments">
                <div v-for="(comment, key) in selectedFeedback.technical_evaluation.comments" :key="key">
                  <strong>{{ getTechnicalEvaluationLabel(key) }}:</strong> {{ comment }}
                </div>
              </div>
              <div v-else>暂无评价</div>
            </description-item>
          </description-list>
        </el-card>

        <!-- 综合评估 -->
        <el-card class="feedback-detail-card" v-if="selectedFeedback.comprehensive_evaluation">
          <div slot="header">
            <span><i class="el-icon-user" style="margin-right: 5px;"></i>综合能力评估</span>
          </div>
          <description-list :column="3" :border="true">
            <description-item label="沟通能力">
              <el-rate :value="getEvalValue(selectedFeedback.comprehensive_evaluation, 'communication')" disabled />
            </description-item>
            <description-item label="团队协作">
              <el-rate :value="getEvalValue(selectedFeedback.comprehensive_evaluation, 'teamwork')" disabled />
            </description-item>
            <description-item label="学习能力">
              <el-rate :value="getEvalValue(selectedFeedback.comprehensive_evaluation, 'learning_ability', 'learningAbility')" disabled />
            </description-item>
            <description-item label="抗压能力">
              <el-rate :value="getEvalValue(selectedFeedback.comprehensive_evaluation, 'pressure_handling', 'pressureHandling')" disabled />
            </description-item>
            <description-item label="文化契合">
              <el-rate :value="getEvalValue(selectedFeedback.comprehensive_evaluation, 'cultural_fit', 'culturalFit')" disabled />
            </description-item>
            <description-item :span="3" label="综合评价">
              <div v-if="selectedFeedback.comprehensive_evaluation.comments">
                <div v-for="(comment, key) in selectedFeedback.comprehensive_evaluation.comments" :key="key">
                  <strong>{{ getComprehensiveEvaluationLabel(key) }}:</strong> {{ comment }}
                </div>
              </div>
              <div v-else>暂无评价</div>
            </description-item>
          </description-list>
        </el-card>

        <!-- 总体评价 -->
        <el-card class="feedback-detail-card">
          <div slot="header">
            <span><i class="el-icon-document" style="margin-right: 5px;"></i>总体评价</span>
          </div>
          <description-list :column="1" :border="true">
            <description-item label="候选人优势">
              {{ selectedFeedback.strengths || '暂无记录' }}
            </description-item>
            <description-item label="候选人劣势">
              {{ selectedFeedback.weaknesses || '暂无记录' }}
            </description-item>
            <description-item label="总体反馈">
              {{ selectedFeedback.feedback || '暂无记录' }}
            </description-item>
          </description-list>
        </el-card>

        <!-- 面试准备材料 -->
        <el-card class="feedback-detail-card" v-if="selectedFeedback.preparation_notes">
          <div slot="header">
            <div class="card-header-with-actions">
              <span><i class="el-icon-notebook-1" style="margin-right: 5px;"></i>面试准备材料</span>
              <el-button 
                type="primary" 
                size="small" 
                icon="el-icon-view"
                @click="previewMarkdown(selectedFeedback.preparation_notes)"
              >
                预览Markdown
              </el-button>
            </div>
          </div>
          <pre class="preparation-notes">{{ selectedFeedback.preparation_notes }}</pre>
        </el-card>
      </div>
    </el-dialog>

    <!-- Markdown预览对话框 -->
    <el-dialog
      title="面试准备材料预览"
      :visible.sync="markdownPreviewVisible"
      width="800px"
      class="markdown-preview-dialog"
    >
      <div class="markdown-content" v-html="markdownHtml"></div>
    </el-dialog>

    <!-- 联系方式对话框 -->
    <el-dialog title="联系方式" :visible.sync="contactVisible" width="30%">
      <div v-loading="contactLoading">
        <description-list :column="1" :border="true">
          <description-item label="手机号码">{{ contactInfo.phone }}</description-item>
          <description-item label="电子邮箱">{{ contactInfo.email }}</description-item>
          <description-item label="微信号">{{ contactInfo.wechat }}</description-item>
        </description-list>
        
        <div class="contact-education" v-if="interview && interview.resume">
          <h4>教育背景</h4>
          <description-list :column="1" :border="true">
            <description-item label="最高学历">{{ interview.resume.highestEducation }}</description-item>
            <description-item label="专业">{{ interview.resume.major }}</description-item>
          </description-list>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import InterviewFeedbackForm from '@/components/InterviewFeedbackForm'

export default {
  name: 'InterviewFeedback',
  components: {
    InterviewFeedbackForm
  },
  data() {
    return {
      loading: false,
      submitting: false,
      interview: {
        id: '',
        candidateName: '',
        candidatePosition: '',
        type: '',
        time: '',
        location: '',
        interviewers: [],
        resume: null
      },
      existingFeedback: null,
      feedbackSummary: {
        interview_id: 0,
        average_score: 0,
        interviewer_count: 0,
        completed_count: 0,
        recommendation_summary: {},
        feedbacks: [],
        key_strengths: [],
        key_weaknesses: [],
        technical_averages: {},
        comprehensive_averages: {}
      },
      showSummary: false,
      dialogVisible: false,
      selectedFeedback: null,
      markdownPreviewVisible: false,
      markdownHtml: '',
      contactVisible: false,
      contactLoading: false,
      contactInfo: {}
    }
  },
  computed: {
    ...mapGetters(['name', 'avatar', 'roles', 'user_id', 'currentUser'])
  },
  created() {
    this.getInterviewInfo()
    this.getExistingFeedback()
  },
  methods: {
    async getInterviewInfo() {
      this.loading = true
      try {
        const interviewId = this.$route.params.id
        // 使用Vuex store获取面试详情
        const response = await this.$store.dispatch('interview/getInterviewDetail', interviewId)
        console.log('Store返回的面试详情数据:', response)
        
        // 根据API返回的数据结构映射到组件的数据模型
        this.interview = {
          id: response.id,
          candidateName: response.resume ? response.resume.name : response.resumeTitle,
          candidatePosition: response.job ? response.job.title : response.jobTitle,
          type: response.interviewType,
          time: response.scheduleTime,
          location: response.location,
          interviewers: response.interviewers || [],
          resume: response.resume || null
        }
        
        // 如果有resume信息，保存联系方式
        if (response.resume) {
          this.contactInfo = {
            phone: response.resume.phone,
            email: response.resume.email,
            wechat: response.resume.wechat || '未提供'
          }
        }
        
        this.getInterviewSummary()
      } catch (error) {
        console.error('获取面试信息失败:', error)
        this.$message.error('获取面试信息失败')
      } finally {
        this.loading = false
      }
    },
    async getExistingFeedback() {
      try {
        const interviewId = this.$route.params.id
        const userId = this.user_id || ''
        
        if (!userId) {
          console.log('未获取到用户ID，无法获取反馈')
          return
        }
        
        // 使用Vuex store获取面试官反馈
        const response = await this.$store.dispatch('interview/getInterviewerFeedback', {
          interviewId,
          interviewerId: userId
        })
        
        console.log('获取到的反馈数据:', response)
        if (response) {
          this.existingFeedback = response
          
          // 如果是管理员或已经完成了自己的反馈，默认显示汇总页
          if (this.roles.includes('admin') || this.roles.includes('tenant_admin') || 
              (this.existingFeedback && this.existingFeedback.status === 'completed')) {
            this.showSummary = true
          }
        }
      } catch (error) {
        // 可能是没有反馈，正常情况
        console.log('未找到现有反馈')
      }
    },
    async refreshSummary() {
      await this.getInterviewSummary()
      this.$message.success('数据已刷新')
    },
    async getInterviewSummary() {
      try {
        const interviewId = this.$route.params.id
        console.log('开始从store获取面试反馈汇总, ID:', interviewId)
        // 使用Vuex store获取面试反馈汇总
        const data = await this.$store.dispatch('interview/getInterviewFeedbackSummary', interviewId)
        console.log('Store返回的面试反馈汇总数据:', data)
        
        // 使用返回的数据
        if (data) {
          console.log('使用返回的数据更新feedbackSummary')
          this.feedbackSummary = data
          
          // 添加更详细的日志
          console.log('完成的反馈数量:', this.feedbackSummary.completed_count)
          console.log('招聘建议统计:', this.feedbackSummary.recommendation_summary)
        } else {
          console.warn('Store返回的数据为空，使用默认值')
          // 如果没有数据，使用默认值
          this.feedbackSummary = {
            interview_id: 0,
            average_score: 0,
            interviewer_count: 0,
            completed_count: 0,
            recommendation_summary: {},
            feedbacks: [],
            key_strengths: [],
            key_weaknesses: [],
            technical_averages: {},
            comprehensive_averages: {}
          }
        }
        console.log('更新后的feedbackSummary:', this.feedbackSummary)
      } catch (error) {
        console.error('获取反馈汇总失败:', error)
        this.$message.error('获取反馈汇总失败: ' + (error.response?.data?.message || error.message))
      }
    },
    async handleSubmitFeedback(feedbackData) {
      this.submitting = true
      try {
        const interviewId = this.$route.params.id
        // 使用Vuex store提交面试官反馈
        await this.$store.dispatch('interview/submitInterviewerFeedback', {
          id: interviewId,
          data: feedbackData
        })
        
        this.$message.success('反馈提交成功')
        
        // 刷新数据
        await this.getExistingFeedback()
        await this.getInterviewSummary()
        
        // 显示汇总页
        this.showSummary = true
      } catch (error) {
        console.error('提交反馈失败:', error)
        this.$message.error('提交反馈失败: ' + (error.response?.data?.message || error.message))
      } finally {
        this.submitting = false
      }
    },
    handleCancel() {
      this.$router.push('/interview/record')
    },
    handleViewFeedback(feedback) {
      this.selectedFeedback = feedback
      this.dialogVisible = true
    },
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
    getRecommendationText(recommendation) {
      const textMap = {
        strong_recommend: '强烈推荐',
        recommend: '推荐',
        neutral: '中立',
        not_recommend: '不推荐',
        strong_not_recommend: '强烈不推荐'
      }
      return textMap[recommendation] || '未评价'
    },
    getRecommendationTagType(recommendation) {
      const typeMap = {
        strong_recommend: 'success',
        recommend: 'success',
        neutral: 'info',
        not_recommend: 'warning',
        strong_not_recommend: 'danger'
      }
      return typeMap[recommendation] || 'info'
    },
    getRecommendationColor(recommendation) {
      const colorMap = {
        strong_recommend: '#67c23a',
        recommend: '#85ce61',
        neutral: '#909399',
        not_recommend: '#e6a23c',
        strong_not_recommend: '#f56c6c'
      }
      return colorMap[recommendation] || '#909399'
    },
    getTechnicalEvaluationLabel(key) {
      const labelMap = {
        coding_ability: '编码能力',
        problem_solving: '问题解决',
        system_design: '系统设计',
        algorithm: '算法理解',
        knowledge_depth: '技术深度',
        knowledge_breadth: '技术广度'
      }
      return labelMap[key] || key
    },
    getComprehensiveEvaluationLabel(key) {
      const labelMap = {
        communication: '沟通能力',
        teamwork: '团队协作',
        learning_ability: '学习能力',
        pressure_handling: '抗压能力',
        cultural_fit: '文化契合'
      }
      return labelMap[key] || key
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
    getEvalValue(obj, key1, key2) {
      if (!obj) return 0;
      if (obj[key1] != null) return obj[key1];
      if (key2 && obj[key2] != null) return obj[key2];
      return 0;
    },
    // 显示联系信息
    showContactInfo() {
      this.contactVisible = true;
    }
  }
}
</script>

<style lang="scss" scoped>
.app-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: calc(100vh - 84px);
}

.box-card {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  
  ::v-deep .el-card__header {
    background-color: #f9fafc;
    border-bottom: 1px solid #ebeef5;
    padding: 15px 20px;
    
    span {
      font-size: 18px;
      font-weight: 600;
      color: #303133;
    }
  }
}

.candidate-profile-card {
  margin-bottom: 24px;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
  background-color: #ffffff;
  border: none;
  
  &:hover {
    box-shadow: 0 8px 28px rgba(0, 0, 0, 0.15);
    transform: translateY(-3px);
  }
  
  ::v-deep .el-card__body {
    padding: 0;
  }
}

.candidate-profile-header {
  display: flex;
  align-items: center;
  padding: 28px;
  background: linear-gradient(120deg, #1a73e8 0%, #3b9fe6 100%);
  color: white;
  position: relative;
  overflow: hidden;
  
  &:before {
    content: "";
    position: absolute;
    top: -50%;
    right: -50%;
    width: 100%;
    height: 200%;
    background: rgba(255, 255, 255, 0.1);
    transform: rotate(25deg);
    pointer-events: none;
  }
  
  .candidate-avatar {
    margin-right: 28px;
    position: relative;
    z-index: 1;
    
    ::v-deep .el-avatar {
      border: 4px solid rgba(255, 255, 255, 0.8);
      box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
      transition: all 0.3s;
      
      &:hover {
        transform: scale(1.05);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.25);
      }
    }
  }
  
  .candidate-main-info {
    position: relative;
    z-index: 1;
    
    .candidate-name {
      margin-bottom: 10px;
      font-size: 24px;
      font-weight: 600;
      color: white;
      text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
    }
    
    .candidate-position {
      margin-bottom: 14px;
      font-size: 16px;
      color: rgba(255, 255, 255, 0.95);
      font-weight: 500;
      display: flex;
      align-items: center;
      
      i {
        margin-right: 8px;
      }
    }
    
    .interview-type {
      margin-top: 10px;
      
      ::v-deep .el-tag {
        border: 1px solid rgba(255, 255, 255, 0.4);
        padding: 6px 12px;
        font-weight: 500;
        letter-spacing: 0.5px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
        transition: all 0.3s;
        
        &:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }
      }
    }
  }
}

.el-divider {
  margin: 0;
  
  ::v-deep .el-divider__text {
    background-color: #f5f7fa;
    padding: 8px 20px;
    font-weight: 600;
    color: #606266;
    border-radius: 20px;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
    font-size: 15px;
  }
}

.candidate-details {
  margin: 24px;
  
  .detail-item {
    margin-bottom: 20px;
    display: flex;
    align-items: flex-start;
    transition: all 0.3s;
    padding: 12px;
    border-radius: 8px;
    
    &:hover {
      background-color: #f9fafc;
      transform: translateX(5px);
    }
    
    &:last-child {
      margin-bottom: 0;
    }
    
    .detail-icon {
      margin-right: 16px;
      color: #409eff;
      background-color: rgba(64, 158, 255, 0.1);
      border-radius: 50%;
      padding: 10px;
      width: 40px;
      height: 40px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 18px;
      transition: all 0.3s;
      
      &:hover {
        transform: rotate(15deg);
        background-color: rgba(64, 158, 255, 0.2);
      }
    }
    
    .detail-content {
      flex: 1;
      
      .detail-label {
        margin-bottom: 6px;
        font-size: 14px;
        color: #909399;
        font-weight: 500;
      }
      
      .detail-value {
        font-size: 15px;
        color: #303133;
        font-weight: 500;
      }
    }
  }
}

.interviewers-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  
  .interviewer-tag {
    margin: 3px;
    border-radius: 20px;
    transition: all 0.3s;
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
  }
}

.candidate-actions {
  display: flex;
  justify-content: flex-end;
  background-color: #f5f7fa;
  padding: 16px 24px;
  gap: 12px;
  border-top: 1px solid #ebeef5;
  
  .el-button {
    transition: all 0.3s ease;
    border-radius: 8px;
    padding: 10px 20px;
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    
    i {
      margin-right: 6px;
      font-size: 16px;
    }
  }
}

.summary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 16px;
  
  h3 {
    margin: 0;
    font-size: 18px;
    color: #303133;
    font-weight: 600;
  }
}

.summary-card {
  margin-bottom: 24px;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s;
  
  &:hover {
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  }
  
  ::v-deep .el-card__header {
    background: linear-gradient(135deg, #409eff 0%, #64b5f6 100%);
    
    span {
      color: white;
      font-weight: 500;
    }
  }
}

.summary-stats {
  display: flex;
  justify-content: space-around;
  margin: 30px 0;
  
  .stat-item {
    text-align: center;
    padding: 20px;
    border-radius: 8px;
    background-color: #f9fafc;
    min-width: 120px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    transition: all 0.3s ease;
    
    &:hover {
      transform: translateY(-5px);
      box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
    }
    
    .stat-value {
      font-size: 36px;
      font-weight: bold;
      color: #409eff;
      margin-bottom: 8px;
    }
    
    .stat-label {
      font-size: 14px;
      color: #606266;
      font-weight: 500;
    }
  }
}

.recommendation-stats {
  background-color: #f9fafc;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  
  h4 {
    margin-top: 0;
    margin-bottom: 20px;
    font-weight: 600;
    color: #303133;
    font-size: 16px;
  }
  
  .recommendation-summary {
    margin-bottom: 20px;
    
    .recommendation-total {
      margin-bottom: 16px;
      background-color: #fff;
      padding: 16px;
      border-radius: 8px;
      box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
      
      .total-label {
        display: inline-block;
        margin-right: 20px;
        margin-bottom: 8px;
        font-weight: 500;
      }
    }
    
    .recommendation-legend {
      display: flex;
      flex-wrap: wrap;
      gap: 16px;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
      background-color: #fff;
      padding: 16px;
      border-radius: 8px;
      box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
      
      .legend-item {
        display: flex;
        align-items: center;
        
        .legend-color {
          width: 16px;
          height: 16px;
          border-radius: 4px;
          margin-right: 8px;
        }
        
        .legend-text {
          font-weight: 500;
          font-size: 14px;
        }
      }
    }
  }
  
  .recommendation-description {
    margin-bottom: 16px;
    color: #606266;
    font-size: 14px;
    background-color: #f0f9eb;
    padding: 10px 16px;
    border-radius: 4px;
    border-left: 4px solid #67c23a;
    
    i {
      margin-right: 8px;
      color: #67c23a;
    }
  }
  
  .recommendation-progress-list {
    margin-bottom: 16px;
    
    .recommendation-progress-item {
      margin-bottom: 16px;
      background-color: #fff;
      padding: 16px;
      border-radius: 8px;
      box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
      transition: all 0.3s;
      
      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
      }
      
      .recommendation-label {
        margin-bottom: 12px;
        font-weight: 500;
      }
      
      .recommendation-progress {
        margin-bottom: 0;
        
        ::v-deep .el-progress-bar__outer {
          border-radius: 8px;
          background-color: #e9ecf2;
        }
        
        ::v-deep .el-progress-bar__inner {
          border-radius: 8px;
        }
        
        ::v-deep .el-progress__text {
          font-weight: 500;
          font-size: 14px !important;
          color: #606266;
        }
      }
    }
  }
  
  .el-empty {
    padding: 20px;
    background-color: #fff;
    border-radius: 8px;
  }
}

.strengths-weaknesses {
  display: flex;
  margin-bottom: 24px;
  gap: 20px;
  
  .strength-card,
  .weakness-card {
    flex: 1;
    border-radius: 8px;
    transition: all 0.3s;
    
    &:hover {
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
    }
  }
  
  .strength-card {
    ::v-deep .el-card__header {
      background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
      
      span {
        color: white;
        font-weight: 500;
      }
    }
  }
  
  .weakness-card {
    ::v-deep .el-card__header {
      background: linear-gradient(135deg, #f56c6c 0%, #fc9292 100%);
      
      span {
        color: white;
        font-weight: 500;
      }
    }
  }
  
  .strength-list,
  .weakness-list {
    padding-left: 20px;
    margin: 12px 0;
    
    li {
      margin-bottom: 12px;
      line-height: 1.5;
      color: #303133;
      
      &:last-child {
        margin-bottom: 0;
      }
    }
  }
}

// 技术和综合能力评分样式
h4 {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 24px 0 16px;
  padding-bottom: 10px;
  border-bottom: 1px solid #ebeef5;
}

ul {
  list-style-type: none;
  padding-left: 0;
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 24px;
  
  li {
    background-color: #f9fafc;
    padding: 12px 16px;
    border-radius: 6px;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
    flex: 1;
    min-width: 180px;
    color: #303133;
    font-weight: 500;
  }
}

.detailed-feedback {
  margin-bottom: 24px;
  border-radius: 8px;
  
  ::v-deep .el-table {
    border-radius: 8px;
    overflow: hidden;
    
    th {
      background-color: #f5f7fa;
      color: #303133;
      font-weight: 600;
    }
    
    .el-table__row {
      transition: all 0.3s;
      
      &:hover {
        background-color: #f0f5ff;
      }
    }
  }
}

.feedback-interviewer {
  margin-bottom: 24px;
  padding: 16px;
  background-color: #f9fafc;
  border-radius: 8px;
  
  h4 {
    margin-top: 0;
    margin-bottom: 16px;
    color: #303133;
    font-weight: 600;
    border-bottom: none;
  }
  
  .feedback-stats {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 20px;
    
    span {
      display: flex;
      align-items: center;
      background-color: white;
      padding: 8px 16px;
      border-radius: 6px;
      box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
    }
  }
}

.feedback-detail-card {
  margin-bottom: 24px;
  border-radius: 8px;
  
  ::v-deep .el-card__header {
    background-color: #f5f7fa;
  }
  
  .card-header-with-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .preparation-notes {
    white-space: pre-wrap;
    font-family: 'Courier New', Courier, monospace;
    background: #f8f8f8;
    padding: 16px;
    border-radius: 6px;
    font-size: 14px;
    line-height: 1.6;
    margin: 0;
    border: 1px solid #ebeef5;
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

// 添加响应式设计
@media screen and (max-width: 768px) {
  .strengths-weaknesses {
    flex-direction: column;
  }
  
  .summary-stats {
    flex-direction: column;
    align-items: center;
    gap: 16px;
    
    .stat-item {
      width: 100%;
    }
  }
}

// 添加一些额外的样式
.contact-education {
  margin-top: 20px;
  
  h4 {
    color: #606266;
    font-size: 16px;
    font-weight: 500;
    margin: 16px 0;
    padding-bottom: 10px;
    border-bottom: 1px solid #ebeef5;
  }
}
</style> 