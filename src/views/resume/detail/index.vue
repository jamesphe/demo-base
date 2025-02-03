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
            <i class="el-icon-user"></i>
            <span>{{ resume.gender }} | {{ resume.age }}岁</span>
          </div>
          <div class="info-item">
            <i class="el-icon-phone"></i>
            <span>{{ resume.phone }}</span>
          </div>
          <div class="info-item">
            <i class="el-icon-message"></i>
            <span>{{ resume.email }}</span>
          </div>
          <div class="info-item">
            <i class="el-icon-location"></i>
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
        <el-button @click="goBack">返回</el-button>
      </div>
    </el-card>
  </div>
</template>

<script>
import { getResumeDetail, downloadResume, toggleResumeStar } from '@/api/resume'

export default {
  name: 'ResumeDetail',
  
  data() {
    return {
      resume: {},
      loading: false
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
</style> 