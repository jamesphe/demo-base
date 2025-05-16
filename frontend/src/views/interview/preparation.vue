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
                <div class="role-tabs">
                  <el-radio-group v-model="preparationForm.role" size="medium">
                    <el-radio-button label="department_head">
                      <i class="el-icon-s-custom"></i> 部门负责人
                    </el-radio-button>
                    <el-radio-button label="technical">
                      <i class="el-icon-s-tools"></i> 技术面试官
                    </el-radio-button>
                    <el-radio-button label="business">
                      <i class="el-icon-s-marketing"></i> 业务面试官
                    </el-radio-button>
                    <el-radio-button label="hr">
                      <i class="el-icon-user-solid"></i> 人事面试官
                    </el-radio-button>
                    <el-radio-button label="behavior">
                      <i class="el-icon-s-opportunity"></i> 行为面试官
                    </el-radio-button>
                    <el-radio-button label="culture">
                      <i class="el-icon-s-cooperation"></i> 文化面试官
                    </el-radio-button>
                    <el-radio-button label="other">
                      <i class="el-icon-more"></i> 其他
                    </el-radio-button>
                  </el-radio-group>
                </div>
                
                <el-input 
                  v-if="preparationForm.role === 'other'" 
                  v-model="preparationForm.otherRole" 
                  placeholder="请输入您的角色" 
                  style="width: 200px; margin-top: 10px;"
                />
                
                <!-- 新增行业选择 -->
                <div class="industry-selector">
                  <span class="industry-label">行业领域：</span>
                  <el-select v-model="preparationForm.industry" placeholder="选择行业领域" @change="handleIndustryChange" size="small">
                    <el-option
                      v-for="item in industryOptions"
                      :key="item.value"
                      :label="item.label"
                      :value="item.value">
                      <span style="float: left;"><i :class="item.icon"></i> {{ item.label }}</span>
                    </el-option>
                  </el-select>
                  <el-tooltip content="选择行业可获得更针对性的面试指导" placement="top" effect="light">
                    <i class="el-icon-question industry-help"></i>
                  </el-tooltip>
                </div>
                
                <div class="role-card" v-if="preparationForm.role !== 'other' || preparationForm.otherRole">
                  <div class="role-card-header">
                    <el-tag 
                      class="role-tag" 
                      :type="getRoleTagType(preparationForm.role)"
                      effect="dark">
                      <i :class="getRoleIcon(preparationForm.role)"></i>
                      {{ preparationForm.role === 'other' ? preparationForm.otherRole : getRoleText(preparationForm.role) }}
                    </el-tag>
                    <el-tag 
                      v-if="preparationForm.industry" 
                      class="industry-tag" 
                      type="info" 
                      effect="plain">
                      <i :class="getIndustryIcon(preparationForm.industry)"></i>
                      {{ getIndustryText(preparationForm.industry) }}
                    </el-tag>
                  </div>
                  <div class="role-card-body" v-if="preparationForm.role !== 'other'">
                    <div class="role-description">
                      <i class="el-icon-info-circle"></i>
                      <span>{{ getRoleDescription(preparationForm.role) }}</span>
                    </div>
                    <div class="role-focus-points">
                      <div class="focus-point-title">主要关注点：</div>
                      <div class="focus-point-list">
                        <div v-for="(point, index) in getRoleFocusPoints(preparationForm.role)" :key="index" class="focus-point-item">
                          <i class="el-icon-check"></i>
                          <span>{{ point }}</span>
                        </div>
                      </div>
                    </div>
                    <div class="industry-tips" v-if="preparationForm.industry">
                      <div class="industry-tips-title"><i class="el-icon-info-circle"></i> {{ getIndustryText(preparationForm.industry) }}行业面试特点：</div>
                      <ul class="industry-tips-list">
                        <li v-for="(tip, index) in getIndustryTips(preparationForm.industry, preparationForm.role)" :key="index">
                          {{ tip }}
                        </li>
                      </ul>
                    </div>
                  </div>
                </div>
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
                <div class="focus-controls">
                  <el-button 
                    type="primary" 
                    icon="el-icon-magic-stick"
                    @click="generateIndustryRoleFocusPoints(preparationForm.industry, preparationForm.role)"
                    :disabled="!preparationForm.role"
                    :loading="generatingFocus">
                    生成面试关注点
                  </el-button>
                  <el-tooltip content="根据您选择的角色和行业自动生成面试关注点内容" placement="top">
                    <i class="el-icon-question help-icon"></i>
                  </el-tooltip>
                </div>
                
                <el-input
                  type="textarea"
                  :rows="12"
                  placeholder="请输入面试关注点内容，或点击上方按钮自动生成..."
                  v-model="preparationForm.focusContent"
                  class="focus-editor"
                />
                
                <div class="focus-tip">
                  <i class="el-icon-info"></i>
                  <span>提示：系统会根据您选择的角色({{ getRoleText(preparationForm.role) }})和行业({{ getIndustryText(preparationForm.industry) || '通用' }})自动生成内容</span>
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
                    icon="el-icon-view"
                    @click="showPreview = !showPreview">
                    {{ showPreview ? '关闭预览' : '预览效果' }}
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
        industry: '',
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
          technical: '## 技术评估要点\n1. 技术深度考察方法\n2. 编码能力测试设计\n3. 系统设计问题准备\n4. 算法能力评估标准\n5. 技术广度探索方式\n\n## 面试技巧\n1. 如何引导候选人深入思考\n2. 技术难题的层层递进\n3. 判断技术潜力的指标\n4. 识别简历技术夸大的方法\n5. 技术岗位特定问题库\n\n## 评分标准\n1. 技术问题评分量表\n2. 编码质量评判依据\n3. 技术交流表达能力标准\n4. 学习能力评估方法\n5. 技术创新思维判断',
          comprehensive: '技术评估策略、编码能力测试、学习能力判断、技术潜力识别、专业能力衡量标准'
        },
        department_head: {
          technical: '## 部门需求对接\n1. 部门现状和人才缺口分析\n2. 团队成员能力互补性考察\n3. 业务理解力评估方法\n4. 候选人职业发展与部门规划契合度\n5. 跨团队协作能力识别\n\n## 管理潜质评估\n1. 如何识别领导潜质\n2. 问题解决的思路评估\n3. 资源分配意识考察\n4. 人际关系处理能力判断\n5. 管理经验相关提问设计\n\n## 面试策略\n1. 部门情况介绍要点\n2. 岗位职责精准传达\n3. 部门发展愿景分享\n4. 管理风格匹配度评估\n5. 入职后发展路径描述',
          comprehensive: '部门需求分析、团队契合度评估、管理潜质识别、业务理解力测试、团队融入度判断'
        },
        hr: {
          technical: '## HR面试准备\n1. 简历深度挖掘技巧\n2. 结构化面试问题设计\n3. 薪资福利政策准备\n4. 公司文化核心要点\n5. 入职流程及周期说明\n\n## 软技能评估\n1. 沟通能力考察方法\n2. 团队合作精神识别\n3. 职业稳定性判断\n4. 学习成长意愿测试\n5. 抗压能力评估技巧\n\n## 面试技巧\n1. 面试气氛营造方法\n2. 敏感问题处理策略\n3. 薪资期望探讨技巧\n4. 候选人疑虑解答准备\n5. 面试结果客观记录方法',
          comprehensive: 'HR面试准备、软技能评估方法、薪资谈判技巧、公司文化传达、候选人疑虑解答'
        },
        behavior: {
          technical: '## 行为面试框架\n1. STAR法则应用指南\n2. 结构化问题设计方法\n3. 过往经验提问策略\n4. 情景假设题目准备\n5. 行为模式识别技巧\n\n## 关键行为评估\n1. 责任心评判标准\n2. 团队合作行为识别\n3. 问题解决模式分析\n4. 沟通效果评估方法\n5. 主动性与创新性考察\n\n## 面试技巧\n1. 避免诱导性提问\n2. 深入追问的时机把握\n3. 行为不一致性识别\n4. 面试偏见预防方法\n5. 客观记录与评分标准',
          comprehensive: '行为面试框架、STAR法则应用、行为模式识别、客观评分标准、面试偏见预防'
        },
        culture: {
          technical: '## 文化面试准备\n1. 公司核心价值观解读\n2. 团队文化特性说明\n3. 企业发展历程介绍\n4. 工作方式与习惯说明\n5. 企业使命愿景传达\n\n## 文化匹配评估\n1. 价值观一致性测试\n2. 工作风格适应性判断\n3. 团队融入度预测\n4. 长期发展意愿考察\n5. 企业认同感评估\n\n## 面试策略\n1. 公司文化生动呈现\n2. 真实工作环境描述\n3. 团队成员风格说明\n4. 文化冲突案例分享\n5. 候选人顾虑解答准备',
          comprehensive: '文化面试准备、企业价值观解读、文化匹配度评估、工作环境介绍、企业认同感测试'
        },
        business: {
          technical: '## 业务能力评估\n1. 业务领域专业知识考察\n2. 行业经验深度评估\n3. 业务问题分析能力测试\n4. 业务创新思维考察\n5. 业务敏感度判断方法\n\n## 实战案例设计\n1. 行业案例分析题准备\n2. 业务决策能力测试\n3. 市场洞察力评估问题\n4. 商业模式理解考察\n5. 竞争策略分析能力测试\n\n## 面试策略\n1. 行业趋势讨论引导\n2. 业务术语应用观察\n3. 专业深度层层递进\n4. 跨部门业务理解测试\n5. 业务价值判断能力评估',
          comprehensive: '业务专业知识、行业经验评估、案例分析能力、商业决策思维、业务创新意识考察'
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
      lastAddedTag: '',
      lastAddedCategoryTag: '',
      industryOptions: [
        { value: '', label: '通用 (不限行业)', icon: 'el-icon-office-building' },
        { value: 'it', label: 'IT/互联网/软件', icon: 'el-icon-monitor' },
        { value: 'finance', label: '金融/银行/保险', icon: 'el-icon-money' },
        { value: 'healthcare', label: '医疗/制药/生物', icon: 'el-icon-first-aid-kit' },
        { value: 'manufacturing', label: '制造/工程/能源', icon: 'el-icon-cpu' },
        { value: 'education', label: '教育/培训/科研', icon: 'el-icon-reading' },
        { value: 'retail', label: '零售/消费品/电商', icon: 'el-icon-shopping-cart-full' },
        { value: 'media', label: '媒体/广告/设计', icon: 'el-icon-picture' },
        { value: 'government', label: '政府/公共事业', icon: 'el-icon-school' },
        { value: 'consulting', label: '咨询/专业服务', icon: 'el-icon-service' }
      ],
      generatingFocus: false,
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
    
    // 根据行业代码获取行业名称
    getIndustryText() {
      return (industry) => {
        const industryMap = {
          'it': '信息技术',
          'finance': '金融',
          'healthcare': '医疗健康',
          'manufacturing': '制造业',
          'education': '教育',
          'retail': '零售',
          'media': '媒体',
          'government': '政府',
          'consulting': '咨询'
        };
        return industryMap[industry] || '未知行业';
      };
    },
    
    // 根据角色代码获取角色名称
    getRoleText() {
      return (role) => {
        const roleMap = {
          'technical': '技术面试官',
          'department_head': '部门主管',
          'hr': '人事面试官',
          'behavior': '行为面试官',
          'culture': '文化面试官',
          'business': '业务面试官',
          'other': '其他角色'
        };
        return roleMap[role] || '未知角色';
      };
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
        this.preparationForm.focusContent = '# 面试关注点\n\n## 面试准备\n1. 候选人简历重点分析\n2. 岗位关键要求梳理\n3. 面试流程与时间规划\n\n## 评估标准\n1. 专业能力评估方法\n2. 通用素质判断标准\n3. 团队匹配度考量因素\n\n## 面试技巧\n1. 有效提问方式\n2. 积极倾听的方法\n3. 候选人潜力发掘技巧\n4. 面试记录与评分标准';
        return;
      }
      
      if (templateKey === 'behavior') {
        this.preparationForm.focusContent = '# 行为面试官指南\n\n## 面试准备\n1. 结构化问题设计\n2. STAR法则应用策略\n3. 行为评估维度确定\n\n## 提问技巧\n1. 开放性问题设计方法\n2. 深入追问的时机把握\n3. 情景模拟问题准备\n\n## 行为分析\n1. 过往行为模式识别\n2. 一致性与真实性判断\n3. 行为背后动机分析\n\n## 评分标准\n1. 客观评分量表设计\n2. 行为表现等级划分\n3. 面试记录规范化方法';
        return;
      }
      
      if (templateKey === 'culture') {
        this.preparationForm.focusContent = '# 文化面试官指南\n\n## 企业文化准备\n1. 核心价值观梳理\n2. 企业文化特色提炼\n3. 团队工作方式总结\n\n## 面试策略\n1. 文化价值观阐述方法\n2. 企业使命愿景传达\n3. 团队氛围真实呈现\n\n## 匹配度评估\n1. 价值观契合度问题设计\n2. 工作方式适应性评估\n3. 文化认同感测试方法\n\n## 决策依据\n1. 文化匹配评分标准\n2. 潜在文化冲突识别\n3. 长期融入度预测方法';
        return;
      }
      
      const defaultPoints = this.defaultFocusPoints[templateKey];
      if (defaultPoints) {
        this.preparationForm.focusContent = defaultPoints.technical;
      }
    },
    
    addQuickTag(content, label) {
      // 如果当前没有内容或内容为空，则先添加标题
      if (!this.preparationForm.focusContent || this.preparationForm.focusContent.trim() === '') {
        this.preparationForm.focusContent = '# 面试关注点';
      }
      
      // 添加快速标签内容
      this.preparationForm.focusContent += content;
      
      // 记录最后添加的标签
      this.lastAddedTag = label;
      
      // 显示提示
      this.$message.success('已添加关注点');
      
      // 短暂延时后恢复高亮
      setTimeout(() => {
        this.lastAddedTag = '';
      }, 2000);
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
          },
          industry: this.preparationForm.industry ? this.getIndustryText(this.preparationForm.industry) : '通用'
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
      
      // 记录最后添加的分类标签
      this.lastAddedCategoryTag = tag.label;
      
      // 显示提示
      this.$message.success(`已添加"${tag.label}"`);
      
      // 短暂延时后恢复高亮
      setTimeout(() => {
        this.lastAddedCategoryTag = '';
      }, 2000);
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
      
      // 添加动画效果
      this.$nextTick(() => {
        const editor = document.querySelector('.focus-editor');
        if (editor) {
          editor.classList.add('highlight-animate');
          setTimeout(() => {
            editor.classList.remove('highlight-animate');
          }, 2000);
        }
      });
    },
    getRoleText(role) {
      const roleMap = {
        'technical': '技术面试官',
        'department_head': '部门负责人',
        'hr': '人事面试官',
        'behavior': '行为面试官',
        'culture': '文化面试官',
        'business': '业务面试官'
      };
      return roleMap[role] || role; // 如果是other或未知角色，直接返回原值
    },
    
    getRoleIcon(role) {
      const iconMap = {
        'technical': 'el-icon-s-tools',
        'department_head': 'el-icon-s-custom',
        'hr': 'el-icon-user-solid',
        'behavior': 'el-icon-s-opportunity',
        'culture': 'el-icon-s-cooperation',
        'business': 'el-icon-s-marketing',
        'other': 'el-icon-more'
      };
      return iconMap[role] || 'el-icon-user';
    },
    
    getRoleTagType(role) {
      const typeMap = {
        'technical': 'primary',
        'department_head': 'success',
        'hr': 'warning',
        'behavior': 'info',
        'culture': 'danger',
        'business': 'success',
        'other': 'info'
      };
      return typeMap[role] || 'info';
    },
    
    getRoleDescription(role) {
      const descMap = {
        'technical': '负责评估候选人技术能力的面试官，通常由有经验的技术专家担任，重点关注专业技能评估',
        'department_head': '由部门主管或团队负责人担任，主要考察候选人与团队和业务的匹配度，关注管理潜力',
        'hr': '由人力资源部门专员担任，负责考察候选人的综合素质、职业规划和薪资期望等方面',
        'behavior': '专注于考察候选人行为模式的面试官，通过结构化问题评估其过往行为表现',
        'culture': '由公司文化推广者或资深员工担任，负责评估候选人与公司价值观和文化的契合度',
        'business': '由业务部门骨干担任，主要负责评估候选人对业务领域的理解和专业知识，关注业务能力和行业经验'
      };
      return descMap[role] || '';
    },
    
    getRoleFocusPoints(role) {
      const focusPointsMap = {
        'technical': [
          '如何设计有针对性的技术问题',
          '如何评估编码能力和技术深度',
          '如何判断技术方案的优劣',
          '技术面试常见陷阱及避免方法',
          '如何识别技术人才的成长潜力'
        ],
        'department_head': [
          '如何结合部门实际需求设计问题',
          '如何评估候选人的管理潜质',
          '团队融入度的考察方法',
          '业务理解能力的评估技巧',
          '如何判断候选人的长期发展契合度'
        ],
        'hr': [
          '如何设计行为面试问题',
          '薪资谈判的技巧和策略',
          '如何进行职业发展规划讨论',
          '软技能评估的方法和标准',
          '企业文化宣讲的要点'
        ],
        'behavior': [
          'STAR法则的应用技巧',
          '如何设计情景类问题',
          '行为模式分析的方法',
          '压力测试的适当方式',
          '如何避免面试偏见'
        ],
        'culture': [
          '公司价值观的有效传达',
          '如何设计文化匹配度问题',
          '团队文化介绍的核心要点',
          '价值观冲突的识别方法',
          '如何评估候选人的文化适应性'
        ],
        'business': [
          '业务领域专业知识的评估方法',
          '如何设计案例分析题目',
          '行业经验和洞察力的考察技巧',
          '业务敏感度的测试方式',
          '商业思维和决策能力的评估'
        ]
      };
      return focusPointsMap[role] || [];
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
    getIndustryText(industry) {
      const industryMap = {
        'it': 'IT/互联网',
        'finance': '金融/银行',
        'healthcare': '医疗/制药',
        'manufacturing': '制造/工程',
        'education': '教育/培训',
        'retail': '零售/消费品',
        'media': '媒体/设计',
        'government': '政府/公共事业',
        'consulting': '咨询/专业服务'
      };
      return industryMap[industry] || '通用';
    },
    
    getIndustryIcon(industry) {
      const iconMap = {
        'it': 'el-icon-monitor',
        'finance': 'el-icon-money',
        'healthcare': 'el-icon-first-aid-kit',
        'manufacturing': 'el-icon-cpu',
        'education': 'el-icon-reading',
        'retail': 'el-icon-shopping-cart-full',
        'media': 'el-icon-picture',
        'government': 'el-icon-school',
        'consulting': 'el-icon-service'
      };
      return iconMap[industry] || 'el-icon-office-building';
    },
    
    getIndustryTips(industry, role) {
      // 根据行业和角色组合返回针对性的面试提示
      const tips = {
        it: {
          technical: [
            '关注候选人的编码实践和系统设计能力',
            '考察算法理解和问题解决思路',
            '评估新技术学习能力和技术视野',
            '关注代码质量和工程实践'
          ],
          department_head: [
            '关注技术管理经验和跨团队协作能力',
            '评估技术决策和架构规划能力',
            '考察敏捷/项目管理方法论应用',
            '了解对技术趋势的把握程度'
          ],
          hr: [
            '了解IT人才市场动态和薪资水平',
            '关注技术人才成长路径和职业规划',
            '评估加班文化接受度和工作节奏',
            '考察远程工作和弹性工作制的适应性'
          ],
          behavior: [
            '关注高压环境下的工作表现',
            '了解跨部门沟通和团队协作能力',
            '考察学习主动性和技术攻坚意愿',
            '评估创新思维和解决方案多样性'
          ],
          culture: [
            '了解对技术创新文化的理解',
            '评估扁平化组织结构的适应能力',
            '考察开源精神和知识分享意愿',
            '关注技术伦理观和数据安全意识'
          ]
        },
        finance: {
          technical: [
            '关注金融领域相关技术和合规知识',
            '评估数据安全意识和风险控制能力',
            '考察高并发和高可用系统经验',
            '了解金融科技趋势的理解'
          ],
          department_head: [
            '关注风险管理和合规意识',
            '评估在监管环境下的决策能力',
            '考察金融业务流程优化经验',
            '了解对金融安全和稳定性的重视程度'
          ],
          hr: [
            '了解金融行业人才特点和激励机制',
            '关注职业资格证书和专业背景',
            '评估对金融行业工作强度的适应能力',
            '考察稳定性和保密意识'
          ],
          behavior: [
            '关注严谨性和细节关注度',
            '评估在高压环境下的表现',
            '考察对监管合规的态度',
            '了解职业操守和道德准则认知'
          ],
          culture: [
            '了解对金融行业企业文化的认识',
            '评估对风险控制文化的接受度',
            '考察对服务精神和专业性的重视',
            '关注稳健性和可靠性价值观'
          ]
        },
        healthcare: {
          technical: [
            '关注医疗健康相关知识和法规了解',
            '评估数据隐私保护和患者信息安全意识',
            '考察医疗信息系统和健康科技经验',
            '了解对医疗行业特殊需求的理解'
          ],
          department_head: [
            '关注医疗质量管理和患者安全意识',
            '评估跨专业团队管理能力',
            '考察医疗行业合规和认证经验',
            '了解对医疗服务改进的思路'
          ],
          hr: [
            '了解医疗人才特点和专业资质要求',
            '关注医疗行业工作强度和倒班适应性',
            '评估对医患关系和医疗伦理的理解',
            '考察专业发展规划和继续教育意愿'
          ],
          behavior: [
            '关注同理心和沟通能力',
            '评估在危急情况下的决策能力',
            '考察团队协作和跨专业合作能力',
            '了解压力管理和情绪调节能力'
          ],
          culture: [
            '了解对医疗使命和价值观的认同',
            '评估对患者至上理念的接受度',
            '考察对医疗质量和安全文化的重视',
            '关注对生命科学伦理的理解'
          ]
        },
        // 为其他行业添加更多提示...
        manufacturing: {
          technical: [
            '关注制造工艺和质量控制知识',
            '评估工业自动化和智能制造认知',
            '考察生产系统优化和效率提升经验',
            '了解对材料科学和工程标准的理解'
          ],
          department_head: [
            '关注生产管理和供应链优化经验',
            '评估质量控制体系和精益生产理念',
            '考察资源调配和产能规划能力',
            '了解对安全生产和环保要求的重视'
          ],
          hr: [
            '了解制造业人才特点和技能要求',
            '关注工厂环境和班次工作适应性',
            '评估对劳动法规和安全培训的理解',
            '考察技术工人培养和技能提升思路'
          ],
          behavior: [
            '关注执行力和操作规范遵守性',
            '评估问题解决和持续改进意识',
            '考察团队协作和跨部门沟通能力',
            '了解对质量和效率平衡的处理'
          ],
          culture: [
            '了解对工匠精神和精益理念的认同',
            '评估对安全文化和质量意识的重视',
            '考察对持续改进和创新的态度',
            '关注对企业社会责任的理解'
          ]
        }
      };
      
      // 默认通用提示
      const defaultTips = [
        '结合行业特点设计面试问题',
        '关注候选人对行业趋势的理解',
        '评估行业专业知识和经验深度',
        '考察行业特定软技能和职业素养'
      ];
      
      // 如果有特定行业和角色的提示，返回对应提示，否则返回通用提示
      return (tips[industry] && tips[industry][role]) ? tips[industry][role] : defaultTips;
    },
    
    handleIndustryChange(value) {
      // 当行业变化时，可以根据行业自动调整面试关注点内容
      if (value && this.preparationForm.role) {
        // 显示消息
        this.$message.success(`已选择${this.getIndustryText(value)}行业，面试指导将更有针对性`);
        
        // 询问用户是否要生成行业特定的面试关注点
        this.$confirm(`是否要生成针对${this.getIndustryText(value)}行业的面试关注点?`, '提示', {
          confirmButtonText: '生成',
          cancelButtonText: '暂不生成',
          type: 'info'
        }).then(() => {
          // 用户确认后，生成行业和角色相关的关注点
          this.generateIndustryRoleFocusPoints(value, this.preparationForm.role);
        }).catch(() => {
          // 用户取消，不做任何操作
        });
      }
    },

    // 添加一个新方法用于生成行业和角色相关的面试关注点
    generateIndustryRoleFocusPoints(industry, role) {
      // 设置加载状态
      this.generatingFocus = true;
      
      // 获取行业文本和角色文本
      const industryText = this.getIndustryText(industry);
      const roleText = this.getRoleText(role);
      
      // 根据行业和角色组合获取对应的面试关注点模板
      const focusPointsTemplate = this.getIndustryRoleFocusPoints(industry, role);
      
      // 内容标题
      const title = `# ${industryText || '通用'}行业${roleText}面试关注点`;
      
      // 设置内容
      this.preparationForm.focusContent = title + '\n\n' + focusPointsTemplate;
      
      // 关闭加载状态
      setTimeout(() => {
        this.generatingFocus = false;
        
        // 添加动画效果
        this.$nextTick(() => {
          const editor = document.querySelector('.focus-editor');
          if (editor) {
            editor.classList.add('highlight-animate');
            setTimeout(() => {
              editor.classList.remove('highlight-animate');
            }, 2000);
          }
        });
        
        // 显示成功消息
        this.$message.success(`已生成${industryText || '通用'}行业${roleText}的面试关注点`);
      }, 500);
    },

    // 添加一个新方法用于获取行业和角色组合的面试关注点模板
    getIndustryRoleFocusPoints(industry, role) {
      // 定义行业和角色组合的关注点模板
      const templates = {
        it: {
          technical: `## 技术深度评估
1. 如何评估候选人在核心技术领域的掌握程度
2. 设计编码测试来验证实际动手能力
3. 提问系统设计问题的技巧和注意事项
4. 技术问题的递进深入方法

## IT行业特定技能考察
1. 云服务和分布式系统知识评估方法
2. 开源贡献和技术社区参与度考察
3. 代码质量和工程实践评估标准
4. 敏捷开发和DevOps理念理解检验

## 技术学习能力评估
1. 新技术学习速度和深度的判断方法
2. 技术视野和知识广度的提问技巧
3. 自驱学习意愿和能力的识别方式
4. 技术潜力评估的重点关注点`,
          
          department_head: `## 技术团队管理能力
1. 技术团队建设和人才培养经验考察
2. 跨团队协作和资源协调能力评估
3. 技术战略规划和落地执行能力判断
4. 技术债务管理和系统演进观念评估

## IT项目管理能力
1. 敏捷方法论实践经验和理解深度
2. 技术风险预判和解决能力评估
3. 项目范围和进度控制能力考察
4. 技术与业务需求平衡能力判断

## 技术决策能力
1. 架构选型和技术决策过程考察
2. 技术创新与稳定性平衡判断
3. 成本效益分析能力评估
4. 技术团队激励和绩效管理方法`,
          
          hr: `## IT人才特点理解
1. 技术人才特性和心理特点把握
2. IT行业薪资结构和福利体系设计
3. 技术人才成长路径和职业规划引导
4. 工作模式和弹性工作制度设计理念

## 技术招聘策略
1. IT人才市场动态和招聘渠道把握
2. 技术人才筛选要点和简历识别技巧
3. 技术面试官团队的组织和培训方法
4. 候选人技术背景基础判断要点

## 文化契合度评估
1. 技术团队文化特点和价值观考察
2. 远程工作和协作能力评估方法
3. 技术驱动型企业的文化适应性判断
4. 创新意识和持续学习态度评估`,
          business: `## IT业务领域知识
1. 产品和服务生命周期理解考察
2. 业务模式和运营策略评估
3. 用户需求分析和产品定位能力
4. IT解决方案商业价值判断能力

## 行业洞察力评估
1. IT行业趋势理解和判断能力
2. 竞争格局分析和市场定位思维
3. 数字化转型和创新模式认知
4. 用户体验和产品思维评估

## 业务决策能力
1. 产品和项目优先级决策能力
2. 业务风险评估和处理方法
3. 数据驱动决策思维考察
4. ROI分析和商业价值判断`
        },
        
        finance: {
          technical: `## 金融科技能力评估
1. 金融领域技术应用知识考察方法
2. 金融数据处理和分析能力评估
3. 风控系统和反欺诈技术经验考量
4. 支付系统和交易处理技术理解

## 金融行业合规意识
1. 金融数据安全和隐私保护意识评估
2. 合规监管技术实现经验考察
3. 金融系统稳定性和可靠性保障能力
4. 金融科技创新与合规平衡理解

## 高性能系统经验
1. 高并发交易系统设计经验考察
2. 金融级容灾和高可用设计能力
3. 实时风控和异常监测系统经验
4. 金融科技趋势和前沿技术理解`,
          
          department_head: `## 金融业务理解
1. 金融业务流程和产品知识考察
2. 业务与技术衔接能力评估方法
3. 金融行业发展趋势把握程度判断
4. 金融创新与风险控制平衡理解

## 合规与风控管理
1. 金融监管政策理解和执行能力
2. 风险管理体系构建和优化经验
3. 合规文化建设和团队意识培养
4. 金融安全和数据保护管理能力

## 金融团队管理
1. 金融专业团队的协调与管理技巧
2. 绩效考核和激励机制设计经验
3. 跨部门协作和资源整合能力
4. 危机处理和应急响应领导力`,
          business: `## 金融业务知识
1. 金融产品和服务理解深度
2. 金融业务流程和规则认知
3. 风险评估和控制意识考察
4. 金融监管政策理解和应用能力

## 金融市场洞察
1. 金融市场趋势判断能力
2. 金融创新模式和产品理解
3. 竞争对手分析和差异化思维
4. 客户需求洞察和服务设计能力

## 金融业务决策
1. 风险与收益平衡能力评估
2. 金融指标分析和解读能力
3. 合规与业务发展平衡思维
4. 金融业务战略规划能力`
        },
        
        healthcare: {
          technical: `## 医疗信息系统能力
1. 医疗数据标准和互操作性理解
2. 临床信息系统开发经验考察
3. 医疗数据安全和隐私保护意识
4. 医疗影像处理和AI应用能力评估

## 医疗行业合规性
1. 医疗数据合规和伦理意识评估
2. 医疗系统认证和标准符合性理解
3. 患者数据管理和使用规范认知
4. 医疗软件监管要求和验证流程

## 专业领域知识
1. 医疗术语和临床流程理解程度
2. 医疗健康产品用户体验设计能力
3. 医疗设备集成和互联互通技术
4. 健康管理和远程医疗技术应用`,
          business: `## 医疗业务领域知识
1. 医疗服务流程和专业术语理解
2. 医疗产品和解决方案知识考察
3. 医患关系管理和服务意识评估
4. 医疗质量管理和风险控制能力

## 医疗行业洞察
1. 医疗健康行业趋势判断能力
2. 医疗政策和法规应用理解
3. 医疗服务创新模式认知程度
4. 健康管理理念和实践经验考察

## 医疗业务决策
1. 医疗资源配置和优化能力
2. 医疗服务价值和效益分析能力
3. 医疗业务伦理和合规决策思维
4. 医疗健康项目规划和管理能力`
        },
        
        manufacturing: {
          technical: `## 工业技术能力
1. 制造业自动化和信息化技术评估
2. 工业物联网和数字孪生技术理解
3. 生产管理系统设计和优化经验
4. 供应链系统和ERP集成技术能力

## 制造业专业知识
1. 工艺流程和生产线设计理解
2. 质量控制系统和标准执行能力
3. 精益生产和持续改进工具应用
4. 工业安全和环保技术要求认知

## 行业解决方案能力
1. 制造业痛点识别和解决方案设计
2. 工业设备监控和预测性维护技术
3. 生产效率优化和成本控制方法
4. 智能制造趋势和技术路线图规划`,
          business: `## 制造业务知识
1. 制造流程和产业链理解深度
2. 产品质量标准和控制方法认知
3. 生产计划和库存管理能力考察
4. 供应链管理和采购策略理解

## 制造行业洞察
1. 制造业趋势和技术变革认知
2. 产品生命周期管理思维评估
3. 制造业成本结构和效益分析能力
4. 产能规划和资源配置逻辑理解

## 制造业务决策
1. 生产效率和质量平衡决策能力
2. 设备投资和技术升级评估能力
3. 精益生产和持续改进思维考察
4. 产品创新和市场定位能力评估`
        },
        
        education: {
          technical: `## 教育技术能力
1. 教育平台设计和用户体验评估
2. 学习数据分析和个性化算法设计
3. 教育资源管理和内容分发系统
4. 在线学习和互动技术应用能力

## 教育专业理解
1. 教学流程和学习方法论理解
2. 教育评估系统和效果测量设计
3. 学习行为分析和干预机制设计
4. 教育游戏化和激励系统设计能力

## 教育行业趋势
1. 教育科技发展趋势和创新方向
2. 混合式学习技术和应用场景
3. 人工智能在教育中的应用前景
4. 教育数据安全和隐私保护措施`,
          business: `## 教育业务知识
1. 教育产品和服务设计理解
2. 学习需求分析和教学设计能力
3. 教育质量评估和效果测量方法
4. 教育市场细分和目标用户定位能力

## 教育行业洞察
1. 教育行业发展趋势判断能力
2. 教育理念和方法论应用能力
3. 教育科技和创新模式认知程度
4. 学习者体验和参与度设计思维

## 教育业务决策
1. 教育资源配置和课程规划能力
2. 教育品质与规模平衡决策思维
3. 教育效果评估和优化能力
4. 教育服务定价和价值传递能力`
        }
      };
      
      // 通用模板，当没有特定行业+角色组合的模板时使用
      const defaultTemplate = `## ${this.getIndustryText(industry)}行业面试要点
1. ${this.getIndustryText(industry)}行业知识和专业术语理解
2. ${this.getIndustryText(industry)}行业趋势和发展方向把握
3. ${this.getIndustryText(industry)}行业特定技能和经验评估
4. ${this.getIndustryText(industry)}行业法规和标准认知考察

## ${this.getRoleText(role)}角色职责
1. ${this.getRoleText(role)}在面试过程中的主要职责
2. ${this.getRoleText(role)}评估候选人的关键维度
3. ${this.getRoleText(role)}常用面试技巧和问题设计
4. ${this.getRoleText(role)}评分标准和决策依据

## 综合能力评估
1. 专业知识与行业经验相结合评估
2. 沟通表达与专业深度平衡考察
3. 学习能力与行业适应性判断方法
4. 团队协作与专业独立性平衡评估`;
      
      // 返回对应的模板，如果没有特定的模板，则返回通用模板
      return (templates[industry] && templates[industry][role]) ? 
        templates[industry][role] : defaultTemplate;
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
  
  .template-help {
    margin-left: 8px;
    color: #909399;
    cursor: pointer;
    
    &:hover {
      color: #409EFF;
    }
  }
}

.quick-tags {
  margin-bottom: 12px;
  padding: 10px;
  background-color: #f0f9ff;
  border-radius: 4px;
  
  .quick-tags-header {
    display: flex;
    align-items: center;
    margin-bottom: 8px;
  }
  
  .quick-tags-label {
    margin-right: 10px;
    color: #606266;
    font-size: 14px;
    font-weight: 500;
  }
  
  .quick-tags-help {
    color: #909399;
    cursor: pointer;
    
    &:hover {
      color: #409EFF;
    }
  }
  
  .quick-tags-content {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }
  
  .quick-tag {
    margin-right: 0;
    margin-bottom: 6px;
    cursor: pointer;
    transition: all 0.2s;
    
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
  
  .toggle-help {
    margin-right: 8px;
    color: #909399;
    cursor: pointer;
    
    &:hover {
      color: #409EFF;
    }
  }
  
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
  
  .category-tabs-help {
    color: #909399;
    font-size: 13px;
    text-align: center;
    margin-bottom: 0;
    padding: 10px 0;
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
  margin-right: 0;
  border-color: #d9ecff;
  
  &:hover {
    background-color: #409EFF;
    color: #fff;
  }
}

.role-tag {
  margin-left: 10px;
  font-size: 13px;
}

.role-tabs {
  margin-bottom: 15px;
  overflow-x: auto;
  white-space: nowrap;
  padding-bottom: 5px;
  
  .el-radio-group {
    display: flex;
    flex-wrap: nowrap;
    
    @media screen and (max-width: 768px) {
      .el-radio-button {
        margin-bottom: 5px;
      }
    }
  }
}

.role-card {
  margin-top: 15px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  overflow: hidden;
  transition: all 0.3s;
  
  &:hover {
    box-shadow: 0 4px 12px 0 rgba(0, 0, 0, 0.1);
  }
  
  .role-card-header {
    padding: 12px 15px;
    background-color: #f5f7fa;
    border-bottom: 1px solid #ebeef5;
    display: flex;
    align-items: center;
    
    .role-tag {
      margin: 0;
      padding: 6px 12px;
      font-size: 14px;
      
      i {
        margin-right: 5px;
      }
    }
    
    .industry-tag {
      margin-left: 10px;
      padding: 4px 8px;
      
      i {
        margin-right: 3px;
      }
    }
  }
  
  .role-card-body {
    padding: 15px;
    
    .role-description {
      margin-bottom: 15px;
      color: #606266;
      display: flex;
      align-items: flex-start;
      
      i {
        color: #409EFF;
        margin-right: 8px;
        margin-top: 3px;
      }
      
      span {
        line-height: 1.5;
        flex: 1;
      }
    }
    
    .role-focus-points {
      background-color: #f8f9fa;
      border-radius: 4px;
      padding: 12px;
      
      .focus-point-title {
        font-weight: 500;
        color: #303133;
        margin-bottom: 10px;
      }
      
      .focus-point-list {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
        gap: 8px;
      }
      
      .focus-point-item {
        display: flex;
        align-items: center;
        color: #606266;
        
        i {
          color: #67c23a;
          margin-right: 5px;
        }
      }
    }
    .industry-tips {
      margin-top: 15px;
      background-color: #ecf8ff;
      border-radius: 4px;
      padding: 12px;
      
      .industry-tips-title {
        font-weight: 500;
        color: #409EFF;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        
        i {
          margin-right: 5px;
        }
      }
      
      .industry-tips-list {
        padding-left: 20px;
        margin: 0;
        
        li {
          color: #606266;
          margin-bottom: 6px;
          line-height: 1.6;
        }
      }
    }
  }
}

.role-description {
  margin-top: 12px;
  display: flex;
  align-items: center;
  padding: 8px 12px;
  background-color: #f8f9fb;
  border-radius: 4px;
  border-left: 3px solid #67c23a;
}

.role-desc-text {
  margin-left: 12px;
  color: #606266;
  font-size: 13px;
}

.industry-selector {
  margin-top: 15px;
  display: flex;
  align-items: center;
  background-color: #f8f9fa;
  padding: 10px;
  border-radius: 4px;
  
  .industry-label {
    margin-right: 10px;
    color: #606266;
    font-size: 14px;
    font-weight: 500;
  }
  
  .industry-help {
    margin-left: 8px;
    color: #909399;
    cursor: pointer;
    
    &:hover {
      color: #409EFF;
    }
  }
}

.focus-header {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.focus-header h3 {
  margin: 0;
  margin-right: 15px;
}

.focus-header .el-icon-question {
  margin-left: 8px;
  color: #909399;
  cursor: pointer;
}

/* 添加生成后的高亮效果 */
@keyframes highlight {
  0% { background-color: rgba(64, 158, 255, 0.1); }
  100% { background-color: transparent; }
}

.highlight-animate {
  animation: highlight 2s ease-out;
}

.focus-controls {
  margin-bottom: 15px;
  display: flex;
  align-items: center;
}

.help-icon {
  margin-left: 8px;
  color: #909399;
  cursor: pointer;
  
  &:hover {
    color: #409EFF;
  }
}

.focus-editor {
  margin-bottom: 10px;
  border-radius: 4px;
  transition: all 0.3s;
  
  &.highlight-animate {
    background-color: rgba(64, 158, 255, 0.1);
  }
}
</style> 