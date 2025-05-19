<template>
  <div class="app-container">
    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span>面试官反馈</span>
      </div>

      <div v-loading="loading">
        <!-- 候选人基本信息 - 使用新组件 -->
        <interview-basic-info 
          v-if="interview && interview.candidateName" 
          :interview="interview" 
          :current-user="currentUser"
          @show-contact-info="showContactInfo"
          @view-resume="viewResume"
        />
        
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
                <div class="empty-state">
                  <i class="el-icon-document"></i>
                  <p>暂无推荐数据</p>
                </div>
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
                <li v-if="feedbackSummary.key_strengths.length === 0">
                  <div class="empty-state">
                    <i class="el-icon-document"></i>
                    <p>暂无数据</p>
                  </div>
                </li>
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
                <li v-if="feedbackSummary.key_weaknesses.length === 0">
                  <div class="empty-state">
                    <i class="el-icon-document"></i>
                    <p>暂无数据</p>
                  </div>
                </li>
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

    <!-- 使用新组件替换原来的详细反馈对话框 -->
    <feedback-detail-dialog
      :visible.sync="dialogVisible"
      :feedback="selectedFeedback"
    />

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
import InterviewBasicInfo from '@/components/InterviewBasicInfo'
import FeedbackDetailDialog from '@/components/FeedbackDetailDialog'

export default {
  name: 'InterviewFeedback',
  components: {
    InterviewFeedbackForm,
    InterviewBasicInfo,
    FeedbackDetailDialog
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
    // 显示联系信息
    showContactInfo() {
      this.contactVisible = true;
    },
    viewResume() {
      // 查看简历功能，可根据实际需求实现
      this.$message.info('查看简历功能待实现')
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

.empty-state {
  text-align: center;
  padding: 20px;
  background-color: #fafafa;
  border-radius: 8px;
  margin: 10px 0;
  
  i {
    font-size: 48px;
    color: #c0c4cc;
    margin-bottom: 16px;
    display: block;
  }
  
  p {
    font-size: 14px;
    color: #909399;
    margin: 0;
  }
}
</style> 