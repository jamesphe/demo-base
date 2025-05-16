<template>
  <div v-loading="loading" class="resume-detail">
    <template v-if="detail">
      <!-- 顶部概览 -->
      <div class="detail-section overview-section">
        <div class="candidate-header">
          <div class="candidate-info">
            <h2 class="name">{{ detail.name }}</h2>
            <div class="basic-tags">
              <el-tag size="medium">{{ detail.gender === 'M' ? '男' : '女' }} · {{ detail.age }}岁</el-tag>
              <el-tag size="medium" type="success">{{ detail.education }}</el-tag>
              <el-tag size="medium" type="warning">{{ detail.experience }}年经验</el-tag>
            </div>
          </div>
          <div class="status-info">
            <el-tag :type="getStatusType(detail.status)" size="large">
              {{ getStatusText(detail.status) }}
            </el-tag>
          </div>
        </div>
        <div class="contact-info">
          <div class="info-item">
            <i class="el-icon-phone" />
            <span>{{ detail.phone }}</span>
          </div>
          <div class="info-item">
            <i class="el-icon-message" />
            <span>{{ detail.email }}</span>
          </div>
          <div class="info-item">
            <i class="el-icon-location" />
            <span>{{ detail.currentCity || '未填写' }}</span>
          </div>
        </div>
      </div>

      <!-- 求职意向 - 重要信息前置 -->
      <div class="detail-section">
        <div class="section-header">
          <i class="el-icon-aim" />
          <span>求职意向</span>
        </div>
        <div class="intention-grid">
          <div class="intention-item">
            <div class="label">期望职位</div>
            <div class="value highlight">{{ detail.expectedPosition || '未填写' }}</div>
          </div>
          <div class="intention-item">
            <div class="label">期望薪资</div>
            <div class="value highlight">{{ detail.expectedSalary || '未填写' }}</div>
          </div>
          <div class="intention-item">
            <div class="label">期望地点</div>
            <div class="value">{{ detail.expectedLocation || '未填写' }}</div>
          </div>
          <div class="intention-item">
            <div class="label">当前职位</div>
            <div class="value">{{ detail.currentPosition || '未填写' }}</div>
          </div>
          <div class="intention-item">
            <div class="label">当前公司</div>
            <div class="value">{{ detail.currentCompany || '未填写' }}</div>
          </div>
        </div>
      </div>

      <!-- 技能评估 -->
      <div class="detail-section">
        <div class="section-header">
          <i class="el-icon-medal" />
          <span>技能评估</span>
        </div>
        <div v-if="detail.skills && detail.skills.length" class="skills-table">
          <el-table :data="detail.skills" style="width: 100%" border>
            <el-table-column prop="name" label="技能名称" min-width="180">
              <template slot-scope="scope">
                <span class="skill-name">{{ scope.row.name }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="level" label="熟练程度" min-width="120" align="center">
              <template slot-scope="scope">
                <el-tag :type="getSkillTagType(scope.row.level)" size="medium">
                  {{ scope.row.level || '一般' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
        <div v-else class="no-data">暂无技能标签</div>
      </div>

      <!-- 工作经历 -->
      <div class="detail-section">
        <div class="section-header">
          <i class="el-icon-office-building" />
          <span>工作经历</span>
        </div>
        <div class="experience-timeline">
          <el-timeline v-if="sortedWorkExperience.length">
            <el-timeline-item
              v-for="(work, index) in sortedWorkExperience"
              :key="index"
              :timestamp="work.period"
              placement="top"
              :type="index === 0 ? 'primary' : ''"
            >
              <el-card class="timeline-card">
                <div class="card-header">
                  <div class="header-main">
                    <h4>{{ work.company }}</h4>
                    <span class="position highlight">{{ work.position }}</span>
                  </div>
                  <div class="work-period">
                    <i class="el-icon-time" />
                    <span>{{ formatWorkPeriod(work.startDate, work.endDate) }}</span>
                    <span v-if="work.duration" class="duration">({{ work.duration }})</span>
                  </div>
                </div>
                <div class="card-content">
                  <p class="description">{{ work.description }}</p>
                  <div v-if="work.achievements && work.achievements.length" class="achievements">
                    <p class="achievements-title">主要成就：</p>
                    <ul>
                      <li v-for="(achievement, i) in work.achievements" :key="i">
                        {{ achievement }}
                      </li>
                    </ul>
                  </div>
                </div>
              </el-card>
            </el-timeline-item>
          </el-timeline>
          <div v-else class="no-data">暂无工作经历</div>
        </div>
      </div>

      <!-- 教育经历 -->
      <div class="detail-section">
        <div class="section-header">
          <i class="el-icon-reading" />
          <span>教育经历</span>
        </div>
        <div class="education-timeline">
          <el-timeline v-if="detail.educationDetail && detail.educationDetail.length">
            <el-timeline-item
              v-for="(edu, index) in detail.educationDetail"
              :key="index"
              :timestamp="edu.period"
              placement="top"
              :type="index === 0 ? 'primary' : ''"
            >
              <el-card class="timeline-card">
                <div class="card-header">
                  <div class="header-main">
                    <h4>{{ edu.school }}</h4>
                    <span class="major highlight">{{ edu.major }} · {{ edu.degree }}</span>
                  </div>
                  <div class="edu-period">
                    <i class="el-icon-time" />
                    <span>{{ formatWorkPeriod(edu.startDate, edu.endDate) }}</span>
                  </div>
                </div>
                <div class="card-content">
                  <div v-if="edu.achievements && edu.achievements.length" class="achievements">
                    <p class="achievements-title">主要成就：</p>
                    <ul>
                      <li v-for="(achievement, i) in edu.achievements" :key="i">
                        {{ achievement }}
                      </li>
                    </ul>
                  </div>
                </div>
              </el-card>
            </el-timeline-item>
          </el-timeline>
          <div v-else class="no-data">暂无教育经历</div>
        </div>
      </div>

      <!-- 项目经历 -->
      <div class="detail-section">
        <div class="section-header">
          <i class="el-icon-s-cooperation" />
          <span>项目经历</span>
        </div>
        <div class="project-timeline">
          <el-timeline v-if="detail.projectExperience && detail.projectExperience.length">
            <el-timeline-item
              v-for="(project, index) in detail.projectExperience"
              :key="index"
              :timestamp="formatWorkPeriod(project.startDate, project.endDate)"
              placement="top"
            >
              <el-card class="timeline-card">
                <div class="card-header">
                  <div class="header-main">
                    <h4>{{ project.name }}</h4>
                    <span class="role highlight">{{ project.role || '未填写' }}</span>
                  </div>
                  <div class="project-meta">
                    <span v-if="project.company" class="company">
                      <i class="el-icon-office-building" />
                      {{ project.company }}
                    </span>
                    <span v-if="project.technologies" class="technologies">
                      <i class="el-icon-cpu" />
                      {{ Array.isArray(project.technologies) ? project.technologies.join('、') : project.technologies }}
                    </span>
                  </div>
                </div>
                <div class="card-content">
                  <div v-if="project.description" class="description">
                    <p class="section-title">项目描述：</p>
                    <p>{{ project.description }}</p>
                  </div>
                  <div v-if="project.responsibilities && project.responsibilities.length">
                    <p class="section-title">主要职责：</p>
                    <ul>
                      <li v-for="(resp, i) in project.responsibilities" :key="i">
                        {{ resp }}
                      </li>
                    </ul>
                  </div>
                  <div v-if="project.achievements && project.achievements.length">
                    <p class="section-title">项目成果：</p>
                    <ul>
                      <li v-for="(achievement, i) in project.achievements" :key="i">
                        {{ achievement }}
                      </li>
                    </ul>
                  </div>
                </div>
              </el-card>
            </el-timeline-item>
          </el-timeline>
          <div v-else class="no-data">暂无项目经历</div>
        </div>
      </div>

      <!-- 其他信息 -->
      <div class="detail-section">
        <div class="section-header">
          <i class="el-icon-info" />
          <span>其他信息</span>
        </div>
        <div v-if="detail.otherInfo" class="other-info">
          <p>{{ detail.otherInfo }}</p>
        </div>
        <div v-else class="no-data">暂无其他信息</div>
      </div>
    </template>
    <div v-else class="no-data-container">
      <div class="no-data">
        <i class="el-icon-document" />
        <p>暂无简历详情</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ResumeDetail',
  props: {
    detail: {
      type: Object,
      default: () => ({})
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    sortedWorkExperience() {
      if (!this.detail?.workExperience) return []
      return [...this.detail.workExperience].sort((a, b) => {
        const getTime = date => date ? new Date(date).getTime() : Date.now()
        const aTime = getTime(a.endDate)
        const bTime = getTime(b.endDate)
        return bTime - aTime // 倒序排列
      })
    }
  },
  watch: {
    detail: {
      handler(newVal) {
        console.log('简历详情数据变化：', newVal)
      },
      immediate: true
    },
    loading(newVal) {
      console.log('加载状态变化：', newVal)
    }
  },
  created() {
    console.log('ResumeDetail组件创建，初始数据：', {
      detail: this.detail,
      loading: this.loading
    })
  },
  methods: {
    getStatusType(status) {
      console.log('状态类型计算：', status)
      const statusMap = {
        pending: 'info',
        invited: 'warning',
        interviewed: 'success',
        rejected: 'danger',
        hired: 'success'
      }
      return statusMap[status] || 'info'
    },
    getStatusText(status) {
      console.log('状态文本计算：', status)
      const textMap = {
        pending: '待处理',
        invited: '已邀约',
        interviewed: '已面试',
        rejected: '不合适',
        hired: '已录用'
      }
      return textMap[status] || status
    },
    getSkillTagType(level) {
      console.log('技能等级类型计算：', level)
      const typeMap = {
        '精通': 'success',
        '熟练': 'primary',
        '良好': 'warning',
        '一般': 'info'
      }
      return typeMap[level] || ''
    },
    formatWorkPeriod(startDate, endDate) {
      if (!startDate) return '时间未知'
      const formatDate = date => {
        if (!date) return ''
        const d = new Date(date)
        return `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, '0')}`
      }
      const start = formatDate(startDate)
      const end = endDate ? formatDate(endDate) : '至今'
      return `${start} - ${end}`
    }
  }
}
</script>

<style lang="scss" scoped>
.resume-detail {
  .detail-section {
    margin-bottom: 24px;
    background: #fff;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);

    &.overview-section {
      background: linear-gradient(135deg, #1890ff0d 0%, #fff 100%);
    }

    .candidate-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 20px;

      .candidate-info {
        .name {
          font-size: 24px;
          font-weight: 600;
          color: #303133;
          margin: 0 0 12px;
        }

        .basic-tags {
          .el-tag {
            margin-right: 8px;
          }
        }
      }
    }

    .contact-info {
      display: flex;
      gap: 24px;

      .info-item {
        display: flex;
        align-items: center;
        color: #606266;

        i {
          margin-right: 8px;
          font-size: 16px;
          color: #409EFF;
        }
      }
    }

    .section-header {
      display: flex;
      align-items: center;
      margin-bottom: 20px;
      padding-bottom: 12px;
      border-bottom: 1px solid #ebeef5;

      i {
        font-size: 20px;
        color: #409EFF;
        margin-right: 8px;
      }

      span {
        font-size: 16px;
        font-weight: 600;
        color: #303133;
      }
    }
  }

  .intention-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;

    .intention-item {
      padding: 16px;
      background: #f8f9fa;
      border-radius: 4px;

      .label {
        font-size: 13px;
        color: #909399;
        margin-bottom: 8px;
      }

      .value {
        font-size: 15px;
        color: #303133;

        &.highlight {
          color: #409EFF;
          font-weight: 500;
        }
      }
    }
  }

  .skills-table {
    .el-table {
      border-radius: 4px;
      overflow: hidden;

      :deep(.el-table__header) {
        th {
          background-color: #f5f7fa;
          color: #606266;
          font-weight: 600;
          padding: 12px;
        }
      }

      :deep(.el-table__body) {
        td {
          padding: 16px;
        }
      }
    }

    .skill-name {
      font-weight: 500;
      color: #303133;
    }
  }

  .timeline-card {
    .card-header {
      margin-bottom: 16px;
      display: flex;
      justify-content: space-between;
      align-items: flex-start;

      .header-main {
        h4 {
          margin: 0;
          font-size: 16px;
          color: #303133;
        }

        .position {
          display: block;
          margin-top: 8px;
          font-size: 14px;
          color: #606266;

          &.highlight {
            color: #409EFF;
            font-weight: 500;
          }
        }
      }

      .work-period {
        display: flex;
        align-items: center;
        color: #909399;
        font-size: 13px;

        i {
          margin-right: 4px;
          font-size: 14px;
        }

        .duration {
          margin-left: 4px;
          color: #409EFF;
        }
      }
    }

    .card-content {
      .description {
        margin: 0 0 16px;
        color: #606266;
        line-height: 1.6;
      }

      .section-title,
      .achievements-title {
        margin: 16px 0 12px;
        font-weight: 500;
        color: #303133;
      }

      ul {
        margin: 0;
        padding-left: 20px;
        color: #606266;

        li {
          margin-bottom: 8px;
          line-height: 1.6;

          &:last-child {
            margin-bottom: 0;
          }
        }
      }
    }
  }

  .no-data {
    color: #909399;
    font-size: 14px;
    text-align: center;
    padding: 24px;

    i {
      font-size: 48px;
      margin-bottom: 12px;
      display: block;
    }

    p {
      margin: 0;
    }
  }

  .no-data-container {
    padding: 40px;
    text-align: center;
    background: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  }

  .project-meta {
    margin-top: 12px;
    display: flex;
    gap: 16px;
    color: #606266;
    font-size: 13px;

    span {
      display: flex;
      align-items: center;

      i {
        margin-right: 4px;
        font-size: 14px;
        color: #409EFF;
      }
    }

    .company {
      color: #606266;
    }

    .technologies {
      color: #67c23a;
    }
  }
}
</style>
