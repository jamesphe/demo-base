<template>
  <el-dialog
    title="AI简历解读"
    :visible.sync="visible"
    width="65%"
    :before-close="handleClose"
    custom-class="ai-analysis-dialog"
  >
    <div class="ai-analysis-container">
      <!-- 表单部分 -->
      <div v-if="!result && !loading" class="analysis-form">
        <p class="analysis-intro">使用AI对简历进行深度解读，帮助您更好地评估候选人的匹配度和潜力。</p>
        
        <el-form :model="form" label-width="100px" class="ai-form">
          <el-form-item label="岗位要求">
            <el-input
              type="textarea"
              :rows="4"
              placeholder="请输入目标岗位的具体要求，如技能、经验、性格特质等"
              v-model="form.jobRequirements"
            />
          </el-form-item>
          
          <el-form-item label="分析维度">
            <el-checkbox-group v-model="form.dimensions">
              <el-checkbox label="技能匹配度">评估候选人的技能与岗位要求的匹配程度</el-checkbox>
              <el-checkbox label="专业经验">分析候选人的工作经历与行业经验</el-checkbox>
              <el-checkbox label="教育背景">评价候选人的学历与专业背景</el-checkbox>
              <el-checkbox label="职业发展">分析候选人的职业轨迹与稳定性</el-checkbox>
              <el-checkbox label="综合能力">评估候选人的综合素质与潜力</el-checkbox>
            </el-checkbox-group>
          </el-form-item>
          
          <el-form-item label="关注问题">
            <el-input
              type="textarea"
              :rows="3"
              placeholder="有什么特别关注的问题？例如：该候选人是否适合团队文化？"
              v-model="form.questions"
            />
          </el-form-item>
          
          <el-form-item label="面试建议">
            <el-switch
              v-model="form.includeInterviewTips"
              active-text="生成面试问题建议"
            />
          </el-form-item>
        </el-form>
        
        <div class="ai-analysis-actions">
          <el-button @click="handleClose">取消</el-button>
          <el-button type="primary" @click="startAnalysis" :disabled="loading">
            开始解读
          </el-button>
        </div>
      </div>
      
      <!-- 加载中状态 -->
      <div v-else-if="loading" class="analysis-loading">
        <div class="progress-container">
          <div class="loading-icon">
            <div class="pulse-container">
              <div class="pulse-circle"></div>
              <div class="pulse-circle"></div>
              <div class="pulse-circle"></div>
            </div>
            <i class="el-icon-loading"></i>
          </div>
          <h3 class="progress-title">AI简历分析中</h3>
          <el-progress 
            :percentage="Math.floor(progress)" 
            :format="format => `${Math.floor(format)}%`" 
            :stroke-width="14" 
            class="analysis-progress-bar">
          </el-progress>
          <div class="progress-step-container">
            <div class="progress-step">{{ currentStep }}</div>
          </div>
          <p class="progress-tip">{{ currentTip }}</p>
          <div class="progress-time-container">
            <i class="el-icon-time"></i>
            <p class="progress-estimate">预计剩余时间: {{ remainingTime }}</p>
          </div>
        </div>
      </div>
      
      <!-- 结果部分 -->
      <div v-else-if="result" class="analysis-result">
        <div class="resume-summary">
          <h3><i class="el-icon-user"></i> 候选人概况</h3>
          <p>{{ result.summary }}</p>
        </div>
        
        <div class="skill-match">
          <h3><i class="el-icon-data-analysis"></i> 技能匹配度分析</h3>
          <div class="match-card">
            <div class="match-rating">
              <div class="match-progress-container">
                <el-progress :percentage="Math.floor(result.matchScore || result.match_score || 0)" :color="matchScoreColor" :stroke-width="18" class="match-progress"></el-progress>
              </div>
            </div>
            <div class="match-details">
              <p>{{ result.skillAnalysis || result.skill_analysis || '无技能分析数据' }}</p>
              <div v-if="(result.skills && result.skills.length)" class="skill-tags">
                <h4>关键技能评估：</h4>
                <div class="tag-list">
                  <el-tag 
                    v-for="(skill, index) in result.skills" 
                    :key="index"
                    :type="getSkillMatchType(skill.match)"
                    effect="dark"
                    class="skill-tag"
                  >
                    {{ skill.name }}: {{ Math.floor(skill.match) }}%
                  </el-tag>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="experience-analysis">
          <h3><i class="el-icon-office-building"></i> 工作经验分析</h3>
          <div class="analysis-card">
            <p>{{ result.experienceAnalysis || result.experience_analysis || '无工作经验分析数据' }}</p>
          </div>
        </div>
        
        <div class="education-analysis">
          <h3><i class="el-icon-reading"></i> 教育背景评估</h3>
          <div class="analysis-card">
            <p>{{ result.educationAnalysis || result.education_analysis || '无教育背景评估数据' }}</p>
          </div>
        </div>
        
        <div class="career-analysis">
          <h3><i class="el-icon-trend-charts"></i> 职业发展轨迹</h3>
          <div class="analysis-card">
            <p>{{ result.careerAnalysis || result.career_analysis || '无职业发展轨迹数据' }}</p>
          </div>
        </div>
        
        <div v-if="(result.strengths && result.strengths.length) || 
                   (result.weaknesses && result.weaknesses.length)" 
             class="strengths-weaknesses">
          <div v-if="result.strengths && result.strengths.length" class="strengths">
            <h3><i class="el-icon-star-on"></i> 优势亮点</h3>
            <div class="analysis-card">
              <ul>
                <li v-for="(strength, index) in result.strengths" :key="'s'+index">
                  {{ strength }}
                </li>
              </ul>
            </div>
          </div>
          <div v-if="result.weaknesses && result.weaknesses.length" class="weaknesses">
            <h3><i class="el-icon-warning"></i> 不足之处</h3>
            <div class="analysis-card">
              <ul>
                <li v-for="(weakness, index) in result.weaknesses" :key="'w'+index">
                  {{ weakness }}
                </li>
              </ul>
            </div>
          </div>
        </div>
        
        <div v-if="form.includeInterviewTips && 
                  (result.interviewTips || result.interview_tips)" 
             class="interview-tips">
          <h3><i class="el-icon-chat-dot-square"></i> 面试建议</h3>
          <div class="analysis-card">
            <p>{{ result.interviewTips || result.interview_tips }}</p>
            <div v-if="(result.suggestedQuestions && result.suggestedQuestions.length) ||
                      (result.suggested_questions && result.suggested_questions.length)" 
                class="suggested-questions">
              <h4>建议面试问题：</h4>
              <ol>
                <li v-for="(question, index) in (result.suggestedQuestions || result.suggested_questions || [])" :key="index">
                  {{ question }}
                </li>
              </ol>
            </div>
          </div>
        </div>
        
        <div class="conclusion">
          <h3><i class="el-icon-medal"></i> 综合评价</h3>
          <div class="analysis-card conclusion-card">
            <p>{{ result.conclusion }}</p>
            <div v-if="result.recommendation" class="recommendation">
              <span class="recommendation-label">推荐意见：</span>
              <el-tag 
                :type="getRecommendationType(result.recommendation)" 
                effect="dark"
                class="recommendation-tag"
              >
                {{ result.recommendation }}
              </el-tag>
            </div>
          </div>
        </div>
        
        <div class="ai-analysis-actions">
          <el-button @click="resetAnalysis">
            <i class="el-icon-back"></i> 返回修改
          </el-button>
          <el-button type="primary" @click="saveAnalysis">
            <i class="el-icon-check"></i> 保存解读结果
          </el-button>
          <el-button type="success" @click="exportAnalysis">
            <i class="el-icon-download"></i> 导出报告
          </el-button>
        </div>
      </div>
    </div>
  </el-dialog>
</template>

<script>
import { analyzeResumeWithAI } from '@/api/resume'
import html2canvas from 'html2canvas'
import jsPDF from 'jspdf'

export default {
  name: 'AiAnalysisDialog',
  props: {
    visible: {
      type: Boolean,
      required: true
    },
    resume: {
      type: Object,
      default: () => ({})
    }
  },
  data() {
    return {
      form: {
        jobRequirements: '',
        dimensions: ['技能匹配度', '专业经验', '教育背景', '职业发展', '综合能力'],
        questions: '',
        includeInterviewTips: true
      },
      loading: false,
      result: null,
      progress: 0,
      currentStep: "正在初始化...",
      stepIndex: 0,
      analysisSteps: [
        { name: "正在初始化分析引擎..." },
        { name: "正在提取简历数据..." },
        { name: "正在匹配职位要求..." },
        { name: "正在分析技能匹配度..." },
        { name: "正在评估工作经验..." },
        { name: "正在分析教育背景..." },
        { name: "正在生成综合评价..." },
        { name: "正在完善分析报告..." }
      ],
      analysisStartTime: null,
      progressTimer: null,
      loadingTips: [
        '正在提取候选人简历数据...',
        '正在深入分析候选人的技能组合与项目经验...',
        '正在评估候选人的专业能力与岗位匹配度...',
        '正在分析候选人的教育背景与工作经历的相关性...',
        '正在评估候选人的职业发展轨迹与稳定性...',
        '正在生成综合评价报告，这可能需要一点时间...',
        '即将完成，正在整理分析结果...'
      ],
      currentTipIndex: 0,
      tipChangeTimer: null,
      currentTip: '',
      remainingTime: "即将完成"
    }
  },
  computed: {
    matchScoreColor() {
      if (!this.result) return '';
      const score = this.result.matchScore || this.result.match_score || 0;
      if (score >= 85) return '#67C23A';
      if (score >= 70) return '#409EFF';
      if (score >= 60) return '#E6A23C';
      return '#F56C6C';
    }
  },
  watch: {
    visible(val) {
      if (val && this.resume) {
        this.resetForm();
      }
    },
    resume(val) {
      if (val && this.visible) {
        this.resetForm();
      }
    }
  },
  methods: {
    resetForm() {
      this.form = {
        jobRequirements: '',
        dimensions: ['技能匹配度', '专业经验', '教育背景', '职业发展', '综合能力'],
        questions: '',
        includeInterviewTips: true
      };
      
      // 预填职位要求（如果当前有筛选条件）
      if (this.resume.expectedPosition) {
        this.form.jobRequirements = `职位名称：${this.resume.expectedPosition}\n`;
        
        if (this.resume.skills && this.resume.skills.length > 0) {
          const skillNames = this.resume.skills.map(s => s.name || s).join('、');
          this.form.jobRequirements += `技能要求：${skillNames}\n`;
        }
        
        if (this.resume.experience) {
          this.form.jobRequirements += `工作经验：${this.resume.experience}\n`;
        }
        
        if (this.resume.education) {
          this.form.jobRequirements += `学历要求：${this.resume.education}\n`;
        }
      }
    },
    handleClose() {
      this.stopProgressUpdate();
      this.$emit('update:visible', false);
      setTimeout(() => {
        this.result = null;
        this.loading = false;
      }, 300);
    },
    async startAnalysis() {
      if (!this.form.jobRequirements) {
        this.$message.warning('请填写岗位要求，以便AI进行更准确的分析');
        return;
      }
      
      this.loading = true;
      this.result = null;
      
      // 初始化分析进度
      this.progress = 0;
      this.stepIndex = 0;
      this.currentStep = this.analysisSteps[0].name;
      this.analysisStartTime = Date.now();
      this.currentTip = this.loadingTips[0];
      
      // 启动进度更新
      this.startProgressUpdate();
      
      try {
        const resumeId = this.resume.id;
        
        // 准备请求数据
        const analysisRequest = {
          job_requirements: this.form.jobRequirements,
          dimensions: this.form.dimensions,
          questions: this.form.questions,
          include_interview_tips: this.form.includeInterviewTips
        };
        
        // 调用API获取分析结果
        const response = await analyzeResumeWithAI(resumeId, analysisRequest);
        
        // 获取响应数据
        const responseData = response;
        
        // 检查字段名，可能需要转换
        if (responseData.match_score !== undefined && responseData.skill_analysis !== undefined) {
          // 字段名是下划线格式，需要转换为驼峰格式
          this.result = {
            summary: responseData.summary,
            matchScore: responseData.match_score,
            skillAnalysis: responseData.skill_analysis,
            skills: responseData.skills || [],
            experienceAnalysis: responseData.experience_analysis,
            educationAnalysis: responseData.education_analysis,
            careerAnalysis: responseData.career_analysis,
            strengths: responseData.strengths || [],
            weaknesses: responseData.weaknesses || [],
            interviewTips: responseData.interview_tips,
            suggestedQuestions: responseData.suggested_questions || [],
            conclusion: responseData.conclusion,
            recommendation: responseData.recommendation
          };
        } else if (responseData.matchScore !== undefined && responseData.skillAnalysis !== undefined) {
          // 字段名已经是驼峰格式，直接使用
          this.result = responseData;
        } else if (responseData.summary !== undefined) {
          // 至少有summary字段，尝试使用原始数据
          this.result = responseData;
        } else {
          // 无法识别的格式
          throw new Error('API返回数据格式无效：缺少必要字段');
        }
        
        // 确保进度条到达100%
        this.completeProgress();
      } catch (error) {
        console.error('AI分析失败:', error);
        this.$message.error('AI分析失败: ' + (error.message || '未知错误'));
        // 停止进度条
        this.stopProgressUpdate();
        this.loading = false;
      }
    },
    startProgressUpdate() {
      // 重置进度状态
      this.progress = 0;
      
      // 清除之前的定时器
      this.stopProgressUpdate();
      
      // 开始提示文字轮换
      this.currentTipIndex = 0;
      this.currentTip = this.loadingTips[0];
      
      // 设置定时切换提示
      this.tipChangeTimer = setInterval(() => {
        this.currentTipIndex = (this.currentTipIndex + 1) % this.loadingTips.length;
        this.currentTip = this.loadingTips[this.currentTipIndex];
      }, 5000);
      
      // 模拟进度增长
      this.progressTimer = setInterval(() => {
        if (this.progress < 95) {
          // 计算当前应该停留在哪个阶段
          const totalSteps = this.analysisSteps.length;
          const targetStepIndex = Math.floor(this.progress / (95 / totalSteps));
          
          // 更新当前步骤（如果需要）
          if (targetStepIndex > this.stepIndex && targetStepIndex < totalSteps) {
            this.stepIndex = targetStepIndex;
            this.currentStep = this.analysisSteps[this.stepIndex].name;
          }
          
          // 非线性增长，初期快，后期慢
          const increment = Math.max(0.5, 5 * Math.exp(-this.progress / 30));
          this.progress = Math.min(95, this.progress + increment);
          
          // 更新剩余时间计算
          this.updateRemainingTime();
        }
      }, 300);
    },
    updateRemainingTime() {
      const elapsedTime = Date.now() - this.analysisStartTime;
      const estimatedTotalTime = elapsedTime / (this.progress / 100);
      const remainingTime = estimatedTotalTime - elapsedTime;
      
      if (remainingTime > 0) {
        const seconds = Math.ceil(remainingTime / 1000);
        if (seconds < 60) {
          this.remainingTime = `${seconds} 秒`;
        } else {
          const minutes = Math.floor(seconds / 60);
          const remainingSeconds = seconds % 60;
          this.remainingTime = `${minutes} 分 ${remainingSeconds} 秒`;
        }
      } else {
        this.remainingTime = "即将完成";
      }
    },
    stopProgressUpdate() {
      if (this.progressTimer) {
        clearInterval(this.progressTimer);
        this.progressTimer = null;
      }
      
      if (this.tipChangeTimer) {
        clearInterval(this.tipChangeTimer);
        this.tipChangeTimer = null;
      }
    },
    completeProgress() {
      // 停止进度条自动增长
      this.stopProgressUpdate();
      
      // 更新到最后一个步骤
      this.stepIndex = this.analysisSteps.length - 1;
      this.currentStep = this.analysisSteps[this.stepIndex].name;
      
      // 平滑动画到100%
      const completeAnimation = setInterval(() => {
        if (this.progress < 100) {
          this.progress = Math.min(100, this.progress + 1);
        } else {
          clearInterval(completeAnimation);
          // 稍微延迟以显示100%完成状态
          setTimeout(() => {
            this.loading = false;
          }, 500);
        }
      }, 20);
    },
    resetAnalysis() {
      this.result = null;
    },
    saveAnalysis() {
      this.$message.success('AI解读结果已保存到候选人档案');
      this.handleClose();
    },
    async exportAnalysis() {
      try {
        this.$message.info('正在生成PDF报告，请稍候...');
        
        // 获取要导出的内容元素
        const contentElement = document.querySelector('.analysis-result');
        if (!contentElement) {
          this.$message.error('未找到要导出的内容');
          return;
        }
        
        // 创建一个专门用于打印的容器
        const printContainer = document.createElement('div');
        printContainer.className = 'print-container';
        printContainer.style.cssText = `
          position: fixed;
          left: -9999px;
          top: 0;
          width: 210mm;
          padding: 20mm;
          background-color: white;
          font-family: SimHei, Arial, sans-serif;
          color: #303133;
          font-size: 12pt;
          box-sizing: border-box;
          z-index: -9999;
        `;
        
        // 创建打印友好的内容
        const candidateName = this.resume?.name || '候选人';
        printContainer.innerHTML = `
          <div class="print-header">
            <h1 style="text-align: center; font-size: 18pt; margin-bottom: 10px;">${candidateName} - AI简历解读报告</h1>
            <p style="text-align: center; color: #666; margin-bottom: 20px;">
              生成日期：${new Date().toLocaleDateString()} ${new Date().toLocaleTimeString()}
            </p>
          </div>
          
          <div class="print-content">
            <div class="print-section">
              <h2 style="font-size: 14pt; color: #303133; border-bottom: 1px solid #eee; padding-bottom: 5px;">
                候选人概况
              </h2>
              <p style="line-height: 1.6;">${this.result.summary}</p>
            </div>
            
            <div class="print-section">
              <h2 style="font-size: 14pt; color: #303133; border-bottom: 1px solid #eee; padding-bottom: 5px;">
                岗位匹配度
              </h2>
              <p style="font-weight: bold; font-size: 14pt; color: ${this.matchScoreColor}; margin: 10px 0;">
                ${this.result.matchScore || this.result.match_score || 0}% 匹配
              </p>
            </div>
            
            <div class="print-section">
              <h2 style="font-size: 14pt; color: #303133; border-bottom: 1px solid #eee; padding-bottom: 5px;">
                技能分析
              </h2>
              <p style="line-height: 1.6;">${this.result.skillAnalysis || this.result.skill_analysis || ''}</p>
              <div style="margin-top: 10px;">
                ${(this.result.skills || []).map(skill => {
                  let bgColor = '#F56C6C'; // 默认红色
                  if (skill.match >= 85) bgColor = '#67C23A'; // 绿色
                  else if (skill.match >= 70) bgColor = '#409EFF'; // 蓝色
                  else if (skill.match >= 60) bgColor = '#E6A23C'; // 黄色
                  
                  return `<span style="display: inline-block; background-color: ${bgColor}; color: white; 
                                     padding: 4px 8px; margin: 3px; border-radius: 4px;">
                    ${skill.name}: ${Math.floor(skill.match)}%
                  </span>`;
                }).join('')}
              </div>
            </div>
            
            <div class="print-section">
              <h2 style="font-size: 14pt; color: #303133; border-bottom: 1px solid #eee; padding-bottom: 5px;">
                工作经验分析
              </h2>
              <p style="line-height: 1.6;">${this.result.experienceAnalysis || this.result.experience_analysis || ''}</p>
            </div>
            
            <div class="print-section">
              <h2 style="font-size: 14pt; color: #303133; border-bottom: 1px solid #eee; padding-bottom: 5px;">
                教育背景评估
              </h2>
              <p style="line-height: 1.6;">${this.result.educationAnalysis || this.result.education_analysis || ''}</p>
            </div>
            
            <div class="print-section">
              <h2 style="font-size: 14pt; color: #303133; border-bottom: 1px solid #eee; padding-bottom: 5px;">
                职业发展轨迹
              </h2>
              <p style="line-height: 1.6;">${this.result.careerAnalysis || this.result.career_analysis || ''}</p>
            </div>
            
            ${this.result.strengths && this.result.strengths.length ? `
            <div class="print-section">
              <h2 style="font-size: 14pt; color: #303133; border-bottom: 1px solid #eee; padding-bottom: 5px;">
                候选人优势
              </h2>
              <ul style="padding-left: 20px; line-height: 1.6;">
                ${this.result.strengths.map(item => `<li>${item}</li>`).join('')}
              </ul>
            </div>
            ` : ''}
            
            ${this.result.weaknesses && this.result.weaknesses.length ? `
            <div class="print-section">
              <h2 style="font-size: 14pt; color: #303133; border-bottom: 1px solid #eee; padding-bottom: 5px;">
                需要改进的方面
              </h2>
              <ul style="padding-left: 20px; line-height: 1.6;">
                ${this.result.weaknesses.map(item => `<li>${item}</li>`).join('')}
              </ul>
            </div>
            ` : ''}
            
            ${this.result.interviewTips || this.result.interview_tips ? `
            <div class="print-section">
              <h2 style="font-size: 14pt; color: #303133; border-bottom: 1px solid #eee; padding-bottom: 5px;">
                面试建议
              </h2>
              <p style="line-height: 1.6;">${this.result.interviewTips || this.result.interview_tips}</p>
            </div>
            ` : ''}
            
            ${this.result.suggestedQuestions && this.result.suggestedQuestions.length ? `
            <div class="print-section">
              <h2 style="font-size: 14pt; color: #303133; border-bottom: 1px solid #eee; padding-bottom: 5px;">
                建议面试问题
              </h2>
              <ol style="padding-left: 20px; line-height: 1.6;">
                ${this.result.suggestedQuestions.map(item => `<li>${item}</li>`).join('')}
              </ol>
            </div>
            ` : ''}
            
            ${this.result.suggested_questions && this.result.suggested_questions.length ? `
            <div class="print-section">
              <h2 style="font-size: 14pt; color: #303133; border-bottom: 1px solid #eee; padding-bottom: 5px;">
                建议面试问题
              </h2>
              <ol style="padding-left: 20px; line-height: 1.6;">
                ${this.result.suggested_questions.map(item => `<li>${item}</li>`).join('')}
              </ol>
            </div>
            ` : ''}
            
            <div class="print-section">
              <h2 style="font-size: 14pt; color: #303133; border-bottom: 1px solid #eee; padding-bottom: 5px;">
                综合结论
              </h2>
              <p style="line-height: 1.6;">${this.result.conclusion}</p>
            </div>
            
            <div class="print-section" style="text-align: center; margin-top: 20px;">
              <div style="display: inline-block; padding: 8px 16px; border-radius: 4px; font-size: 14pt; 
                         background-color: ${this.getRecommendationType(this.result.recommendation) === 'success' ? '#67C23A' : 
                                           this.getRecommendationType(this.result.recommendation) === 'primary' ? '#409EFF' :
                                           this.getRecommendationType(this.result.recommendation) === 'warning' ? '#E6A23C' : '#F56C6C'};
                         color: white;">
                ${this.result.recommendation}
              </div>
            </div>
          </div>
        `;
        
        document.body.appendChild(printContainer);
        
        // 等待内容渲染
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // 创建PDF
        const doc = new jsPDF({
          orientation: 'portrait',
          unit: 'mm',
          format: 'a4'
        });
        
        // 使用html2canvas将重新排版的内容转为图像
        const canvas = await html2canvas(printContainer, {
          scale: 2,
          useCORS: true,
          logging: false,
          backgroundColor: '#ffffff',
          width: printContainer.offsetWidth,
          height: printContainer.scrollHeight,
          imageTimeout: 0,
          windowWidth: printContainer.offsetWidth
        });
        
        // 图像分页处理
        const imgData = canvas.toDataURL('image/jpeg', 1.0);
        const imgWidth = 210; // A4宽度(mm)
        const pageHeight = 297; // A4高度(mm)
        const imgHeight = canvas.height * imgWidth / canvas.width;
        let heightLeft = imgHeight;
        let position = 0;
        let pageCount = 0;
        
        // 添加第一页
        doc.addImage(imgData, 'JPEG', 0, position, imgWidth, imgHeight);
        heightLeft -= pageHeight;
        pageCount++;
        
        // 如果内容超过一页，添加更多页面
        while (heightLeft > 0) {
          position = heightLeft - imgHeight;
          doc.addPage();
          doc.addImage(imgData, 'JPEG', 0, position, imgWidth, imgHeight);
          heightLeft -= pageHeight;
          pageCount++;
        }
        
        // 添加页码
        for (let i = 0; i < pageCount; i++) {
          doc.setPage(i + 1);
          doc.setFontSize(9);
          doc.text(`第 ${i + 1} 页 / 共 ${pageCount} 页`, imgWidth / 2, pageHeight - 5, { align: 'center' });
        }
        
        // 生成PDF文件并下载
        doc.save(`${candidateName}_AI解读报告.pdf`);
        
        // 移除临时元素
        document.body.removeChild(printContainer);
        
        this.$message.success('AI解读报告已成功生成并下载');
      } catch (error) {
        console.error('导出PDF失败:', error);
        this.$message.error('导出PDF失败: ' + (error.message || '未知错误'));
      }
    },
    getSkillMatchType(match) {
      if (match >= 85) return 'success';
      if (match >= 70) return 'primary';
      if (match >= 60) return 'warning';
      return 'danger';
    },
    getRecommendationType(recommendation) {
      const typeMap = {
        '强烈推荐': 'success',
        '推荐': 'primary',
        '待定': 'warning',
        '不建议继续': 'danger',
        '一般推荐': 'info',
        '建议面试': 'success',
        '不推荐': 'danger',
        '需要更多信息': 'warning'
      };
      return typeMap[recommendation] || 'info';
    }
  },
  beforeDestroy() {
    this.stopProgressUpdate();
  }
}
</script>

<style lang="scss" scoped>
.ai-analysis-dialog {
  :deep(.el-dialog__body) {
    padding: 20px 30px;
  }
}

.ai-analysis-container {
  min-height: 300px;
  
  .analysis-intro {
    color: #606266;
    margin-bottom: 20px;
    line-height: 1.6;
  }
  
  .ai-form {
    margin-bottom: 20px;
    
    :deep(.el-form-item__label) {
      font-weight: 500;
    }
    
    :deep(.el-checkbox) {
      margin-right: 20px;
      margin-bottom: 10px;
    }
  }
  
  .ai-analysis-actions {
    padding-top: 20px;
    border-top: 1px solid #EBEEF5;
    display: flex;
    justify-content: flex-end;
    gap: 12px;
  }
  
  // 加载中的样式
  .analysis-loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 30px 20px;
    
    .progress-container {
      background-color: #fff;
      padding: 40px;
      border-radius: 12px;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
      text-align: center;
      width: 90%;
      max-width: 620px;
      margin: 0 auto;
      
      .loading-icon {
        position: relative;
        width: 100px;
        height: 100px;
        margin: 0 auto 25px;
        
        i.el-icon-loading {
          font-size: 48px;
          color: #409EFF;
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          z-index: 2;
        }
        
        .pulse-container {
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          
          .pulse-circle {
            position: absolute;
            border: 3px solid #409EFF;
            border-radius: 50%;
            height: 100%;
            width: 100%;
            opacity: 0;
            animation: pulse-animation 3s infinite;
            
            &:nth-child(2) {
              animation-delay: 1s;
            }
            
            &:nth-child(3) {
              animation-delay: 2s;
            }
          }
        }
      }
      
      .progress-title {
        font-size: 24px;
        font-weight: 600;
        margin-bottom: 25px;
        color: #303133;
        letter-spacing: 1px;
      }
      
      .analysis-progress-bar {
        margin: 15px 0 25px;
        
        :deep(.el-progress-bar__outer) {
          border-radius: 10px;
          background-color: #f0f7ff;
          height: 14px !important;
        }
        
        :deep(.el-progress-bar__inner) {
          border-radius: 10px;
          background: linear-gradient(90deg, #409EFF, #67C23A);
          transition: width 0.5s cubic-bezier(0.23, 1, 0.32, 1);
        }
        
        :deep(.el-progress__text) {
          font-size: 18px !important;
          color: #409EFF;
          font-weight: 600;
          min-width: 60px !important;
        }
      }
      
      .progress-step-container {
        margin: 20px 0;
        
        .progress-step {
          display: inline-block;
          background-color: #ecf5ff;
          color: #409EFF;
          padding: 10px 20px;
          border-radius: 30px;
          font-weight: 500;
          font-size: 16px;
          box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
          transition: all 0.3s ease;
          border: 1px solid rgba(64, 158, 255, 0.2);
        }
      }
      
      .progress-tip {
        font-size: 15px;
        color: #606266;
        margin: 15px 0;
        min-height: 22px;
      }
      
      .progress-time-container {
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 20px 0 0;
        background-color: rgba(64, 158, 255, 0.1);
        padding: 12px 20px;
        border-radius: 8px;
        display: inline-flex;
        
        i {
          font-size: 18px;
          color: #409EFF;
          margin-right: 8px;
          animation: pulse 1.5s infinite;
        }
        
        .progress-estimate {
          font-size: 15px;
          color: #409EFF;
          font-weight: 500;
          margin: 0;
        }
      }
    }
  }
  
  // 结果部分
  .analysis-result {
    padding: 0 10px;
    
    h3 {
      font-size: 18px;
      font-weight: 600;
      margin: 24px 0 16px;
      color: #303133;
      display: flex;
      align-items: center;
      
      i {
        margin-right: 8px;
        font-size: 20px;
        color: #409EFF;
      }
    }
    
    h4 {
      font-size: 16px;
      font-weight: 600;
      margin: 16px 0 12px;
      color: #606266;
    }
    
    p {
      line-height: 1.8;
      color: #606266;
      margin-bottom: 16px;
    }
    
    .resume-summary {
      background-color: #f0f9ff;
      border-radius: 8px;
      padding: 16px 20px;
      margin-bottom: 24px;
      border-left: 4px solid #409EFF;
      
      h3 {
        margin-top: 0;
        
        i {
          color: #409EFF;
        }
      }
      
      p {
        margin-bottom: 0;
      }
    }
    
    .match-card, .analysis-card {
      background-color: #fff;
      border-radius: 8px;
      box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
      padding: 16px 20px;
      margin-bottom: 20px;
      border: 1px solid #EBEEF5;
      transition: all 0.3s;
      
      &:hover {
        box-shadow: 0 4px 12px 0 rgba(0, 0, 0, 0.1);
      }
    }
    
    .match-rating {
      display: flex;
      flex-direction: column;
      margin-bottom: 16px;
      width: 100%;
      
      .match-progress-container {
        width: 100%;
        position: relative;
      }
      
      :deep(.el-progress) {
        margin-bottom: 8px;
        
        .el-progress-bar__outer {
          border-radius: 8px;
          background-color: #E6E6E6;
        }
        
        .el-progress-bar__inner {
          border-radius: 8px;
        }
      }
    }
    
    .skill-tags {
      margin-top: 16px;
      
      .tag-list {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        
        .skill-tag {
          padding: 6px 12px;
          font-size: 13px;
          border-radius: 4px;
          display: flex;
          align-items: center;
          height: 32px;
        }
      }
    }
    
    .experience-analysis, .education-analysis, .career-analysis {
      margin-bottom: 24px;
      
      h3 i {
        color: #409EFF;
      }
      
      .analysis-card {
        border-left: 3px solid #409EFF;
      }
    }
    
    .strengths-weaknesses {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 24px;
      margin-bottom: 24px;
      
      @media (max-width: 768px) {
        grid-template-columns: 1fr;
      }
      
      ul {
        padding-left: 20px;
        margin-top: 0;
        margin-bottom: 0;
        
        li {
          margin-bottom: 10px;
          line-height: 1.6;
          position: relative;
          
          &:last-child {
            margin-bottom: 0;
          }
        }
      }
      
      .strengths {
        h3 i {
          color: #67C23A;
        }
        
        .analysis-card {
          border-left: 3px solid #67C23A;
        }
        
        li {
          color: #67C23A;
          
          &::marker {
            color: #67C23A;
          }
        }
      }
      
      .weaknesses {
        h3 i {
          color: #E6A23C;
        }
        
        .analysis-card {
          border-left: 3px solid #E6A23C;
        }
        
        li {
          color: #E6A23C;
          
          &::marker {
            color: #E6A23C;
          }
        }
      }
    }
    
    .interview-tips {
      margin-bottom: 24px;
      
      h3 i {
        color: #409EFF;
      }
      
      .analysis-card {
        border-left: 3px solid #409EFF;
      }
      
      .suggested-questions {
        ol {
          padding-left: 20px;
          margin-top: 0;
          margin-bottom: 0;
          
          li {
            margin-bottom: 10px;
            line-height: 1.6;
            color: #606266;
            
            &:last-child {
              margin-bottom: 0;
            }
          }
        }
      }
    }
    
    .conclusion-card {
      background-color: #f9f9f9;
      border-left: 4px solid #67C23A;
    }
    
    .recommendation {
      display: flex;
      align-items: center;
      margin-top: 16px;
      border-top: 1px dashed #EBEEF5;
      padding-top: 16px;
      
      .recommendation-label {
        font-weight: 600;
        margin-right: 12px;
        color: #303133;
      }
      
      .recommendation-tag {
        font-size: 14px;
        padding: 8px 16px;
        border-radius: 4px;
        display: flex;
        align-items: center;
        height: 36px;
      }
    }
    
    .ai-analysis-actions {
      display: flex;
      justify-content: center;
      margin-top: 30px;
      padding-top: 20px;
      border-top: 1px solid #EBEEF5;
      gap: 16px;
    }
  }
}

@keyframes pulse-animation {
  0% {
    transform: scale(0.5);
    opacity: 0;
  }
  25% {
    opacity: 0.3;
  }
  50% {
    transform: scale(1.2);
    opacity: 0;
  }
  100% {
    opacity: 0;
  }
}

@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.2);
  }
  100% {
    transform: scale(1);
  }
}
</style> 