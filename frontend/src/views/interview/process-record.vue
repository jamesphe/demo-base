<template>
  <div class="app-container">
    <el-card class="box-card" shadow="hover">
      <div slot="header" class="clearfix header-container">
        <div class="page-title">
          <i class="el-icon-edit-outline"></i>
          <span>面试实时记录</span>
        </div>
        <div class="header-actions">
          <div class="interview-status-control">
            <el-tag :type="getInterviewStatusType(interview.status)">
              {{ getInterviewStatusText(interview.status) }}
            </el-tag>
            <el-button 
              v-if="interview.status === 'scheduled'"
              type="success" 
              size="small" 
              icon="el-icon-video-play"
              @click="startInterview"
              :loading="statusUpdating"
            >
              开始面试
            </el-button>
            <el-button 
              v-if="interview.status === 'in_progress'"
              type="danger" 
              size="small" 
              icon="el-icon-circle-check"
              @click="completeInterview"
              :loading="statusUpdating"
            >
              结束面试
            </el-button>
          </div>
          <el-divider direction="vertical"></el-divider>
          <el-button 
            type="primary" 
            size="small" 
            icon="el-icon-document-copy"
            @click="saveDraft"
            :disabled="!isModified"
          >
            保存草稿
          </el-button>
          <el-button
            type="success"
            size="small"
            icon="el-icon-check"
            @click="submitRecord"
            :disabled="!hasContent"
          >
            完成记录
          </el-button>
        </div>
      </div>

      <div v-loading="loading">
        <!-- 候选人基本信息 -->
        <el-card class="candidate-info-card" shadow="hover">
          <div class="info-header">
            <i class="el-icon-user"></i>
            <span>面试基本信息</span>
          </div>
          <el-row :gutter="20" class="info-row">
            <el-col :xs="24" :sm="12" :md="8">
              <div class="info-item">
                <div class="info-icon"><i class="el-icon-user-solid"></i></div>
                <div class="info-content-wrapper">
                  <div class="info-label">候选人</div>
                  <div class="info-content">{{ interview.candidateName || '暂无数据' }}</div>
                </div>
              </div>
            </el-col>
            <el-col :xs="24" :sm="12" :md="8">
              <div class="info-item">
                <div class="info-icon"><i class="el-icon-suitcase"></i></div>
                <div class="info-content-wrapper">
                  <div class="info-label">应聘职位</div>
                  <div class="info-content">{{ interview.candidatePosition || '暂无数据' }}</div>
                </div>
              </div>
            </el-col>
            <el-col :xs="24" :sm="12" :md="8">
              <div class="info-item">
                <div class="info-icon"><i class="el-icon-postcard"></i></div>
                <div class="info-content-wrapper">
                  <div class="info-label">面试类型</div>
                  <div class="info-content">
                    <el-tag :type="getInterviewTypeTag(interview.type)" v-if="interview.type" size="small">
                      {{ getInterviewTypeText(interview.type) }}
                    </el-tag>
                    <span v-else>暂无数据</span>
                  </div>
                </div>
              </div>
            </el-col>
            <el-col :xs="24" :sm="12" :md="8">
              <div class="info-item">
                <div class="info-icon"><i class="el-icon-date"></i></div>
                <div class="info-content-wrapper">
                  <div class="info-label">面试时间</div>
                  <div class="info-content">
                    <template v-if="typeof interview.time === 'string' && interview.time.includes('NaN')">
                      {{ interview.time }}
                    </template>
                    <template v-else>
                      {{ formatDateTime(interview.time) || '暂无数据' }}
                    </template>
                  </div>
                </div>
              </div>
            </el-col>
            <el-col :xs="24" :sm="12" :md="8">
              <div class="info-item">
                <div class="info-icon"><i class="el-icon-location"></i></div>
                <div class="info-content-wrapper">
                  <div class="info-label">面试地点</div>
                  <div class="info-content">{{ interview.location || '暂无数据' }}</div>
                </div>
              </div>
            </el-col>
            <el-col :xs="24" :sm="12" :md="8">
              <div class="info-item">
                <div class="info-icon"><i class="el-icon-s-custom"></i></div>
                <div class="info-content-wrapper">
                  <div class="info-label">面试官</div>
                  <div class="info-content">
                    <el-tag
                      v-for="interviewer in interview.interviewers"
                      :key="interviewer.id"
                      size="small"
                      class="interviewer-tag"
                      :type="interviewer.id === currentUser.id ? 'success' : 'info'"
                      effect="light"
                    >
                      {{ interviewer.name || interviewer.username }}
                    </el-tag>
                    <span v-if="!interview.interviewers || interview.interviewers.length === 0">暂无数据</span>
                  </div>
                </div>
              </div>
            </el-col>
          </el-row>
        </el-card>

        <el-divider content-position="center">面试过程</el-divider>

        <!-- 两栏布局：左侧记录区，右侧面试指导 -->
        <el-row :gutter="0" class="interview-content-row">
          <!-- 左侧记录区 -->
          <el-col :span="leftColSpan" class="record-column">
            <div class="column-title">
              <i class="el-icon-edit"></i> 面试记录
            </div>
            
            <!-- 面试记录工具栏 -->
            <div class="record-toolbar">
              <el-button-group>
                <el-button size="small" icon="el-icon-timer" @click="addTimestamp">添加时间戳</el-button>
                <el-button size="small" icon="el-icon-star-off" @click="addSection('优势')">记录优势</el-button>
                <el-button size="small" icon="el-icon-warning-outline" @click="addSection('不足')">记录不足</el-button>
                <el-button size="small" icon="el-icon-question" @click="addSection('疑问')">记录疑问</el-button>
              </el-button-group>
              
              <div class="timer-section">
                <i class="el-icon-time"></i>
                <span class="timer">{{ formatTime(elapsedTime) }}</span>
                <el-button 
                  size="mini" 
                  :type="timerRunning ? 'danger' : 'primary'"
                  icon="el-icon-video-pause"
                  v-if="timerRunning"
                  @click="pauseTimer"
                >
                  暂停
                </el-button>
                <el-button 
                  size="mini" 
                  type="primary"
                  icon="el-icon-video-play"
                  v-else
                  @click="startTimer"
                >
                  开始
                </el-button>
              </div>
            </div>

            <!-- 面试记录编辑区 -->
            <div class="record-content">
              <el-input
                type="textarea"
                :rows="15"
                placeholder="在此记录面试过程的问答内容、候选人表现等..."
                v-model="recordContent"
                @input="handleContentChange"
              />
            </div>

            <!-- 快速评分区 -->
            <div class="record-ratings">
              <el-form :model="ratings" label-position="top" :inline="true">
                <div class="ratings-title">快速评分</div>
                <el-form-item label="技术能力">
                  <el-rate v-model="ratings.technical" @change="handleRatingChange" />
                </el-form-item>
                <el-form-item label="沟通能力">
                  <el-rate v-model="ratings.communication" @change="handleRatingChange" />
                </el-form-item>
                <el-form-item label="解决问题">
                  <el-rate v-model="ratings.problemSolving" @change="handleRatingChange" />
                </el-form-item>
                <el-form-item label="文化契合">
                  <el-rate v-model="ratings.cultureFit" @change="handleRatingChange" />
                </el-form-item>
                <el-form-item label="综合评价">
                  <el-rate v-model="ratings.overall" @change="handleRatingChange" />
                </el-form-item>
              </el-form>
            </div>

            <!-- 面试官总结 -->
            <div class="record-summary">
              <div class="summary-title">面试总结</div>
              <el-input
                type="textarea"
                :rows="4"
                placeholder="请总结候选人的整体表现、优势和不足..."
                v-model="summary"
                @input="handleContentChange"
              />
            </div>

            <!-- 招聘建议 -->
            <div class="record-recommendation">
              <div class="recommendation-title">招聘建议</div>
              <el-radio-group v-model="recommendation" @change="handleContentChange">
                <el-radio label="strongly_recommend">强烈推荐</el-radio>
                <el-radio label="recommend">推荐</el-radio>
                <el-radio label="neutral">中立</el-radio>
                <el-radio label="not_recommend">不推荐</el-radio>
                <el-radio label="strongly_not_recommend">强烈不推荐</el-radio>
              </el-radio-group>
            </div>
          </el-col>
          
          <!-- 可拖动分隔线 -->
          <el-tooltip content="拖动调整宽度" placement="top" :open-delay="500" :enterable="false">
            <div class="resizer" @mousedown="startResize" :class="{ 'active': isResizing }"></div>
          </el-tooltip>
          
          <!-- 右侧面试准备内容 -->
          <el-col :span="24 - leftColSpan" class="guide-column">
            <div class="column-title">
              <i class="el-icon-document"></i> 面试准备指导
              <el-tag size="mini" type="success" v-if="preparationInfo.preparation_notes">
                <i class="el-icon-success"></i> AI生成
              </el-tag>
            </div>
            
            <div v-loading="preparationInfo.loading" class="preparation-notes-container">
              <div class="preparation-scroll-area">
                <div v-if="preparationInfo.preparation_notes" class="preparation-notes">
                  <div class="preparation-header">
                    <span class="preparation-title">AI生成面试指导</span>
                    <div class="preparation-actions-bar">
                      <el-tooltip content="复制内容" placement="top">
                        <i class="el-icon-document-copy action-icon" @click="copyPreparationNotes"></i>
                      </el-tooltip>
                      <el-tooltip content="全屏查看" placement="top">
                        <i class="el-icon-full-screen action-icon" @click="toggleFullScreen"></i>
                      </el-tooltip>
                    </div>
                  </div>
                  <div v-html="formattedPreparationNotes" class="preparation-content"></div>
                </div>
                
                <div v-else class="no-preparation-notes">
                  <i class="el-icon-document" style="font-size: 48px; color: #DCDFE6; margin-bottom: 15px;"></i>
                  <div class="empty-tip">
                    <p>暂无面试准备内容</p>
                    <p>您可以在面试准备页面生成面试指导内容</p>
                  </div>
                </div>
                
                <!-- 关注点列表 -->
                <div v-if="preparationInfo.focus_points && preparationInfo.focus_points.length > 0" class="focus-points-container">
                  <h4>关注点</h4>
                  <el-tag 
                    v-for="(point, index) in preparationInfo.focus_points" 
                    :key="index"
                    type="info"
                    effect="plain"
                    class="focus-point-tag"
                  >
                    {{ point }}
                  </el-tag>
                </div>
              </div>
              
              <!-- 底部操作栏 -->
              <div class="preparation-actions">
                <el-button 
                  size="small" 
                  type="text" 
                  icon="el-icon-view"
                  @click="$router.push(`/interview/preparation/${$route.params.id}`)"
                >
                  查看完整面试准备
                </el-button>
              </div>
            </div>
          </el-col>
        </el-row>

        <!-- 操作按钮 -->
        <div class="record-actions">
          <el-button type="primary" @click="saveDraft" :disabled="!isModified">保存草稿</el-button>
          <el-button type="success" @click="submitRecord" :disabled="!hasContent">完成记录</el-button>
          <el-button @click="$router.back()">返回</el-button>
        </div>
      </div>
    </el-card>

    <!-- 保存成功对话框 -->
    <el-dialog
      title="保存成功"
      :visible.sync="saveSuccessVisible"
      width="30%"
      :show-close="false"
    >
      <div class="success-dialog-content">
        <i class="el-icon-success success-icon"></i>
        <div class="success-message">面试记录已成功保存</div>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button type="primary" @click="handleSaveSuccess">确定</el-button>
      </span>
    </el-dialog>
    
    <!-- 全屏查看面试指导对话框 -->
    <el-dialog
      title="面试准备指导"
      :visible.sync="showFullScreen"
      width="80%"
      class="fullscreen-dialog"
      top="5vh"
    >
      <div v-loading="preparationInfo.loading">
        <div v-if="preparationInfo.preparation_notes" class="fullscreen-content">
          <div v-html="formattedPreparationNotes" class="preparation-content"></div>
        </div>
        <div v-else class="no-content">
          <i class="el-icon-document" style="font-size: 48px; color: #DCDFE6; margin-bottom: 15px;"></i>
          <p>暂无面试准备内容</p>
        </div>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="copyPreparationNotes" type="primary" plain icon="el-icon-document-copy">
          复制内容
        </el-button>
        <el-button @click="showFullScreen = false">关闭</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import { getInterviewDetail, submitInterviewerFeedback, getInterviewPreparation, updateInterviewStatus } from '@/api/interview'
import { parseTime } from '@/utils'
import MarkdownIt from 'markdown-it'

export default {
  name: 'InterviewProcessRecord',
  data() {
    return {
      interview: {
        candidateName: '',
        candidatePosition: '',
        type: '',
        time: '',
        location: '',
        interviewers: [],
        status: 'scheduled'
      },
      statusUpdating: false,
      recordContent: '',
      summary: '',
      recommendation: 'neutral',
      ratings: {
        technical: 3,
        communication: 3,
        problemSolving: 3,
        cultureFit: 3,
        overall: 3
      },
      loading: false,
      isModified: false,
      timerRunning: false,
      elapsedTime: 0,
      timerInterval: null,
      drawerVisible: false,
      currentUser: {
        id: '',
        name: ''
      },
      saveSuccessVisible: false,
      technicalTemplates: [
        { title: '前端技能扎实', content: '候选人的前端基础知识扎实，对HTML/CSS/JavaScript有深入理解，对主流框架（如React/Vue）使用经验丰富。' },
        { title: '算法能力优秀', content: '候选人的算法思维清晰，能够快速理解并解决复杂问题，代码实现简洁高效。' },
        { title: '系统设计薄弱', content: '候选人在系统设计方面经验不足，对大型应用架构理解有限，需要加强学习。' }
      ],
      strengthTemplates: [
        { title: '学习能力强', content: '候选人展现出很强的学习能力，能够快速理解新概念并应用。' },
        { title: '团队合作好', content: '候选人过往经历表明善于团队协作，乐于分享知识，善于沟通。' }
      ],
      weaknessTemplates: [
        { title: '经验不足', content: '候选人在实际项目经验方面略显不足，有些概念仅停留在理论层面。' },
        { title: '沟通需改进', content: '候选人在表达技术观点时不够清晰，需要提高专业沟通能力。' }
      ],
      summaryTemplates: [
        { title: '推荐入职', content: '整体而言，候选人技术基础扎实，学习能力强，文化契合度高，推荐录用。' },
        { title: '建议再观察', content: '候选人有一定潜力，但在某些关键能力上还需提高，建议安排下一轮面试进一步评估。' }
      ],
      activeGuideTab: 'process',
      preparationInfo: {
        focus_points: [],
        preparation_notes: '',
        interview_guide: '',
        loading: false
      },
      showFullScreen: false,
      md: new MarkdownIt({
        html: true,
        breaks: true,
        linkify: true,
        typographer: true
      }),
      leftColSpan: 16,
      isResizing: false,
      startX: 0,
      initialLeftColSpan: 16,
      containerWidth: 0,
      scrollAreaHeight: 600
    }
  },
  computed: {
    hasContent() {
      return (
        this.recordContent.trim() !== '' ||
        this.summary.trim() !== ''
      )
    },
    formattedPreparationNotes() {
      if (!this.preparationInfo.preparation_notes) return ''
      return this.md.render(this.preparationInfo.preparation_notes)
    }
  },
  created() {
    this.fetchInterviewDetail()
    this.currentUser = {
      id: this.$store.getters.userId || '',
      name: this.$store.getters.name || ''
    }

    this.loadDraft()
  },
  beforeDestroy() {
    this.clearTimer()
  },
  methods: {
    async fetchInterviewDetail() {
      this.loading = true
      try {
        const interviewId = this.$route.params.id
        if (!interviewId) {
          this.$message.error('未找到面试ID')
          return
        }

        const response = await getInterviewDetail(interviewId)
        console.log('接口返回数据:', response)
        
        if (response) {
          const data = response
          
          this.interview = {
            id: data.id,
            candidateName: data.resume?.name || '未知候选人',
            candidatePosition: data.job?.title || '未知职位',
            type: data.interview_type || data.interviewType,
            time: data.schedule_time || data.scheduleTime,
            location: data.location || '未指定地点',
            interviewers: data.interviewers || [],
            status: data.status || 'scheduled'
          }
          
          this.fetchInterviewPreparation(interviewId)
        } else {
          this.$message.error('无法获取面试详情')
        }
        
        if (this.interview.status === 'in_progress') {
          this.startTimer()
        }
      } catch (error) {
        console.error('获取面试详情失败:', error)
        this.$message.error('获取面试详情失败')
      } finally {
        this.loading = false
      }
    },
    async fetchInterviewPreparation(interviewId) {
      this.preparationInfo.loading = true
      try {
        const response = await getInterviewPreparation(interviewId)
        console.log('面试准备信息:', response)
        
        if (response) {
          this.preparationInfo = {
            ...this.preparationInfo,
            preparation_notes: response.preparationNotes || '',
            focus_points: response.focusPoints || [],
            interview_guide: response.interviewGuide || '',
            loading: false
          }
        }
      } catch (error) {
        console.error('获取面试准备信息失败:', error)
        this.$message.warning('获取面试指导文档失败')
      } finally {
        this.preparationInfo.loading = false
      }
    },
    formatDateTime(timestamp) {
      if (!timestamp) {
        return '暂无数据'
      }
      
      if (typeof timestamp === 'string' && timestamp.includes('NaN')) {
        return timestamp
      }
      
      try {
        if (typeof timestamp === 'string' && timestamp.includes('T')) {
          const date = new Date(timestamp)
          if (!isNaN(date.getTime())) {
            const year = date.getFullYear()
            const month = String(date.getMonth() + 1).padStart(2, '0')
            const day = String(date.getDate()).padStart(2, '0')
            const hours = String(date.getHours()).padStart(2, '0')
            const minutes = String(date.getMinutes()).padStart(2, '0')
            
            const formattedTime = `${year}-${month}-${day} ${hours}:${minutes}`
            return formattedTime
          } else {
            return timestamp
          }
        }
        
        const result = parseTime(timestamp, '{y}-{m}-{d} {h}:{i}')
        return result || timestamp
      } catch (error) {
        return typeof timestamp === 'string' ? timestamp : '日期格式错误'
      }
    },
    getInterviewTypeText(type) {
      const types = {
        first: '初试',
        second: '复试',
        final: '终试'
      }
      return types[type] || type
    },
    getInterviewTypeTag(type) {
      const tags = {
        first: 'info',
        second: 'success',
        final: 'warning'
      }
      return tags[type] || ''
    },
    startTimer() {
      if (this.timerRunning) return
      
      this.timerRunning = true
      this.timerInterval = setInterval(() => {
        this.elapsedTime += 1
      }, 1000)
    },
    pauseTimer() {
      this.timerRunning = false
      if (this.timerInterval) {
        clearInterval(this.timerInterval)
        this.timerInterval = null
      }
    },
    clearTimer() {
      this.pauseTimer()
      this.elapsedTime = 0
    },
    formatTime(seconds) {
      const hours = Math.floor(seconds / 3600)
      const minutes = Math.floor((seconds % 3600) / 60)
      const secs = seconds % 60
      
      return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
    },
    addTimestamp() {
      const now = new Date()
      const timestamp = `[${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}] `
      
      this.insertAtCursor(timestamp)
      this.isModified = true
    },
    addSection(sectionName) {
      const section = `\n\n----- ${sectionName} -----\n`
      this.insertAtCursor(section)
      this.isModified = true
    },
    insertAtCursor(text) {
      const textarea = document.querySelector('.record-content textarea')
      if (!textarea) {
        this.recordContent += text
        this.isModified = true
        return
      }
      
      const start = textarea.selectionStart
      const end = textarea.selectionEnd
      
      const newText = this.recordContent.substring(0, start) + text + this.recordContent.substring(end)
      this.recordContent = newText
      
      this.$nextTick(() => {
        textarea.focus()
        textarea.setSelectionRange(start + text.length, start + text.length)
      })
      
      this.isModified = true
    },
    handleContentChange() {
      this.isModified = true
    },
    handleRatingChange() {
      this.isModified = true
    },
    insertTemplate(template) {
      this.insertAtCursor(`\n${template.content}\n`)
      this.drawerVisible = false
    },
    saveDraft() {
      this.loading = true
      try {
        const interviewId = this.$route.params.id
        const draft = {
          recordContent: this.recordContent,
          summary: this.summary,
          recommendation: this.recommendation,
          ratings: this.ratings,
          timestamp: new Date().getTime()
        }
        
        localStorage.setItem(`interview_draft_${interviewId}_${this.currentUser.id}`, JSON.stringify(draft))
        
        this.$message.success('草稿已保存')
        this.isModified = false
      } catch (error) {
        console.error('保存草稿失败:', error)
        this.$message.error('保存草稿失败')
      } finally {
        this.loading = false
      }
    },
    loadDraft() {
      try {
        const interviewId = this.$route.params.id
        const draftJson = localStorage.getItem(`interview_draft_${interviewId}_${this.currentUser.id}`)
        
        if (draftJson) {
          const draft = JSON.parse(draftJson)
          this.recordContent = draft.recordContent || ''
          this.summary = draft.summary || ''
          this.recommendation = draft.recommendation || 'neutral'
          this.ratings = draft.ratings || {
            technical: 3,
            communication: 3,
            problemSolving: 3,
            cultureFit: 3,
            overall: 3
          }
          
          this.isModified = false
        }
      } catch (error) {
        console.error('加载草稿失败:', error)
      }
    },
    async submitRecord() {
      if (!this.hasContent) {
        this.$message.warning('请先记录面试内容或总结')
        return
      }
      
      this.loading = true
      try {
        const interviewId = this.$route.params.id
        
        const feedbackData = {
          process_record: this.recordContent,
          summary: this.summary,
          hiring_recommendation: this.recommendation,
          evaluation_score: this.ratings.overall,
          technical_evaluation: {
            coding_ability: this.ratings.technical,
            problem_solving: this.ratings.problemSolving,
            comments: {
              "coding_ability": this.summary,
              "problem_solving": this.summary
            }
          },
          comprehensive_evaluation: {
            communication: this.ratings.communication,
            cultural_fit: this.ratings.cultureFit,
            comments: {
              "communication": this.summary,
              "cultural_fit": this.summary
            }
          }
        }
        
        await submitInterviewerFeedback(interviewId, feedbackData)
        
        localStorage.removeItem(`interview_draft_${interviewId}_${this.currentUser.id}`)
        
        this.saveSuccessVisible = true
      } catch (error) {
        console.error('提交面试记录失败:', error)
        this.$message.error('提交面试记录失败: ' + (error.response?.data?.message || error.message))
      } finally {
        this.loading = false
      }
    },
    handleSaveSuccess() {
      this.saveSuccessVisible = false
      this.$router.push(`/interview/feedback/${this.$route.params.id}`)
    },
    copyPreparationNotes() {
      const textarea = document.createElement('textarea')
      textarea.value = this.preparationInfo.preparation_notes
      document.body.appendChild(textarea)
      
      textarea.select()
      document.execCommand('copy')
      
      document.body.removeChild(textarea)
      
      this.$message.success('面试指导内容已复制到剪贴板')
    },
    toggleFullScreen() {
      this.showFullScreen = !this.showFullScreen
    },
    startResize(event) {
      this.isResizing = true
      this.startX = event.clientX
      document.body.style.cursor = 'col-resize'
      document.body.style.userSelect = 'none'
      
      this.initialLeftColSpan = this.leftColSpan
      this.containerWidth = this.$el.querySelector('.interview-content-row').offsetWidth
      
      document.documentElement.style.setProperty('--left-col-span', this.leftColSpan)
    },
    resize(event) {
      if (this.isResizing) {
        event.preventDefault()
        const dx = event.clientX - this.startX
        const percentDelta = (dx / this.containerWidth)
        
        const spanChange = Math.floor(percentDelta * 24)
        
        const newSpan = Math.max(10, Math.min(20, this.initialLeftColSpan + spanChange))
        
        if (newSpan !== this.leftColSpan) {
          this.leftColSpan = newSpan
          document.documentElement.style.setProperty('--left-col-span', this.leftColSpan)
        }
      }
    },
    endResize() {
      this.isResizing = false
      document.body.style.cursor = ''
      document.body.style.userSelect = ''
    },
    updateScrollAreaHeight() {
      const viewportHeight = window.innerHeight
      const scrollArea = this.$el.querySelector('.preparation-scroll-area')
      if (scrollArea) {
        const rect = scrollArea.getBoundingClientRect()
        const availableHeight = viewportHeight - rect.top - 70
        this.scrollAreaHeight = Math.max(400, availableHeight)
        document.documentElement.style.setProperty('--scroll-area-height', `${this.scrollAreaHeight}px`)
      }
    },
    getInterviewStatusText(status) {
      const statusMap = {
        scheduled: '待面试',
        in_progress: '进行中',
        completed: '已完成',
        evaluated: '已评估',
        cancelled: '已取消'
      }
      return statusMap[status] || status
    },
    getInterviewStatusType(status) {
      const typeMap = {
        scheduled: 'info',
        in_progress: 'warning',
        completed: 'success',
        evaluated: 'success',
        cancelled: 'danger'
      }
      return typeMap[status] || 'info'
    },
    async startInterview() {
      if (this.interview.status !== 'scheduled') {
        return
      }
      
      this.statusUpdating = true
      try {
        const interviewId = this.$route.params.id
        
        await updateInterviewStatus(interviewId, {
          status: 'in_progress'
        })
        
        this.interview.status = 'in_progress'
        this.$message.success('面试已开始')
        
        this.startTimer()
      } catch (error) {
        console.error('更新面试状态失败:', error)
        this.$message.error('开始面试失败: ' + (error.response?.data?.message || error.message))
      } finally {
        this.statusUpdating = false
      }
    },
    async completeInterview() {
      if (this.interview.status !== 'in_progress') {
        return
      }
      
      this.statusUpdating = true
      try {
        const interviewId = this.$route.params.id
        
        await updateInterviewStatus(interviewId, {
          status: 'completed'
        })
        
        this.interview.status = 'completed'
        this.$message.success('面试已完成')
        
        this.pauseTimer()
      } catch (error) {
        console.error('更新面试状态失败:', error)
        this.$message.error('完成面试失败: ' + (error.response?.data?.message || error.message))
      } finally {
        this.statusUpdating = false
      }
    }
  },
  mounted() {
    document.addEventListener('mousemove', this.resize)
    document.addEventListener('mouseup', this.endResize)
    document.documentElement.style.setProperty('--left-col-span', this.leftColSpan)
    
    this.$nextTick(() => {
      this.updateScrollAreaHeight()
      window.addEventListener('resize', this.updateScrollAreaHeight)
    })
  },
  beforeDestroy() {
    this.clearTimer()
    document.removeEventListener('mousemove', this.resize)
    document.removeEventListener('mouseup', this.endResize)
    window.removeEventListener('resize', this.updateScrollAreaHeight)
  }
}
</script>

<style lang="scss" scoped>
.app-container {
  padding: 20px;
}

.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  display: flex;
  align-items: center;
  font-size: 18px;
  font-weight: 500;
  
  i {
    margin-right: 8px;
    color: #409EFF;
  }
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.interview-status-control {
  display: flex;
  align-items: center;
  gap: 10px;
  
  .el-tag {
    min-width: 60px;
    text-align: center;
  }
}

.el-divider--vertical {
  height: 20px;
  margin: 0 10px;
}

.candidate-info-card {
  margin-bottom: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
  
  &:hover {
    box-shadow: 0 4px 15px 0 rgba(0, 0, 0, 0.08);
  }
}

.info-header {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #ebeef5;
  
  i {
    margin-right: 8px;
    color: #409EFF;
    font-size: 18px;
  }
  
  span {
    font-weight: 500;
    font-size: 16px;
    color: #303133;
  }
}

.info-row {
  margin-bottom: 15px;
}

.info-item {
  margin-bottom: 15px;
  display: flex;
  align-items: flex-start;
  padding: 8px 10px;
  border-radius: 6px;
  transition: background-color 0.3s;
  
  &:hover {
    background-color: #f9fafc;
  }
  
  .info-icon {
    margin-right: 12px;
    color: #409EFF;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: rgba(64, 158, 255, 0.1);
    border-radius: 50%;
    
    i {
      font-size: 14px;
    }
  }
  
  .info-content-wrapper {
    flex: 1;
  }
  
  .info-label {
    font-weight: 500;
    color: #909399;
    margin-bottom: 5px;
    font-size: 13px;
  }
  
  .info-content {
    color: #303133;
    font-size: 14px;
    word-break: break-all;
    
    .el-tag {
      margin-right: 5px;
      margin-bottom: 5px;
    }
  }
}

.record-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 20px 0;
  padding: 10px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.timer-section {
  display: flex;
  align-items: center;
  
  .timer {
    font-family: monospace;
    font-size: 16px;
    margin: 0 10px;
    font-weight: bold;
  }
  
  i {
    color: #409EFF;
    font-size: 18px;
  }
}

.record-content {
  margin-bottom: 20px;
}

.record-ratings {
  margin: 20px 0;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 4px;
  
  .ratings-title {
    font-weight: 500;
    font-size: 16px;
    margin-bottom: 10px;
    color: #303133;
  }
}

.record-summary, .record-recommendation {
  margin-bottom: 20px;
  
  .summary-title, .recommendation-title {
    font-weight: 500;
    font-size: 16px;
    margin-bottom: 10px;
    color: #303133;
  }
}

.record-actions {
  display: flex;
  justify-content: center;
  margin-top: 30px;
  
  .el-button {
    min-width: 100px;
    margin: 0 10px;
  }
}

.templates-container {
  padding: 20px;
  
  .templates-category {
    margin-bottom: 25px;
    
    h3 {
      border-bottom: 1px solid #EBEEF5;
      padding-bottom: 10px;
      margin-bottom: 10px;
    }
    
    .el-button {
      display: block;
      text-align: left;
      margin-bottom: 5px;
    }
  }
}

.success-dialog-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  
  .success-icon {
    font-size: 56px;
    color: #67C23A;
    margin-bottom: 20px;
  }
  
  .success-message {
    font-size: 18px;
  }
}

@media (max-width: 768px) {
  .record-toolbar {
    flex-direction: column;
    
    .el-button-group {
      margin-bottom: 10px;
    }
  }
  
  .record-ratings {
    .el-form-item {
      margin-right: 0;
    }
  }
  
  .interview-content-row {
    flex-direction: column;
  }
  
  .record-column, .guide-column {
    width: 100% !important;
  }
  
  .resizer {
    display: none;
  }
  
  .preparation-scroll-area {
    max-height: 350px;
  }
}

.interview-content-row {
  margin-bottom: 20px;
  position: relative;
  min-height: 500px;
  display: flex;
}

.record-column {
  padding-right: 10px;
  position: relative;
}

.guide-column {
  padding-left: 10px;
  position: relative;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.column-title {
  font-weight: 500;
  font-size: 16px;
  margin-bottom: 10px;
  color: #303133;
}

.guide-content {
  padding: 10px;
}

.guide-help-icon {
  margin-left: 5px;
  color: #409EFF;
  cursor: pointer;
}

.question-list {
  padding-left: 20px;
}

.guide-section-title {
  font-weight: 500;
  font-size: 16px;
  margin-bottom: 10px;
  color: #303133;
}

.template-item {
  padding: 10px;
  cursor: pointer;
  border-bottom: 1px solid #EBEEF5;
  
  &:last-child {
    border-bottom: none;
  }
  
  .template-title {
    font-weight: 500;
    font-size: 16px;
    margin-bottom: 5px;
    color: #303133;
  }
  
  .template-content {
    color: #606266;
  }
}

.criteria-section {
  margin-bottom: 15px;
  
  h4 {
    margin-bottom: 10px;
    color: #303133;
  }
  
  .criteria-description {
    color: #606266;
    
    div {
      padding: 5px 0;
    }
    
    strong {
      color: #303133;
    }
  }
}

.preparation-notes-container {
  padding: 10px;
  background-color: #f8f9fa;
  border-radius: 4px;
  margin-bottom: 20px;
  display: flex;
  flex-direction: column;
  flex: 1;
}

.preparation-scroll-area {
  overflow-y: auto;
  flex: 1;
  max-height: var(--scroll-area-height, 600px);
  padding-right: 5px;
  
  &::-webkit-scrollbar {
    width: 6px;
  }
  
  &::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 3px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: #d0d0d0;
    border-radius: 3px;
  }
  
  &::-webkit-scrollbar-thumb:hover {
    background: #a0a0a0;
  }
  
  scrollbar-width: thin;
  scrollbar-color: #d0d0d0 #f1f1f1;
}

.preparation-notes {
  margin-bottom: 10px;
}

.preparation-content {
  color: #606266;
  line-height: 1.6;
  padding: 10px;
  
  h1 {
    font-size: 20px;
    font-weight: 600;
    margin: 20px 0 12px 0;
    padding-bottom: 6px;
    border-bottom: 1px solid #EBEEF5;
    color: #303133;
  }
  
  h2 {
    font-size: 18px;
    font-weight: 500;
    margin: 16px 0 10px 0;
    color: #303133;
  }
  
  h3 {
    font-size: 16px;
    font-weight: 500;
    margin: 12px 0 8px 0;
    color: #303133;
  }
  
  p {
    margin: 8px 0;
  }
  
  strong {
    font-weight: 600;
    color: #409EFF;
  }
  
  em {
    font-style: italic;
    color: #606266;
  }
  
  ul, ol {
    padding-left: 20px;
    margin: 8px 0;
  }
  
  li {
    margin: 4px 0;
  }
  
  pre {
    margin: 10px 0;
    padding: 10px;
    background-color: #f5f7fa;
    border-radius: 4px;
    overflow-x: auto;
  }
  
  code {
    font-family: 'Courier New', Courier, monospace;
  }
  
  p code {
    padding: 2px 5px;
    margin: 0 2px;
    background-color: #f5f7fa;
    border-radius: 3px;
    color: #E6A23C;
  }
  
  blockquote {
    padding: 8px 16px;
    margin: 10px 0;
    border-left: 4px solid #409EFF;
    background-color: #ecf5ff;
    color: #606266;
    font-style: italic;
  }
  
  table {
    border-collapse: collapse;
    margin: 10px 0;
    width: 100%;
  }
  
  th, td {
    border: 1px solid #EBEEF5;
    padding: 8px;
    text-align: left;
  }
  
  th {
    background-color: #f5f7fa;
    font-weight: 500;
  }
  
  hr {
    margin: 15px 0;
    border: none;
    border-top: 1px solid #EBEEF5;
  }
}

.no-preparation-notes {
  text-align: center;
  padding: 40px 20px;
  background-color: #f8f9fa;
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  
  .empty-tip {
    font-size: 14px;
    color: #909399;
    margin-top: 5px;
    
    p {
      margin: 5px 0;
      
      &:first-child {
        font-size: 16px;
        color: #606266;
        font-weight: 500;
      }
    }
  }
}

.focus-points-container {
  margin-top: 10px;
  margin-bottom: 10px;
}

.focus-point-tag {
  margin-right: 5px;
}

.preparation-actions {
  margin-top: 10px;
  text-align: right;
  padding-top: 5px;
  border-top: 1px solid #EBEEF5;
}

.preparation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.preparation-title {
  font-weight: 500;
  font-size: 16px;
  color: #303133;
}

.preparation-actions-bar {
  display: flex;
  align-items: center;
}

.action-icon {
  margin-left: 5px;
  color: #409EFF;
  cursor: pointer;
}

.show-full-screen-dialog {
  width: 80%;
  max-width: 800px;
}

.fullscreen-dialog {
  .el-dialog {
    max-width: 1000px;
  }
  
  .el-dialog__body {
    padding: 0;
  }
}

.fullscreen-content {
  padding: 10px 20px;
  max-height: 70vh;
  overflow-y: auto;
  
  .preparation-content {
    padding: 15px;
    background-color: #fff;
    border-radius: 4px;
  }
}

.no-content {
  padding: 40px;
  text-align: center;
  color: #909399;
  font-size: 16px;
}

.resizer {
  width: 6px;
  background-color: #EBEEF5;
  cursor: col-resize;
  position: absolute;
  top: 0;
  bottom: 0;
  z-index: 10;
  left: calc(100% * (var(--left-col-span) / 24) - 3px);
  transition: background-color 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &:hover, &:active, &.active {
    background-color: #409EFF;
  }
  
  &::after {
    content: "";
    height: 40px;
    width: 2px;
    background-color: #909399;
    display: none;
  }
  
  &:hover::after, &.active::after {
    display: block;
  }
}
</style> 