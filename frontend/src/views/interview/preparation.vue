<template>
  <div class="app-container">
    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span>
          <i class="el-icon-document"></i>
          面试准备
        </span>
      </div>

      <div v-loading="loading">
        <!-- 面试基本信息 - 新设计 -->
        <transition name="fade">
          <el-card class="interview-info-card" shadow="hover">
            <div class="interview-header">
              <div class="interview-title">
                <i class="el-icon-user"></i>
                <span>{{ interview.candidateName || '候选人信息' }}</span>
                <el-tag class="position-tag" effect="plain">{{ interview.candidatePosition }}</el-tag>
                <el-tag v-if="interview.job && interview.job.department" class="department-tag">
                  {{ interview.job.department }}
                </el-tag>
              </div>
              <div class="interview-status">
                <el-tag :type="getStatusType(interview.status)" effect="dark" size="medium">
                  {{ getStatusText(interview.status) }}
                </el-tag>
                <span class="interview-id">ID: {{ interview.id }}</span>
              </div>
            </div>
            
            <el-divider content-position="left">
              <i class="el-icon-info"></i> 面试信息
            </el-divider>
            
            <div class="info-grid">
              <div class="info-item">
                <div class="info-label">
                  <i class="el-icon-date"></i>
                  面试时间
                </div>
                <div class="info-value">{{ formatDateTime(interview.time) }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">
                  <i class="el-icon-location"></i>
                  面试地点
                </div>
                <div class="info-value">{{ interview.location }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">
                  <i class="el-icon-medal"></i>
                  面试类型
                </div>
                <div class="info-value">
                  <el-tag :type="getInterviewTypeTag(interview.type)" size="small">
                    {{ getInterviewTypeText(interview.type) }}
                  </el-tag>
                </div>
              </div>
              <div class="info-item">
                <div class="info-label">
                  <i class="el-icon-s-custom"></i>
                  面试官
                </div>
                <div class="info-value interviewer-list">
                  <el-tag
                    v-for="interviewer in interview.interviewers"
                    :key="interviewer.id"
                    size="small"
                    class="interviewer-tag"
                    effect="plain"
                  >
                    {{ interviewer.name }}
                  </el-tag>
                </div>
              </div>
            </div>
            
            <template v-if="interview.resume">
              <el-divider content-position="left">
                <i class="el-icon-user"></i> 候选人详细信息
              </el-divider>
              
              <div class="info-grid three-columns">
                <div class="info-item">
                  <div class="info-label">
                    <i class="el-icon-phone-outline"></i>
                    联系电话
                  </div>
                  <div class="info-value">{{ interview.resume.phone || '-' }}</div>
                </div>
                <div class="info-item">
                  <div class="info-label">
                    <i class="el-icon-message"></i>
                    电子邮箱
                  </div>
                  <div class="info-value">{{ interview.resume.email || '-' }}</div>
                </div>
                <div class="info-item">
                  <div class="info-label">
                    <i class="el-icon-collection"></i>
                    学历
                  </div>
                  <div class="info-value">{{ interview.resume.highestEducation || '-' }}</div>
                </div>
                <div class="info-item">
                  <div class="info-label">
                    <i class="el-icon-reading"></i>
                    专业
                  </div>
                  <div class="info-value">{{ interview.resume.major || '-' }}</div>
                </div>
                <div class="info-item" v-if="interview.notes">
                  <div class="info-label">
                    <i class="el-icon-document"></i>
                    备注
                  </div>
                  <div class="info-value">{{ interview.notes }}</div>
                </div>
              </div>
            </template>
          </el-card>
        </transition>

        <!-- 面试准备表单 -->
        <el-form
          ref="preparationForm"
          :model="preparationForm"
          label-width="120px"
          class="preparation-form"
        >
          <!-- 面试角色选择 -->
          <transition name="slide-fade">
            <el-card class="preparation-card">
              <div slot="header">
                <i class="el-icon-user"></i>
                <span>面试角色</span>
              </div>
              <el-form-item label="选择角色">
                <el-radio-group v-model="preparationForm.role" size="medium">
                  <el-radio-button label="department_head">部门负责人</el-radio-button>
                  <el-radio-button label="technical">技术面试官</el-radio-button>
                  <el-radio-button label="hr">人事面试官</el-radio-button>
                  <el-radio-button label="other">其他</el-radio-button>
                </el-radio-group>
                <el-input 
                  v-if="preparationForm.role === 'other'" 
                  v-model="preparationForm.otherRole" 
                  placeholder="请输入您的角色" 
                  style="width: 200px; margin-left: 10px;"
                />
                <el-tag 
                  v-if="preparationForm.role !== 'other'" 
                  class="role-tag" 
                  type="success" 
                  effect="plain">
                  当前身份：{{ getRoleText(preparationForm.role) }}
                </el-tag>
                <el-tag 
                  v-else-if="preparationForm.otherRole" 
                  class="role-tag" 
                  type="success" 
                  effect="plain">
                  当前身份：{{ preparationForm.otherRole }}
                </el-tag>
              </el-form-item>
            </el-card>
          </transition>

          <!-- 面试关注点 -->
          <transition name="slide-fade">
            <el-card class="preparation-card">
              <div slot="header">
                <i class="el-icon-star-on"></i>
                <span>面试关注点</span>
                <el-button
                  style="float: right; padding: 3px 0"
                  type="text"
                  @click="handleSaveFocusPoints"
                >
                  <i class="el-icon-upload2"></i>
                  保存为模板
                </el-button>
              </div>
              <el-form-item>
                <div class="template-selector">
                  <span class="template-label">模板：</span>
                  <el-select v-model="selectedTemplate" placeholder="选择模板" @change="applyTemplate" size="small">
                    <el-option label="技术面试" value="technical"></el-option>
                    <el-option label="管理面试" value="department_head"></el-option>
                    <el-option label="HR面试" value="hr"></el-option>
                    <el-option label="通用模板" value="general"></el-option>
                    <el-option label="我的模板" value="custom" v-if="hasCustomTemplate"></el-option>
                  </el-select>
                </div>
                
                <div class="quick-tags">
                  <span class="quick-tags-label">快速添加：</span>
                  <el-tag 
                    v-for="tag in quickTags" 
                    :key="tag.content"
                    size="small"
                    class="quick-tag"
                    @click="addQuickTag(tag.content)">
                    {{ tag.label }}
                  </el-tag>
                </div>
                
                <div class="category-selector">
                  <el-tabs v-model="activeCategory" type="card" size="small">
                    <el-tab-pane label="全部" name="all"></el-tab-pane>
                    <el-tab-pane label="技术能力" name="technical">
                      <div class="category-tags">
                        <el-tag 
                          v-for="tag in technicalTags" 
                          :key="tag.label"
                          size="mini"
                          class="category-tag"
                          @click="addCategoryTag(tag)">
                          {{ tag.label }}
                        </el-tag>
                      </div>
                    </el-tab-pane>
                    <el-tab-pane label="软技能" name="soft">
                      <div class="category-tags">
                        <el-tag 
                          v-for="tag in softSkillTags" 
                          :key="tag.label"
                          size="mini"
                          class="category-tag"
                          @click="addCategoryTag(tag)">
                          {{ tag.label }}
                        </el-tag>
                      </div>
                    </el-tab-pane>
                    <el-tab-pane label="管理能力" name="management">
                      <div class="category-tags">
                        <el-tag 
                          v-for="tag in managementTags" 
                          :key="tag.label"
                          size="mini"
                          class="category-tag"
                          @click="addCategoryTag(tag)">
                          {{ tag.label }}
                        </el-tag>
                      </div>
                    </el-tab-pane>
                  </el-tabs>
                </div>
                
                <el-input
                  type="textarea"
                  :rows="8"
                  placeholder="请输入面试关注点内容，您可以自由添加需要关注的任何方面..."
                  v-model="preparationForm.focusContent"
                />
                <div class="focus-tip">
                  <i class="el-icon-info"></i>
                  <span>提示：您可以自由组织关注点内容，例如包括技术能力、项目经验、综合素质、团队协作、沟通能力等多个方面</span>
                </div>
                
                <div class="preview-toggle">
                  <el-switch
                    v-model="showPreview"
                    active-text="预览"
                    inactive-text="编辑"
                    active-color="#409EFF"
                  ></el-switch>
                </div>
                
                <div class="focus-actions">
                  <el-button 
                    size="mini" 
                    type="danger" 
                    plain 
                    icon="el-icon-delete"
                    @click="confirmClearFocus">
                    清空内容
                  </el-button>
                  <el-button 
                    size="mini" 
                    type="primary" 
                    plain 
                    icon="el-icon-magic-stick"
                    @click="formatFocusContent">
                    格式化内容
                  </el-button>
                </div>
                
                <div v-if="showPreview" class="focus-preview">
                  <div class="preview-header">
                    <i class="el-icon-view"></i> 预览效果
                  </div>
                  <div class="preview-content" v-html="renderedFocusContent"></div>
                </div>
              </el-form-item>
            </el-card>
          </transition>

          <!-- 生成面试指导文档 -->
          <transition name="slide-fade">
            <el-card class="preparation-card">
              <div slot="header">
                <i class="el-icon-document"></i>
                <span>面试指导文档</span>
                <div style="float: right;">
                  <el-button
                    type="primary"
                    size="small"
                    icon="el-icon-magic-stick"
                    @click="generateInterviewGuide"
                    :loading="generatingGuide || guideLoading"
                    :disabled="isGenerating"
                  >
                    {{ generatingGuide ? '生成中...' : '生成文档' }}
                  </el-button>
                  <el-button
                    type="success"
                    size="small"
                    icon="el-icon-download"
                    @click="exportToPDF"
                    :disabled="!interviewGuide"
                  >
                    导出PDF
                  </el-button>
                </div>
              </div>
              
              <div v-if="interviewGuide || forceShowGuide" class="interview-guide">
                <div class="guide-actions">
                  <el-button 
                    type="primary" 
                    size="small" 
                    icon="el-icon-edit"
                    @click="editMode = !editMode"
                  >
                    {{ editMode ? '完成编辑' : '编辑文档' }}
                  </el-button>
                </div>
                
                <div v-if="editMode" class="guide-editor">
                  <el-input
                    type="textarea"
                    :rows="20"
                    v-model="interviewGuide"
                    placeholder="面试指导文档内容"
                    class="markdown-editor"
                  />
                  <div class="editor-tip">
                    <i class="el-icon-info"></i>
                    <span>支持Markdown格式编辑，包括标题、列表、加粗等</span>
                  </div>
                </div>
                <div v-else class="guide-content" ref="guideContent" :class="{'guide-generating': guideLoading}">
                  <div v-if="!interviewGuide && !guideLoading" class="empty-guide">
                    <i class="el-icon-document"></i>
                    <span>暂无面试指南，点击"生成面试指南"按钮生成</span>
                  </div>
                  <div v-else-if="guideLoading && !interviewGuide" class="loading-guide">
                    <i class="el-icon-loading"></i>
                    <span>正在生成面试指南...</span>
                  </div>
                  <div v-else-if="interviewGuide" class="markdown-content" v-html="renderedGuide"></div>
                </div>
              </div>
              <div v-else class="empty-tip">
                <div class="empty-content">
                  <i class="el-icon-document"></i>
                  <p>点击"生成文档"按钮，AI将根据您的角色和关注点生成面试指导文档</p>
                  <p class="empty-tip-sub">您添加的关注点越详细，生成的面试指导文档越有针对性</p>
                </div>
              </div>
            </el-card>
          </transition>

          <!-- 操作按钮 -->
          <div class="form-actions">
            <el-button @click="handleCancel" icon="el-icon-back">返 回</el-button>
            <el-button type="primary" @click="handleSave" :loading="saving" icon="el-icon-check">保 存</el-button>
          </div>
        </el-form>
      </div>
    </el-card>
  </div>
</template>

<script>
import { mapActions, mapGetters } from 'vuex'
import html2pdf from 'html2pdf.js'
import MarkdownIt from 'markdown-it'

export default {
  name: 'InterviewPreparation',
  data() {
    return {
      loading: false,
      saving: false,
      generatingGuide: false,
      generatingQuestions: false,
      generatingAnalysis: false,
      editMode: false,
      interview: {},
      preparation: {},
      interviewGuide: '',
      preparationForm: {
        role: 'technical',
        otherRole: '',
        focusContent: '',
      },
      isGenerating: false,
      guideLoading: false,
      markdown: new MarkdownIt({
        breaks: true,
        linkify: true,
        typographer: true,
        html: false
      }),
      defaultFocusPoints: {
        technical: {
          technical: '## 技术能力\n1. 技术栈深度和广度评估\n2. 核心技术原理理解\n3. 系统设计能力\n4. 问题解决思路\n5. 代码质量和编程规范\n\n## 项目经验\n1. 项目架构和技术选型\n2. 技术难点攻克经历\n3. 性能优化经验\n4. 项目部署和运维经验\n5. 技术方案决策过程\n\n## 综合素质\n1. 技术学习能力\n2. 技术文档编写能力\n3. 技术分享经验\n4. 团队协作能力\n5. 技术创新意识',
          comprehensive: '技术学习能力、技术文档编写能力、技术分享经验、团队协作能力、技术创新意识'
        },
        department_head: {
          technical: '## 领导能力\n1. 技术视野和发展规划\n2. 技术团队管理经验\n3. 跨部门协作能力\n4. 技术战略规划能力\n5. 技术风险控制\n\n## 管理经验\n1. 项目全局把控能力\n2. 资源调配经验\n3. 项目风险预估\n4. 团队建设经验\n5. 项目进度管理\n\n## 综合素质\n1. 领导力和决策能力\n2. 沟通和协调能力\n3. 危机处理能力\n4. 团队文化建设\n5. 员工培养计划',
          comprehensive: '领导力和决策能力、沟通和协调能力、危机处理能力、团队文化建设、员工培养计划'
        },
        hr: {
          technical: '## 基础评估\n1. 基础技术认知\n2. 技术发展趋势了解\n3. 技术岗位要求把握\n4. 技术人才评估标准\n5. 行业技术水平认知\n\n## 工作态度\n1. 项目经验评估\n2. 团队协作表现\n3. 项目责任心\n4. 项目压力处理\n5. 项目管理意识\n\n## 软技能与文化\n1. 职业规划清晰度\n2. 价值观契合度\n3. 沟通表达能力\n4. 学习成长意愿\n5. 团队融入度',
          comprehensive: '职业规划清晰度、价值观契合度、沟通表达能力、学习成长意愿、团队融入度'
        }
      },
      quickTags: [
        { label: '技术能力', content: '\n\n## 技术能力\n1. 专业技术深度\n2. 技术广度和学习能力\n3. 问题解决思路' },
        { label: '项目经验', content: '\n\n## 项目经验\n1. 项目角色和职责\n2. 技术难点解决\n3. 项目管理经验' },
        { label: '沟通能力', content: '\n\n## 沟通能力\n1. 表达清晰度\n2. 专业术语表达\n3. 团队沟通效率' },
        { label: '团队协作', content: '\n\n## 团队协作\n1. 团队贡献\n2. 冲突处理\n3. 跨团队合作' },
        { label: '学习成长', content: '\n\n## 学习成长\n1. 持续学习能力\n2. 技术视野\n3. 职业规划' }
      ],
      selectedTemplate: '',
      hasCustomTemplate: false,
      customTemplate: '',
      showPreview: false,
      activeCategory: 'all',
      technicalTags: [
        { label: '算法能力', content: '算法设计与分析能力' },
        { label: '代码质量', content: '代码质量与编程风格' },
        { label: '架构设计', content: '系统架构设计能力' },
        { label: '调试能力', content: '问题诊断与调试能力' },
        { label: '性能优化', content: '系统性能优化经验' },
        { label: '技术前瞻', content: '技术趋势把握能力' },
        { label: '安全意识', content: '安全编码与防护意识' }
      ],
      softSkillTags: [
        { label: '沟通效率', content: '沟通效率与表达清晰度' },
        { label: '团队合作', content: '团队协作与贡献能力' },
        { label: '解决冲突', content: '冲突处理与协调能力' },
        { label: '时间管理', content: '时间管理与任务规划' },
        { label: '学习能力', content: '自主学习与知识更新' },
        { label: '抗压能力', content: '压力承受与情绪管理' },
        { label: '创新思维', content: '创新思维与问题解决' }
      ],
      managementTags: [
        { label: '团队管理', content: '团队建设与人员管理' },
        { label: '资源调配', content: '资源规划与合理调配' },
        { label: '目标设定', content: '目标制定与分解能力' },
        { label: '决策能力', content: '决策判断与风险评估' },
        { label: '绩效管理', content: '绩效评估与反馈能力' },
        { label: '战略思维', content: '战略规划与执行能力' },
        { label: '变革管理', content: '组织变革与推动能力' }
      ],
      forceShowGuide: false,
    }
  },
  computed: {
    renderedGuide() {
      // 简化日志输出
      if (!this.interviewGuide) return '';
      
      // 使用markdown-it渲染markdown内容
      let rendered = this.markdown.render(this.interviewGuide);
      
      // 如果文档仍在生成中，添加一个闪烁的光标效果
      if (this.guideLoading || this.generatingGuide) {
        rendered += '<span class="blinking-cursor">|</span>';
      }
      
      return rendered;
    },
    
    formattedGuide() {
      if (!this.interviewGuide) return '';
      
      // 将换行符转换为<br>标签 (保留此方法用于兼容性)
      let formatted = this.interviewGuide.replace(/\n/g, '<br>');
      
      // 如果文档仍在生成中，添加一个闪烁的光标效果
      if (this.guideLoading || this.generatingGuide) {
        formatted += '<span class="blinking-cursor">|</span>';
      }
      
      return formatted;
    },
    renderedFocusContent() {
      if (!this.preparationForm.focusContent) return '<div class="empty-preview">暂无内容</div>';
      return this.markdown.render(this.preparationForm.focusContent);
    },
  },
  watch: {
    'preparationForm.role': {
      handler(newRole) {
        if (newRole === 'other') {
          this.clearFocusPoints()
          return
        }
        
        const defaultPoints = this.defaultFocusPoints[newRole]
        if (defaultPoints) {
          this.preparationForm.focusContent = defaultPoints.technical
        }
      },
      immediate: true
    }
  },
  async created() {
    this.loading = true;
    
    try {
      // 先获取面试基本信息
      await this.getInterviewInfo();
      
      // 然后获取准备信息
      await this.getPreparationInfo().catch(error => {
        console.error('获取面试准备信息失败，将使用默认值:', error);
        this.$message.warning('获取面试准备信息失败，将使用默认模板');
      });
      
      // 尝试获取关注点
      await this.getFocusPoints().catch(() => {});
    } catch (error) {
      console.error('初始化面试准备数据失败:', error);
      this.$message.error('加载面试基本信息失败，请刷新页面重试');
    } finally {
      this.loading = false;
    }
  },
  mounted() {
    // 在DOM挂载后检查内容是否正确显示
    this.$nextTick(() => {
      this.checkGuideDisplay();
    });
  },
  methods: {
    ...mapActions('interview', [
      'getInterviewDetail',
      'getInterviewPreparation',
      'generateInterviewPreparation',
      'updateInterviewPreparation',
      'getInterviewerFocusPoints',
      'saveInterviewerFocusPoints',
      'saveInterviewPreparationNotes'
    ]),
    ...mapActions('ai', [
      'generateQuestions',
      'generateAnalysis',
      'getSuggestions',
      'getEvaluationSuggestions',
      'streamGenerateInterviewGuide'
    ]),
    async getInterviewInfo() {
      try {
        const interviewId = this.$route.params.id
        
        const response = await this.$store.dispatch('interview/getInterviewDetail', interviewId)
        
        if (!response || !response.resumeId || !response.jobId) {
          throw new Error('面试信息不完整')
        }
        
        // 统一数据格式，确保所有字段都有值
        this.interview = {
          // 基本信息
          id: response.id,
          resumeId: response.resumeId,
          jobId: response.jobId,
          resume_id: response.resumeId, // 兼容性字段
          job_id: response.jobId, // 兼容性字段
          
          // 面试状态信息
          status: response.status || 'scheduled',
          type: response.interviewType || 'first',
          time: response.scheduleTime,
          location: response.location || '-',
          duration: response.duration || 60,
          notes: response.notes || '',
          
          // 时间信息
          createdAt: response.createdAt,
          updatedAt: response.updatedAt,
          
          // 候选人信息
          candidateName: response.resume?.name || response.resumeTitle || '-',
          candidatePosition: response.job?.title || response.jobTitle || '-',
          
          // 简历信息
          resume: response.resume ? {
            id: response.resume.id,
            name: response.resume.name || '-',
            phone: response.resume.phone || '-',
            email: response.resume.email || '-',
            gender: response.resume.gender || '-',
            highestEducation: response.resume.highestEducation || '-',
            major: response.resume.major || '-'
          } : null,
          
          // 职位信息
          job: response.job ? {
            id: response.job.id,
            title: response.job.title || '-',
            department: response.job.department || '-'
          } : null,
          
          // 面试官信息
          interviewers: (response.interviewers || []).map(interviewer => ({
            id: interviewer.id,
            name: interviewer.username || '-',
            email: interviewer.email || '-',
            avatar: interviewer.avatar || null
          }))
        }
        
        // 检查响应中是否有preparationNotes，如果有则直接设置到interviewGuide
        if (response.preparationNotes) {
          console.log('在面试详情中发现preparationNotes，直接设置为interviewGuide')
          this.interviewGuide = response.preparationNotes
        }
        
        return Promise.resolve(response)
      } catch (error) {
        this.$message.error(error.message || '获取面试信息失败')
        return Promise.reject(error)
      }
    },
    async getPreparationInfo() {
      try {
        const interviewId = this.$route.params.id
        
        // 处理可能的后端500错误
        let preparation
        try {
          preparation = await this.getInterviewPreparation(interviewId)
          console.log('获取到的preparation数据:', preparation)
          // 检查preparation是否为undefined
          if (!preparation) {
            console.log('preparation数据为空')
            return Promise.resolve({})
          }
          
          // 检查字段名（驼峰式或下划线式）
          console.log('API返回字段:', Object.keys(preparation))
          const hasPreparationNotes = !!preparation.preparationNotes
          const hasSnakeCase = !!preparation.preparation_notes
          console.log('是否有preparationNotes:', hasPreparationNotes)
          console.log('是否有preparation_notes:', hasSnakeCase)
          
          // 尝试输出前10个字符检查格式
          if (preparation.preparationNotes) {
            console.log('preparationNotes前10个字符:', preparation.preparationNotes.substring(0, 10))
          } else if (preparation.preparation_notes) {
            console.log('preparation_notes前10个字符:', preparation.preparation_notes.substring(0, 10))
          }
        } catch (apiError) {
          console.error('API调用失败:', apiError)
          // 如果是服务器错误，使用一个空对象
          if (apiError.response && apiError.response.status >= 500) {
            return Promise.resolve({})
          }
          // 其他错误则继续抛出
          throw apiError
        }
        
        // 检查返回数据是否有效
        if (!preparation) {
          return Promise.resolve({})
        }
        
        this.preparation = preparation
        console.log('是否有focusPoints:', !!(preparation && preparation.focusPoints))
        if (preparation.focusPoints) {
          this.preparationForm = {
            ...this.preparationForm,
            focusContent: preparation.focusPoints.content || preparation.focusPoints.technical || '',
          }
        }
        
        // 检查多种可能的字段名
        const hasInterviewGuide = !!(preparation && preparation.interviewGuide)
        const hasPreparationNotes = !!(preparation && preparation.preparationNotes)
        const hasPreparationNotesSnake = !!(preparation && preparation.preparation_notes)
        
        console.log('是否有interviewGuide:', hasInterviewGuide)
        console.log('是否有preparationNotes:', hasPreparationNotes)
        console.log('是否有preparation_notes:', hasPreparationNotesSnake)
        
        if (preparation.interviewGuide) {
          this.interviewGuide = preparation.interviewGuide
          console.log('设置interviewGuide:', this.interviewGuide.substring(0, 50) + '...')
        } else if (preparation.preparationNotes) {
          // 如果没有interviewGuide但有preparationNotes，则使用preparationNotes
          console.log('准备设置preparationNotes到interviewGuide')
          this.interviewGuide = preparation.preparationNotes
          console.log('使用preparationNotes设置interviewGuide:', this.interviewGuide.substring(0, 50) + '...')
        } else if (preparation.preparation_notes) {
          // 使用下划线形式的字段名
          console.log('准备设置preparation_notes到interviewGuide')
          this.interviewGuide = preparation.preparation_notes
          console.log('使用preparation_notes设置interviewGuide:', this.interviewGuide.substring(0, 50) + '...')
        }
        
        // 设置角色信息
        if (preparation.role) {
          const roleMapping = {
            '技术面试官': 'technical',
            '部门负责人': 'department_head',
            '人事面试官': 'hr'
          }
          
          const mappedRole = roleMapping[preparation.role]
          if (mappedRole) {
            this.preparationForm.role = mappedRole
          } else {
            // 如果不是预定义角色，则设为"其他"
            this.preparationForm.role = 'other'
            this.preparationForm.otherRole = preparation.role
          }
        }
        
        return Promise.resolve(preparation)
      } catch (error) {
        console.error('获取面试准备信息失败:', error)
        // 不在这里显示错误消息，统一在created钩子中处理
        return Promise.reject(error)
      }
    },
    async getFocusPoints() {
      try {
        let focusPoints
        try {
          focusPoints = await this.getInterviewerFocusPoints()
        } catch (apiError) {
          console.error('获取面试官关注点失败:', apiError)
          // 任何API错误都返回null而不中断执行
          return Promise.resolve(null)
        }
        
        if (focusPoints && focusPoints.content) {
          // 如果没有通过getPreparationInfo获取到面试准备内容，则使用面试官模板
          if (!this.preparationForm.focusContent || this.preparationForm.focusContent === '') {
            this.preparationForm = {
              ...this.preparationForm,
              focusContent: focusPoints.content || focusPoints.technical || '',
            }
          }
          
          // 设置自定义模板
          this.customTemplate = focusPoints.content || focusPoints.technical || ''
          this.hasCustomTemplate = !!this.customTemplate
        }
        
        return Promise.resolve(focusPoints)
      } catch (error) {
        console.error('获取面试关注点失败:', error)
        // 不显示错误消息，因为这个是次要功能
        return Promise.resolve(null) // 返回resolve而不是reject，这样不会中断链式调用
      }
    },
    applyTemplate(templateKey) {
      if (templateKey === 'custom' && this.customTemplate) {
        this.preparationForm.focusContent = this.customTemplate;
        return;
      }
      
      if (templateKey === 'general') {
        this.preparationForm.focusContent = '# 面试关注点\n\n## 专业能力\n1. 专业知识和技能掌握程度\n2. 解决问题的思路和方法\n3. 专业术语的理解和使用\n\n## 项目经验\n1. 过往项目的角色和职责\n2. 项目中遇到的挑战及解决方案\n3. 对项目成果的贡献\n\n## 综合素质\n1. 沟通表达能力\n2. 团队协作精神\n3. 学习能力和成长意愿\n4. 职业规划与公司匹配度';
        return;
      }
      
      const defaultPoints = this.defaultFocusPoints[templateKey];
      if (defaultPoints) {
        this.preparationForm.focusContent = defaultPoints.technical;
      }
    },
    
    addQuickTag(content) {
      // 如果当前没有内容或内容为空，则先添加标题
      if (!this.preparationForm.focusContent || this.preparationForm.focusContent.trim() === '') {
        this.preparationForm.focusContent = '# 面试关注点';
      }
      
      // 添加快速标签内容
      this.preparationForm.focusContent += content;
      
      // 显示提示
      this.$message.success('已添加关注点');
    },
    
    async handleSaveFocusPoints() {
      try {
        await this.$store.dispatch('interview/saveInterviewerFocusPoints', {
          content: this.preparationForm.focusContent
        })
        
        // 保存为自定义模板
        this.customTemplate = this.preparationForm.focusContent;
        this.hasCustomTemplate = true;
        
        this.$message.success('关注点保存成功')
      } catch (error) {
        // 显示具体的错误信息，包括后端403状态的详细信息
        const errorDetail = error.response?.data?.detail || '保存关注点失败';
        this.$message.error(errorDetail);
      }
    },
    async generateInterviewGuide() {
      // 如果已经在生成中，不要重复生成
      if (this.isGenerating) {
        this.$message.info('正在生成中，请稍候...');
        return;
      }

      try {
        // 设置生成状态
        this.isGenerating = true;
        this.guideLoading = true;
        this.generatingGuide = true;
        
        // 清空当前的面试指南内容
        this.interviewGuide = '';
        
        const interviewId = this.$route.params.id;
        
        // 使用 resumeId 或 resume_id
        const resumeId = this.interview.resumeId || this.interview.resume_id;
        const jobId = this.interview.jobId || this.interview.job_id;
        
        if (!resumeId || !jobId) {
          this.$message.error('缺少必要的面试信息，无法生成面试指南');
          this.guideLoading = false;
          this.isGenerating = false;
          this.generatingGuide = false;
          return;
        }
        
        const guideElement = this.$refs.guideContent;
        
        // 构建请求数据
        const requestData = {
          resumeId: resumeId,
          jobId: jobId,
          role: this.getRoleText(this.preparationForm.role === 'other' ? 
                this.preparationForm.otherRole : this.preparationForm.role),
          focusPoints: {
            content: this.preparationForm.focusContent
          }
        };
        
        this.$message.info('开始生成面试指南，这可能需要一些时间...');
        
        // 使用流式生成API
        await this.$store.dispatch('ai/streamGenerateInterviewGuide', {
          data: requestData,
          onChunk: (chunk) => {
            // 流式接收数据块并更新UI
            if (chunk && chunk.length > 0) {
              // 更新面试指南内容
              this.interviewGuide += chunk;
              
              // 确保DOM更新后滚动到底部
              this.$nextTick(() => {
                if (guideElement) {
                  guideElement.scrollTop = guideElement.scrollHeight;
                } else {
                  // 尝试查找备用元素
                  const container = document.querySelector('.guide-content');
                  if (container) {
                    container.scrollTop = container.scrollHeight;
                  }
                }
              });
            }
          }
        });
        
        if (this.interviewGuide && this.interviewGuide.trim().length > 0) {
          this.$message.success('面试指南生成完成');
        } else {
          this.$message.warning('面试指南生成完成，但内容为空');
        }
      } catch (error) {
        // 针对特定错误类型提供更友好的提示
        let errorMessage = '未知错误';
        if (error.message && error.message.includes('超时')) {
          errorMessage = '请求超时，请稍后重试';
        } else if (error.message && error.message.includes('网络')) {
          errorMessage = '网络连接错误，请检查网络连接并重试';
        } else if (error.message) {
          errorMessage = error.message;
        }
        
        this.$message.error(`生成面试指南失败: ${errorMessage}`);
        
        // 恢复之前的内容，如果有的话
        if (!this.interviewGuide && this.preparation && this.preparation.interviewGuide) {
          this.interviewGuide = this.preparation.interviewGuide;
          this.$message.info('已恢复之前保存的面试指南');
        }
      } finally {
        this.guideLoading = false;
        this.isGenerating = false;
        this.generatingGuide = false;
      }
    },
    exportToPDF() {
      if (!this.interviewGuide) {
        this.$message.warning('没有可导出的文档')
        return
      }
      
      const element = document.createElement('div')
      element.innerHTML = `
        <div style="padding: 20px;">
          <h1 style="text-align: center; margin-bottom: 30px;">面试指导文档</h1>
          
          <div style="margin-bottom: 30px; border: 1px solid #ebeef5; padding: 15px; border-radius: 5px;">
            <h2 style="margin-top: 0; margin-bottom: 15px; border-bottom: 1px solid #ebeef5; padding-bottom: 10px;">基本信息</h2>
            <table style="width: 100%; border-collapse: collapse;">
              <tr>
                <td style="width: 120px; font-weight: bold; padding: 8px 0;">候选人：</td>
                <td style="padding: 8px 0;">${this.interview.candidateName || '-'}</td>
                <td style="width: 120px; font-weight: bold; padding: 8px 0;">应聘职位：</td>
                <td style="padding: 8px 0;">${this.interview.candidatePosition || '-'}</td>
              </tr>
              <tr>
                <td style="font-weight: bold; padding: 8px 0;">所属部门：</td>
                <td style="padding: 8px 0;">${this.interview.job?.department || '-'}</td>
                <td style="font-weight: bold; padding: 8px 0;">面试类型：</td>
                <td style="padding: 8px 0;">${this.getInterviewTypeText(this.interview.type)}</td>
              </tr>
              <tr>
                <td style="font-weight: bold; padding: 8px 0;">面试时间：</td>
                <td style="padding: 8px 0;">${this.formatDateTime(this.interview.time)}</td>
                <td style="font-weight: bold; padding: 8px 0;">面试地点：</td>
                <td style="padding: 8px 0;">${this.interview.location || '-'}</td>
              </tr>
              <tr>
                <td style="font-weight: bold; padding: 8px 0;">最高学历：</td>
                <td style="padding: 8px 0;">${this.interview.resume?.highestEducation || '-'}</td>
                <td style="font-weight: bold; padding: 8px 0;">专业：</td>
                <td style="padding: 8px 0;">${this.interview.resume?.major || '-'}</td>
              </tr>
              <tr>
                <td style="font-weight: bold; padding: 8px 0;">联系电话：</td>
                <td style="padding: 8px 0;">${this.interview.resume?.phone || '-'}</td>
                <td style="font-weight: bold; padding: 8px 0;">邮箱：</td>
                <td style="padding: 8px 0;">${this.interview.resume?.email || '-'}</td>
              </tr>
            </table>
          </div>
          
          <h2 style="margin-bottom: 15px;">面试指导内容</h2>
          <div class="markdown-content">${this.renderedGuide}</div>
          
          <div style="margin-top: 30px; font-size: 12px; color: #909399; text-align: center;">
            此文档由 AI 面试助手自动生成于 ${new Date().toLocaleString('zh-CN')}
          </div>
        </div>
      `
      
      // 添加CSS样式，确保PDF中Markdown内容正确渲染
      const style = document.createElement('style')
      style.textContent = `
        .markdown-content {
          font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
          line-height: 1.6;
          color: #333;
        }
        .markdown-content h1, .markdown-content h2, .markdown-content h3 {
          margin-top: 20px;
          margin-bottom: 10px;
          font-weight: 600;
        }
        .markdown-content h1 {
          font-size: 22px;
          padding-bottom: 10px;
          border-bottom: 1px solid #eee;
        }
        .markdown-content h2 {
          font-size: 18px;
          padding-bottom: 5px;
          border-bottom: 1px solid #eee;
        }
        .markdown-content h3 {
          font-size: 16px;
        }
        .markdown-content ul, .markdown-content ol {
          padding-left: 20px;
          margin-bottom: 15px;
        }
        .markdown-content li {
          margin-bottom: 5px;
        }
        .markdown-content p {
          margin-bottom: 10px;
        }
      `
      element.appendChild(style)
      
      const opt = {
        margin: 1,
        filename: `面试指导_${this.interview.candidateName}_${new Date().toLocaleDateString()}.pdf`,
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2 },
        jsPDF: { unit: 'in', format: 'a4', orientation: 'portrait' }
      }
      
      this.$message.info('正在生成PDF，请稍候...')
      html2pdf().set(opt).from(element).save().then(() => {
        this.$message.success('PDF导出成功')
      }).catch(error => {
        this.$message.error('PDF导出失败')
      })
    },
    async handleSave() {
      this.saving = true
      try {
        const interviewId = this.$route.params.id
        
        // 获取用户信息
        const userData = await this.$store.dispatch('user/getInfo')
        const currentUserId = userData.id || this.$store.state.user.id
        
        if (!currentUserId) {
          throw new Error('无法获取当前用户ID')
        }
        
        // 使用updateInterviewPreparation接口，调用新的后端API
        await this.$store.dispatch('interview/updateInterviewPreparation', {
          interviewId,
          data: {
            focusPoints: {
              content: this.preparationForm.focusContent
            },
            role: this.getRoleText(this.preparationForm.role === 'other' ? 
                  this.preparationForm.otherRole : this.preparationForm.role),
            interviewGuide: this.interviewGuide || ''
          }
        })
        
        this.$message.success('保存成功')
        this.$router.push('/interview/schedule')
      } catch (error) {
        console.error('保存失败:', error)
        
        // 获取后端返回的具体错误信息
        const errorDetail = error.response?.data?.detail;
        
        // 根据错误类型提供不同的提示信息
        if (error.response && error.response.status === 403) {
          this.$message.error(errorDetail || '权限不足：您不是该面试的面试官，无法保存')
        } else if (error.response && error.response.status === 404) {
          this.$message.error(errorDetail || '保存失败：找不到相关记录')
        } else {
          this.$message.error('保存失败：' + (errorDetail || error.message || '未知错误'))
        }
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
    },
    getStatusText(status) {
      const statusMap = {
        scheduled: '待面试',
        in_progress: '进行中',
        completed: '已完成',
        cancelled: '已取消'
      }
      return statusMap[status] || '未知状态'
    },
    getStatusType(status) {
      const typeMap = {
        scheduled: 'warning',
        in_progress: 'primary',
        completed: 'success',
        cancelled: 'info'
      }
      return typeMap[status] || 'info'
    },
    clearFocusPoints() {
      this.preparationForm.focusContent = ''
    },
    addCategoryTag(tag) {
      // 获取光标位置
      const textarea = document.querySelector('textarea');
      const cursorPosition = textarea ? textarea.selectionStart : this.preparationForm.focusContent.length;
      
      // 在光标位置插入内容
      const beforeCursor = this.preparationForm.focusContent.substring(0, cursorPosition);
      const afterCursor = this.preparationForm.focusContent.substring(cursorPosition);
      
      this.preparationForm.focusContent = `${beforeCursor}${tag.content}${afterCursor}`;
      
      // 显示提示
      this.$message.success(`已添加"${tag.label}"`);
    },
    confirmClearFocus() {
      this.$confirm('确定要清空所有关注点内容吗?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.clearFocusPoints();
        this.$message({
          type: 'success',
          message: '内容已清空'
        });
      }).catch(() => {
        // 用户取消操作
      });
    },
    formatFocusContent() {
      const content = this.preparationForm.focusContent.trim();
      if (!content) {
        this.$message.warning('没有可格式化的内容');
        return;
      }
      
      // 分析内容，按行处理
      const lines = content.split('\n');
      const formattedLines = [];
      let inList = false;
      let listPrefix = '';
      let inHeading = false;
      
      // 确保第一行是标题
      if (!lines[0] || !lines[0].startsWith('#')) {
        formattedLines.push('# 面试关注点');
      }
      
      // 处理每一行
      for (let i = 0; i < lines.length; i++) {
        let line = lines[i].trim();
        
        // 空行处理
        if (!line) {
          if (inList) {
            inList = false;
            formattedLines.push('');
          } else if (i > 0 && formattedLines[formattedLines.length - 1] !== '') {
            formattedLines.push('');
          }
          continue;
        }
        
        // 标题处理
        if (line.startsWith('#')) {
          inHeading = true;
          inList = false;
          // 确保标题前有空行
          if (formattedLines.length > 0 && formattedLines[formattedLines.length - 1] !== '') {
            formattedLines.push('');
          }
          formattedLines.push(line);
          continue;
        }
        
        // 列表项处理
        if (/^\d+\./.test(line) || line.startsWith('-') || line.startsWith('*')) {
          const match = line.match(/^(\d+\.|-|\*)\s*/);
          if (match) {
            listPrefix = match[1];
            inList = true;
            formattedLines.push(line);
          }
          continue;
        }
        
        // 普通文本处理
        if (inList) {
          // 将普通文本转换为列表项
          if (listPrefix === '-' || listPrefix === '*') {
            formattedLines.push(`${listPrefix} ${line}`);
          } else {
            // 数字列表，寻找最后一个数字序号并加1
            const lastListItem = formattedLines[formattedLines.length - 1];
            const numMatch = lastListItem.match(/^(\d+)\./);
            if (numMatch) {
              const nextNum = parseInt(numMatch[1]) + 1;
              formattedLines.push(`${nextNum}. ${line}`);
            } else {
              formattedLines.push(`1. ${line}`);
            }
          }
        } else if (inHeading) {
          // 标题后的文本转为列表
          inHeading = false;
          formattedLines.push('');
          formattedLines.push(`1. ${line}`);
          inList = true;
          listPrefix = '1.';
        } else {
          // 普通段落
          formattedLines.push(line);
        }
      }
      
      // 更新内容
      this.preparationForm.focusContent = formattedLines.join('\n');
      this.$message.success('内容已格式化');
    },
    getRoleText(role) {
      const roleMap = {
        'technical': '技术面试官',
        'department_head': '部门负责人',
        'hr': '人事面试官'
      };
      return roleMap[role] || role; // 如果是other或未知角色，直接返回原值
    },
    
    // 检查指南显示状态
    checkGuideDisplay() {
      const guideContent = document.querySelector('.guide-content');
      const markdownContent = document.querySelector('.markdown-content');
      
      if (this.interviewGuide && (!guideContent || !markdownContent)) {
        this.forceUpdate();
      }
    },
    
    // 简化强制更新组件函数
    forceUpdate() {
      // 先设为false再设为true，强制触发视图更新
      this.forceShowGuide = false;
      setTimeout(() => {
        this.forceShowGuide = true;
      }, 100);
    },
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
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
  transition: all 0.3s ease;

  &:hover {
    box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.15);
  }
}

.interview-info-card {
  margin-bottom: 20px;
  border-radius: 8px;
  transition: all 0.3s ease;

  .interview-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;

    .interview-title {
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 16px;
      font-weight: 500;

      i {
        font-size: 20px;
        color: #409EFF;
      }

      .position-tag {
        margin-left: 10px;
        background-color: #e8f4ff;
        color: #409EFF;
      }

      .department-tag {
        background-color: #f0f9eb;
        color: #67c23a;
      }
    }

    .interview-status {
      display: flex;
      align-items: center;
      gap: 15px;

      .interview-id {
        color: #909399;
        font-size: 14px;
      }
    }
  }
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin: 20px 0;

  &.three-columns {
    grid-template-columns: repeat(3, 1fr);
  }

  .info-item {
    .info-label {
      display: flex;
      align-items: center;
      gap: 8px;
      color: #606266;
      margin-bottom: 8px;
      font-size: 14px;

      i {
        color: #409EFF;
      }
    }

    .info-value {
      color: #303133;
      font-size: 14px;
      line-height: 1.4;
    }

    .interviewer-list {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;

      .interviewer-tag {
        margin: 0;
      }
    }
  }
}

.preparation-form {
  margin-top: 30px;

  .preparation-card {
    margin-bottom: 20px;
    border-radius: 8px;
    transition: all 0.3s ease;

    &:hover {
      box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.1);
    }

    .el-card__header {
      padding: 15px 20px;
      border-bottom: 1px solid #ebeef5;
      
      i {
        margin-right: 8px;
        color: #409EFF;
      }
    }
  }
}

.interview-guide {
  .guide-actions {
    margin-bottom: 15px;
    text-align: right;
  }

  .guide-editor {
    margin-top: 15px;
  }

  .guide-content {
    padding: 20px;
    background-color: #fafafa;
    border-radius: 4px;
    line-height: 1.6;
    font-size: 14px;
  }
}

.empty-tip {
  padding: 40px 0;
  text-align: center;

  .empty-content {
    color: #909399;

    i {
      font-size: 48px;
      margin-bottom: 15px;
    }

    p {
      margin: 10px 0 0;
      font-size: 14px;
    }
    
    .empty-tip-sub {
      font-size: 12px;
      color: #C0C4CC;
      margin-top: 5px;
    }
  }
}

.form-actions {
  margin-top: 30px;
  text-align: center;
  padding: 20px 0;
  border-top: 1px solid #ebeef5;
}

// 动画效果
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter, .fade-leave-to {
  opacity: 0;
}

.slide-fade-enter-active {
  transition: all 0.3s ease;
}

.slide-fade-leave-active {
  transition: all 0.3s cubic-bezier(1.0, 0.5, 0.8, 1.0);
}

.slide-fade-enter, .slide-fade-leave-to {
  transform: translateY(10px);
  opacity: 0;
}

.guide-generating {
  background-color: #f9f9f9;
  border: 1px solid #e6f7ff;
  box-shadow: 0 0 5px rgba(24, 144, 255, 0.2);
}

.loading-guide {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #1890ff;
  padding: 30px 0;
}

.loading-guide i {
  font-size: 24px;
  margin-bottom: 10px;
}

.empty-guide {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #909399;
  padding: 30px 0;
}

.empty-guide i {
  font-size: 32px;
  margin-bottom: 15px;
}

.blinking-cursor {
  display: inline-block;
  animation: blink 1s step-end infinite;
  color: #1890ff;
  font-weight: bold;
}

@keyframes blink {
  from, to { opacity: 1; }
  50% { opacity: 0; }
}

.guide-content {
  padding: 20px;
  background-color: #fafafa;
  border-radius: 4px;
  line-height: 1.6;
  font-size: 14px;
}

.markdown-content {
  padding: 10px;
  line-height: 1.6;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

.markdown-content h1 {
  font-size: 24px;
  margin-top: 24px;
  margin-bottom: 16px;
  font-weight: 600;
  line-height: 1.25;
  border-bottom: 1px solid #eaecef;
  padding-bottom: 0.3em;
}

.markdown-content h2 {
  font-size: 20px;
  margin-top: 24px;
  margin-bottom: 16px;
  font-weight: 600;
  line-height: 1.25;
  border-bottom: 1px solid #eaecef;
  padding-bottom: 0.3em;
}

.markdown-content h3 {
  font-size: 18px;
  margin-top: 20px;
  margin-bottom: 12px;
  font-weight: 600;
  line-height: 1.25;
}

.markdown-content ul, .markdown-content ol {
  padding-left: 24px;
  margin-top: 8px;
  margin-bottom: 16px;
}

.markdown-content li {
  margin-bottom: 4px;
}

.markdown-content li>p {
  margin-top: 12px;
}

.markdown-content p {
  margin-top: 0;
  margin-bottom: 16px;
}

.markdown-content blockquote {
  padding: 0 1em;
  color: #6a737d;
  border-left: 0.25em solid #dfe2e5;
  margin: 0 0 16px 0;
}

.markdown-editor {
  font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
  line-height: 1.6;
  font-size: 14px;
}

.editor-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
  padding: 8px;
  background-color: #f8f9fa;
  border-radius: 4px;
  display: flex;
  align-items: center;
}

.editor-tip i {
  margin-right: 4px;
  color: #409EFF;
}

.focus-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
  padding: 10px;
  background-color: #f0f9ff;
  border-radius: 4px;
  border-left: 3px solid #409EFF;
  display: flex;
  align-items: flex-start;
}

.focus-tip i {
  margin-right: 6px;
  margin-top: 2px;
  color: #409EFF;
}

.template-selector {
  margin-bottom: 15px;
  padding: 10px;
  background-color: #f8f9fa;
  border-radius: 4px;
  display: flex;
  align-items: center;
  
  .template-label {
    margin-right: 10px;
    color: #606266;
    font-size: 14px;
    font-weight: 500;
  }
}

.quick-tags {
  margin-bottom: 12px;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  
  .quick-tags-label {
    margin-right: 10px;
    color: #606266;
    font-size: 14px;
  }
  
  .quick-tag {
    margin-right: 8px;
    margin-bottom: 6px;
    cursor: pointer;
    transition: all 0.2s;
    background-color: #f0f9ff;
    color: #409EFF;
    border-color: #d9ecff;
    
    &:hover {
      background-color: #409EFF;
      color: #fff;
    }
  }
}

.preview-toggle {
  margin-top: 10px;
  text-align: right;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  
  .el-switch {
    margin-left: 8px;
  }
}

.focus-actions {
  margin-top: 10px;
  margin-bottom: 10px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.focus-preview {
  margin-top: 15px;
  padding: 15px;
  background-color: #fff;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.03);

  .preview-header {
    margin-bottom: 15px;
    padding-bottom: 10px;
    border-bottom: 1px solid #ebeef5;
    font-weight: 500;
    color: #409EFF;
    display: flex;
    align-items: center;
    
    i {
      margin-right: 5px;
    }
  }

  .preview-content {
    line-height: 1.6;
    font-size: 14px;
    min-height: 100px;
  }
}

.empty-preview {
  text-align: center;
  color: #909399;
  padding: 30px 0;
}

.category-selector {
  margin-bottom: 15px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  overflow: hidden;
  
  .el-tabs__header {
    margin-bottom: 0;
  }
  
  .el-tabs__content {
    padding: 15px;
    background-color: #f8f9fa;
  }
}

.category-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding: 5px 0;
}

.category-tag {
  cursor: pointer;
  transition: all 0.2s;
  background-color: #f0f9ff;
  color: #409EFF;
  border-color: #d9ecff;
  padding: 4px 8px;
  border-radius: 4px;
  
  &:hover {
    background-color: #409EFF;
    color: #fff;
  }
}

.role-tag {
  margin-left: 10px;
  font-size: 13px;
}
</style> 