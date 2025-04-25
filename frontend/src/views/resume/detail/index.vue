<template>
  <div class="resume-detail">
    <el-card class="detail-card">
      <!-- 基本信息 -->
      <div class="section basic-info">
        <div class="header">
          <h2>{{ resume.name }}</h2>
          <el-tag>{{ resume.title }}</el-tag>
        </div>
        <div class="info-grid">
          <div class="info-item">
            <i class="el-icon-user" />
            <span>{{ resume.gender }} | {{ resume.age }}岁</span>
          </div>
          <div class="info-item">
            <i class="el-icon-phone" />
            <span>{{ resume.phone }}</span>
          </div>
          <div class="info-item">
            <i class="el-icon-message" />
            <span>{{ resume.email }}</span>
          </div>
          <div class="info-item">
            <i class="el-icon-location" />
            <span>{{ resume.location }}</span>
          </div>
        </div>
      </div>

      <!-- 技能标签 -->
      <div class="section skills">
        <h3>技能特长</h3>
        <div class="skill-tags">
          <el-tag
            v-for="skill in resume.skills"
            :key="skill"
            size="medium"
            class="skill-tag"
          >
            {{ skill }}
          </el-tag>
        </div>
      </div>

      <!-- 工作经历 -->
      <div class="section work-experience">
        <h3>工作经历</h3>
        <el-timeline>
          <el-timeline-item
            v-for="work in resume.workExperience"
            :key="work.period"
            :timestamp="work.period"
            placement="top"
          >
            <el-card>
              <h4>{{ work.company }}</h4>
              <p class="position">{{ work.position }}</p>
              <p class="description">{{ work.description }}</p>
              <div class="achievements">
                <p v-for="(achievement, index) in work.achievements" :key="index">
                  · {{ achievement }}
                </p>
              </div>
            </el-card>
          </el-timeline-item>
        </el-timeline>
      </div>

      <!-- 教育经历 -->
      <div class="section education">
        <h3>教育经历</h3>
        <el-timeline>
          <el-timeline-item
            v-for="edu in resume.educationDetail"
            :key="edu.period"
            :timestamp="edu.period"
            placement="top"
          >
            <el-card>
              <h4>{{ edu.school }}</h4>
              <p>{{ edu.major }} | {{ edu.degree }}</p>
              <div class="achievements">
                <p v-for="(achievement, index) in edu.achievements" :key="index">
                  · {{ achievement }}
                </p>
              </div>
            </el-card>
          </el-timeline-item>
        </el-timeline>
      </div>

      <!-- 项目经历 -->
      <div class="section projects">
        <h3>项目经历</h3>
        <div class="project-list">
          <el-card
            v-for="project in resume.projects"
            :key="project.name"
            class="project-card"
          >
            <div class="project-header">
              <h4>{{ project.name }}</h4>
              <span class="period">{{ project.period }}</span>
            </div>
            <p class="description">{{ project.description }}</p>
            <p class="responsibility">
              <strong>主要职责：</strong>{{ project.responsibility }}
            </p>
          </el-card>
        </div>
      </div>

      <!-- 自我评价 -->
      <div class="section self-evaluation">
        <h3>自我评价</h3>
        <p>{{ resume.selfEvaluation }}</p>
      </div>

      <!-- 操作按钮 -->
      <div class="actions">
        <el-button type="primary" @click="downloadResume">下载简历</el-button>
        <el-button
          :type="resume.starred ? 'warning' : 'info'"
          @click="toggleStar"
        >
          {{ resume.starred ? '取消收藏' : '收藏简历' }}
        </el-button>
        <el-button type="success" @click="showAiAnalysis">AI解读</el-button>
        <el-button @click="goBack">返回</el-button>
      </div>
    </el-card>

    <!-- AI解读对话框 -->
    <el-dialog
      title="AI简历解读"
      :visible.sync="aiAnalysisVisible"
      width="70%"
      :before-close="closeAiAnalysis"
      custom-class="ai-analysis-dialog"
    >
      <div v-loading="aiAnalysisLoading" class="ai-analysis-container">
        <div v-if="!aiAnalysisResult" class="analysis-form">
          <h3>请配置AI解读参数</h3>
          <el-form :model="aiAnalysisForm" label-width="100px" class="ai-form">
            <el-form-item label="职位要求">
              <div class="requirements-header">
                <el-button type="text" size="small" @click="openPositionSelector">
                  <i class="el-icon-plus"></i> 从现有职位导入
                </el-button>
              </div>
              <el-input
                type="textarea"
                v-model="aiAnalysisForm.job_requirements"
                :rows="5"
                placeholder="请输入目标职位的详细要求描述，越详细越有助于精准分析"
              ></el-input>
            </el-form-item>
            
            <el-form-item label="分析维度">
              <el-checkbox-group v-model="aiAnalysisForm.dimensions">
                <el-checkbox label="技能匹配度">技能匹配度</el-checkbox>
                <el-checkbox label="专业经验">专业经验</el-checkbox>
                <el-checkbox label="教育背景">教育背景</el-checkbox>
                <el-checkbox label="职业发展">职业发展</el-checkbox>
                <el-checkbox label="综合能力">综合能力</el-checkbox>
              </el-checkbox-group>
            </el-form-item>
            
            <el-form-item label="特别关注点">
              <el-input
                type="textarea"
                v-model="aiAnalysisForm.questions"
                :rows="2"
                placeholder="有什么特别需要关注的问题？"
              ></el-input>
            </el-form-item>
            
            <el-form-item>
              <el-checkbox v-model="aiAnalysisForm.include_interview_tips">
                包含面试建议和推荐问题
              </el-checkbox>
            </el-form-item>
          </el-form>
          
          <div class="ai-analysis-actions">
            <el-button @click="closeAiAnalysis">取消</el-button>
            <el-button type="primary" @click="startAiAnalysis" :disabled="aiAnalysisLoading">
              开始解读
            </el-button>
          </div>
        </div>
        
        <div v-else class="analysis-result">
          <h3>解读结果</h3>
          
          <div class="result-section">
            <h4>候选人概述</h4>
            <p>{{ aiAnalysisResult.summary }}</p>
          </div>
          
          <div class="result-section">
            <h4>匹配度</h4>
            <el-progress :percentage="aiAnalysisResult.match_score" :color="matchScoreColor"></el-progress>
            <span class="score-text">{{ aiAnalysisResult.match_score }}% 匹配度</span>
          </div>
          
          <div class="result-section">
            <h4>技能分析</h4>
            <p>{{ aiAnalysisResult.skill_analysis }}</p>
            <div v-if="aiAnalysisResult.skills && aiAnalysisResult.skills.length" class="skill-tags">
              <el-tag
                v-for="(skill, index) in aiAnalysisResult.skills"
                :key="index"
                :type="getSkillMatchType(skill.match)"
                class="skill-tag"
              >
                {{ skill.name }}: {{ skill.match && !isNaN(skill.match) ? Math.floor(skill.match) + '%' : '未知' }}
              </el-tag>
            </div>
          </div>
          
          <div class="result-section">
            <h4>工作经验</h4>
            <p>{{ aiAnalysisResult.experience_analysis }}</p>
          </div>
          
          <div class="result-section">
            <h4>教育背景</h4>
            <p>{{ aiAnalysisResult.education_analysis }}</p>
          </div>
          
          <div class="result-section">
            <h4>职业发展</h4>
            <p>{{ aiAnalysisResult.career_analysis }}</p>
          </div>
          
          <div v-if="aiAnalysisResult.strengths && aiAnalysisResult.strengths.length || aiAnalysisResult.weaknesses && aiAnalysisResult.weaknesses.length" class="strengths-weaknesses">
            <div v-if="aiAnalysisResult.strengths && aiAnalysisResult.strengths.length" class="advantages">
              <h4>核心优势</h4>
              <ul>
                <li v-for="(strength, index) in aiAnalysisResult.strengths" :key="'s'+index">
                  {{ strength }}
                </li>
              </ul>
            </div>
            
            <div v-if="aiAnalysisResult.weaknesses && aiAnalysisResult.weaknesses.length" class="disadvantages">
              <h4>潜在不足</h4>
              <ul>
                <li v-for="(weakness, index) in aiAnalysisResult.weaknesses" :key="'w'+index">
                  {{ weakness }}
                </li>
              </ul>
            </div>
          </div>
          
          <div v-if="aiAnalysisResult.interview_tips" class="interview-tips">
            <h4>面试建议</h4>
            <p>{{ aiAnalysisResult.interview_tips }}</p>
            
            <h4 v-if="aiAnalysisResult.suggested_questions && aiAnalysisResult.suggested_questions.length">建议问题</h4>
            <ol v-if="aiAnalysisResult.suggested_questions && aiAnalysisResult.suggested_questions.length">
              <li v-for="(question, index) in aiAnalysisResult.suggested_questions" :key="index">
                {{ question }}
              </li>
            </ol>
          </div>
          
          <div class="result-section">
            <h4>结论</h4>
            <p>{{ aiAnalysisResult.conclusion }}</p>
          </div>
          
          <div class="recommendation">
            <el-tag
              :type="getRecommendationType(aiAnalysisResult.recommendation)"
              size="large"
            >
              {{ aiAnalysisResult.recommendation }}
            </el-tag>
          </div>
          
          <div class="ai-analysis-actions">
            <el-button @click="resetAiAnalysis">返回修改</el-button>
            <el-button type="primary" @click="saveAiAnalysis">保存解读结果</el-button>
            <el-button type="success" @click="exportAiAnalysis">导出报告</el-button>
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- 职位选择器对话框 -->
    <el-dialog
      title="选择职位模板"
      :visible.sync="showPositionSelector"
      width="50%"
      append-to-body
    >
      <div v-loading="positionsLoading" class="position-selector-container">
        <div v-if="companyPositions.length === 0 && !positionsLoading" class="empty-data">
          <i class="el-icon-document"></i>
          <p>暂无职位数据</p>
          <el-button type="primary" size="small" @click="fetchPositions">刷新</el-button>
        </div>
        
        <el-table 
          v-else 
          :data="companyPositions" 
          style="width: 100%" 
          @row-click="importPositionRequirements"
          border
          stripe
        >
          <el-table-column prop="id" label="ID" width="80" align="center"></el-table-column>
          <el-table-column prop="name" label="职位名称"></el-table-column>
          <el-table-column label="操作" width="120" align="center">
            <template slot-scope="{row}">
              <el-button size="mini" type="primary" @click.stop="importPositionRequirements(row)">导入</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
      
      <div slot="footer" class="dialog-footer">
        <el-button @click="showPositionSelector = false">取消</el-button>
        <el-button type="primary" @click="fetchPositions" :loading="positionsLoading">刷新职位</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { getResumeDetail, downloadResume, toggleResumeStar, analyzeResumeWithAI } from '@/api/resume'
import { getPositionList } from '@/api/position'
import html2canvas from 'html2canvas'
import jsPDF from 'jspdf'

export default {
  name: 'ResumeDetail',

  data() {
    return {
      resume: {},
      loading: false,
      aiAnalysisVisible: false,
      aiAnalysisLoading: false,
      aiAnalysisResult: null,
      aiAnalysisForm: {
        job_requirements: '',
        dimensions: ['技能匹配度', '专业经验', '教育背景', '职业发展', '综合能力'],
        questions: '',
        include_interview_tips: true
      },
      showPositionSelector: false,
      companyPositions: [],
      positionsLoading: false,
    }
  },

  computed: {
    matchScoreColor() {
      if (!this.aiAnalysisResult) return '';
      const score = this.aiAnalysisResult.match_score;
      if (score >= 85) return '#67C23A';
      if (score >= 70) return '#409EFF';
      if (score >= 60) return '#E6A23C';
      return '#F56C6C';
    }
  },

  created() {
    this.getDetail()
  },

  methods: {
    async getDetail() {
      this.loading = true
      try {
        const { data } = await getResumeDetail(this.$route.params.id)
        this.resume = data
      } catch (error) {
        this.$message.error('获取简历详情失败：' + error.message)
      } finally {
        this.loading = false
      }
    },

    async downloadResume() {
      try {
        await downloadResume(this.resume.id)
        this.$message.success('简历下载成功')
      } catch (error) {
        this.$message.error('简历下载失败：' + error.message)
      }
    },

    async toggleStar() {
      try {
        await toggleResumeStar(this.resume.id, !this.resume.starred)
        this.resume.starred = !this.resume.starred
        this.$message.success(this.resume.starred ? '收藏成功' : '已取消收藏')
      } catch (error) {
        this.$message.error('操作失败：' + error.message)
      }
    },

    goBack() {
      this.$router.back()
    },

    showAiAnalysis() {
      this.aiAnalysisVisible = true
      this.aiAnalysisResult = null
      
      this.aiAnalysisForm.job_requirements = `职位名称：[请输入职位名称]\n技能要求：[请输入所需技能]\n工作经验：[请输入所需工作经验]\n学历要求：[请输入学历要求]\n其他要求：[请输入其他要求]`;
      
      if (this.companyPositions.length === 0) {
        this.fetchPositions();
      }
    },

    async fetchPositions() {
      this.positionsLoading = true;
      try {
        const response = await getPositionList({
          page: 1,
          per_page: 50,
          status: 1
        });
        
        if (response && response.data && Array.isArray(response.data)) {
          this.companyPositions = response.data.map(position => ({
            id: position.id,
            name: position.title || '未命名职位',
            requirements: this.formatPositionRequirements(position)
          }));
        } else {
          console.warn('职位数据格式不符合预期:', response);
          this.$message.warning('获取职位列表失败，请稍后重试');
        }
      } catch (error) {
        console.error('获取职位列表失败:', error);
        this.$message.error('获取职位列表失败: ' + (error.message || '未知错误'));
      } finally {
        this.positionsLoading = false;
      }
    },

    formatPositionRequirements(position) {
      let requirements = `职位名称：${position.title || '未命名职位'}\n`;
      
      if (position.requirements) {
        requirements += `技能要求：${position.requirements}\n`;
      } else if (position.required_skills && position.required_skills.length) {
        const skillNames = position.required_skills.map(skill => skill.name || skill).join('、');
        requirements += `技能要求：${skillNames}\n`;
      } else {
        requirements += `技能要求：无\n`;
      }
      
      requirements += `工作经验：${position.experienceRequired || position.experience || '无要求'}\n`;
      
      let education = position.educationRequired || position.education || '无要求';
      if (education === 'bachelor') education = '本科';
      else if (education === 'master') education = '硕士';
      else if (education === 'doctor') education = '博士';
      else if (education === 'college') education = '大专';
      else if (education === 'highschool') education = '高中';
      requirements += `学历要求：${education}\n`;
      
      requirements += `其他要求：${position.description || '无'}`;
      
      return requirements;
    },

    openPositionSelector() {
      this.showPositionSelector = true;
    },

    importPositionRequirements(position) {
      this.aiAnalysisForm.job_requirements = position.requirements;
      this.showPositionSelector = false;
    },

    closeAiAnalysis() {
      this.aiAnalysisVisible = false
      this.aiAnalysisResult = null
      this.aiAnalysisLoading = false
      this.showPositionSelector = false
    },

    async startAiAnalysis() {
      if (!this.aiAnalysisForm.job_requirements) {
        this.$message.warning('请填写岗位要求，以便AI进行更准确的分析')
        return
      }
      
      this.aiAnalysisLoading = true
      
      try {
        const response = await analyzeResumeWithAI(
          this.resume.id,
          this.aiAnalysisForm
        )
        
        this.aiAnalysisResult = response.data
      } catch (error) {
        console.error('AI分析失败:', error)
        this.$message.error('AI分析失败: ' + (error.message || '未知错误'))
      } finally {
        this.aiAnalysisLoading = false
      }
    },

    resetAiAnalysis() {
      this.aiAnalysisResult = null
    },

    saveAiAnalysis() {
      this.$message.success('AI解读结果已保存到候选人档案')
      this.closeAiAnalysis()
    },

    async exportAiAnalysis() {
      try {
        this.$message.info('正在生成PDF报告，请稍候...')
        
        const contentElement = document.querySelector('.analysis-result')
        if (!contentElement) {
          this.$message.error('未找到要导出的内容')
          return
        }
        
        const printContainer = document.createElement('div')
        printContainer.className = 'print-container'
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
        `
        
        const candidateName = this.resume?.name || '候选人'
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
              <p style="line-height: 1.6;">${this.aiAnalysisResult.summary}</p>
            </div>
            
            <div class="print-section">
              <h2 style="font-size: 14pt; color: #303133; border-bottom: 1px solid #eee; padding-bottom: 5px;">
                岗位匹配度
              </h2>
              <p style="font-weight: bold; font-size: 14pt; color: ${this.matchScoreColor}; margin: 10px 0;">
                ${this.aiAnalysisResult.match_score}% 匹配
              </p>
            </div>
            
            <div class="print-section">
              <h2 style="font-size: 14pt; color: #303133; border-bottom: 1px solid #eee; padding-bottom: 5px;">
                技能分析
              </h2>
              <p style="line-height: 1.6;">${this.aiAnalysisResult.skill_analysis || ''}</p>
              <div style="margin-top: 10px;">
                ${(this.aiAnalysisResult.skills || []).map(skill => {
                  let bgColor = '#F56C6C'
                  if (skill.match >= 85) bgColor = '#67C23A'
                  else if (skill.match >= 70) bgColor = '#409EFF'
                  else if (skill.match >= 60) bgColor = '#E6A23C'
                  
                  return `<span style="display: inline-block; background-color: ${bgColor}; color: white; 
                                     padding: 4px 8px; margin: 3px; border-radius: 4px;">
                    ${skill.name}: ${skill.match && !isNaN(skill.match) ? Math.floor(skill.match) + '%' : '未知'}
                  </span>`
                }).join('')}
              </div>
            </div>
            
            <div class="print-section">
              <h2 style="font-size: 14pt; color: #303133; border-bottom: 1px solid #eee; padding-bottom: 5px;">
                工作经验分析
              </h2>
              <p style="line-height: 1.6;">${this.aiAnalysisResult.experience_analysis || ''}</p>
            </div>
            
            <div class="print-section">
              <h2 style="font-size: 14pt; color: #303133; border-bottom: 1px solid #eee; padding-bottom: 5px;">
                教育背景评估
              </h2>
              <p style="line-height: 1.6;">${this.aiAnalysisResult.education_analysis || ''}</p>
            </div>
            
            <div class="print-section">
              <h2 style="font-size: 14pt; color: #303133; border-bottom: 1px solid #eee; padding-bottom: 5px;">
                职业发展轨迹
              </h2>
              <p style="line-height: 1.6;">${this.aiAnalysisResult.career_analysis || ''}</p>
            </div>
            
            ${this.aiAnalysisResult.strengths && this.aiAnalysisResult.strengths.length ? `
            <div class="print-section">
              <h2 style="font-size: 14pt; color: #303133; border-bottom: 1px solid #eee; padding-bottom: 5px;">
                候选人优势
              </h2>
              <ul style="padding-left: 20px; line-height: 1.6;">
                ${this.aiAnalysisResult.strengths.map(item => `<li>${item}</li>`).join('')}
              </ul>
            </div>
            ` : ''}
            
            ${this.aiAnalysisResult.weaknesses && this.aiAnalysisResult.weaknesses.length ? `
            <div class="print-section">
              <h2 style="font-size: 14pt; color: #303133; border-bottom: 1px solid #eee; padding-bottom: 5px;">
                需要改进的方面
              </h2>
              <ul style="padding-left: 20px; line-height: 1.6;">
                ${this.aiAnalysisResult.weaknesses.map(item => `<li>${item}</li>`).join('')}
              </ul>
            </div>
            ` : ''}
            
            ${this.aiAnalysisResult.interview_tips ? `
            <div class="print-section">
              <h2 style="font-size: 14pt; color: #303133; border-bottom: 1px solid #eee; padding-bottom: 5px;">
                面试建议
              </h2>
              <p style="line-height: 1.6;">${this.aiAnalysisResult.interview_tips}</p>
            </div>
            ` : ''}
            
            ${this.aiAnalysisResult.suggested_questions && this.aiAnalysisResult.suggested_questions.length ? `
            <div class="print-section">
              <h2 style="font-size: 14pt; color: #303133; border-bottom: 1px solid #eee; padding-bottom: 5px;">
                建议面试问题
              </h2>
              <ol style="padding-left: 20px; line-height: 1.6;">
                ${this.aiAnalysisResult.suggested_questions.map(item => `<li>${item}</li>`).join('')}
              </ol>
            </div>
            ` : ''}
            
            <div class="print-section">
              <h2 style="font-size: 14pt; color: #303133; border-bottom: 1px solid #eee; padding-bottom: 5px;">
                综合结论
              </h2>
              <p style="line-height: 1.6;">${this.aiAnalysisResult.conclusion}</p>
            </div>
            
            <div class="print-section" style="text-align: center; margin-top: 20px;">
              <div style="display: inline-block; padding: 8px 16px; border-radius: 4px; font-size: 14pt; 
                        background-color: ${this.getRecommendationType(this.aiAnalysisResult.recommendation) === 'success' ? '#67C23A' : 
                                          this.getRecommendationType(this.aiAnalysisResult.recommendation) === 'primary' ? '#409EFF' :
                                          this.getRecommendationType(this.aiAnalysisResult.recommendation) === 'warning' ? '#E6A23C' : '#F56C6C'};
                        color: white;">
                ${this.aiAnalysisResult.recommendation}
              </div>
            </div>
          </div>
        `
        
        document.body.appendChild(printContainer)
        
        await new Promise(resolve => setTimeout(resolve, 500))
        
        const doc = new jsPDF({
          orientation: 'portrait',
          unit: 'mm',
          format: 'a4'
        })
        
        const canvas = await html2canvas(printContainer, {
          scale: 2,
          useCORS: true,
          logging: false,
          backgroundColor: '#ffffff',
          width: printContainer.offsetWidth,
          height: printContainer.scrollHeight,
          imageTimeout: 0,
          windowWidth: printContainer.offsetWidth
        })
        
        const imgData = canvas.toDataURL('image/jpeg', 1.0)
        const imgWidth = 210
        const pageHeight = 297
        const imgHeight = canvas.height * imgWidth / canvas.width
        let heightLeft = imgHeight
        let position = 0
        let pageCount = 0
        
        doc.addImage(imgData, 'JPEG', 0, position, imgWidth, imgHeight)
        heightLeft -= pageHeight
        pageCount++
        
        while (heightLeft > 0) {
          position = heightLeft - imgHeight
          doc.addPage()
          doc.addImage(imgData, 'JPEG', 0, position, imgWidth, imgHeight)
          heightLeft -= pageHeight
          pageCount++
        }
        
        for (let i = 0; i < pageCount; i++) {
          doc.setPage(i + 1)
          doc.setFontSize(9)
          doc.text(`第 ${i + 1} 页 / 共 ${pageCount} 页`, imgWidth / 2, pageHeight - 5, { align: 'center' })
        }
        
        doc.save(`${candidateName}_AI解读报告.pdf`)
        
        document.body.removeChild(printContainer)
        
        this.$message.success('AI解读报告已成功导出')
      } catch (error) {
        console.error('导出报告失败:', error)
        this.$message.error('导出报告失败，请重试')
      }
    },

    getSkillMatchType(match) {
      if (!match || isNaN(match)) return 'info'
      if (match >= 85) return 'success'
      if (match >= 70) return 'primary'
      if (match >= 60) return 'warning'
      return 'danger'
    },

    getRecommendationType(recommendation) {
      const typeMap = {
        '强烈推荐': 'success',
        '推荐面试': 'primary',
        '待定': 'warning',
        '不建议继续': 'danger'
      }
      return typeMap[recommendation] || 'info'
    }
  }
}
</script>

<style lang="scss" scoped>
.resume-detail {
  padding: 20px;
  background: #f0f2f5;
  min-height: calc(100vh - 84px);

  .detail-card {
    max-width: 1000px;
    margin: 0 auto;

    .section {
      margin-bottom: 30px;

      h3 {
        margin-bottom: 20px;
        padding-bottom: 10px;
        border-bottom: 1px solid #eee;
      }
    }

    .basic-info {
      .header {
        display: flex;
        align-items: center;
        margin-bottom: 20px;

        h2 {
          margin: 0 15px 0 0;
        }
      }

      .info-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 15px;

        .info-item {
          display: flex;
          align-items: center;

          i {
            margin-right: 8px;
            color: #409EFF;
          }
        }
      }
    }

    .skills {
      .skill-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
      }
    }

    .work-experience, .education {
      .position {
        color: #409EFF;
        margin: 8px 0;
      }

      .description {
        color: #666;
        margin: 8px 0;
      }

      .achievements {
        margin-top: 10px;
        color: #666;

        p {
          margin: 5px 0;
        }
      }
    }

    .projects {
      .project-card {
        margin-bottom: 15px;

        .project-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 10px;

          h4 {
            margin: 0;
          }

          .period {
            color: #999;
            font-size: 14px;
          }
        }

        .description, .responsibility {
          margin: 8px 0;
          color: #666;
        }
      }
    }

    .actions {
      display: flex;
      justify-content: center;
      gap: 15px;
      margin-top: 30px;
      padding-top: 20px;
      border-top: 1px solid #eee;
    }
  }
}

.ai-analysis-dialog {
  .el-dialog__body {
    padding: 20px 30px;
  }
}

.ai-analysis-container {
  min-height: 300px;

  .ai-form {
    margin-top: 20px;
  }

  .analysis-result {
    h3 {
      margin-bottom: 20px;
      font-weight: 600;
      color: #303133;
    }

    .result-section {
      margin-bottom: 24px;

      h4 {
        font-weight: 600;
        margin-bottom: 10px;
        color: #409EFF;
      }

      p {
        line-height: 1.6;
        color: #606266;
      }
    }

    .skill-tags {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 10px;
    }

    .strengths-weaknesses {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
      margin-bottom: 24px;

      ul {
        padding-left: 20px;
        color: #606266;
        
        li {
          margin-bottom: 5px;
          line-height: 1.5;
        }
      }
    }

    .interview-tips {
      margin-bottom: 24px;
      
      ol {
        padding-left: 20px;
        color: #606266;
        
        li {
          margin-bottom: 8px;
          line-height: 1.5;
        }
      }
    }

    .recommendation {
      display: flex;
      justify-content: center;
      margin: 30px 0;
      
      .el-tag {
        font-size: 16px;
        padding: 8px 16px;
      }
    }

    .score-text {
      margin-left: 10px;
      font-weight: 600;
    }
  }

  .ai-analysis-actions {
    display: flex;
    justify-content: center;
    margin-top: 30px;
    gap: 15px;
  }
}

.requirements-header {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 5px;
}

.position-selector-container {
  min-height: 200px;
  
  .empty-data {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 40px 0;
    color: #909399;
    
    i {
      font-size: 48px;
      margin-bottom: 20px;
    }
    
    p {
      margin-bottom: 20px;
      font-size: 16px;
    }
  }
}
</style>
