<template>
  <div class="result-list-container">
    <el-table :data="resultList" style="width: 100%" :border="true" class="resume-table">
      <el-table-column label="候选人信息" min-width="240">
        <template slot-scope="{row}">
          <div class="candidate-info">
            <div class="primary-info">
              <div class="name-status">
                <el-button type="text" class="name-button" @click="viewDetail(row)">
                  {{ row.name }}
                </el-button>
                <el-tag
                  size="small"
                  :type="getStatusType(row.status)"
                  effect="dark"
                  class="status-tag"
                >
                  {{ getStatusText(row.status) }}
                </el-tag>
              </div>
              <div class="tags">
                <el-tag size="mini" :type="row.gender === 'F' ? 'danger' : 'primary'" class="gender-tag">
                  {{ row.gender === 'F' ? '女' : '男' }}
                </el-tag>
                <el-tag size="mini" type="success">{{ row.age }}岁</el-tag>
                <el-tag size="mini" type="warning">{{ row.education }}</el-tag>
              </div>
            </div>
            <div class="contact-info">
              <i class="el-icon-phone" />{{ row.phone || '未提供' }}
            </div>
            <div class="contact-info">
              <i class="el-icon-message" />{{ row.email || '未提供' }}
            </div>
            <div class="location-info">
              <i class="el-icon-location" />{{ row.currentCity || '未提供' }}
            </div>
            <div class="update-info">
              <i class="el-icon-time" />更新：{{ formatDate(row.updateTime) }}
            </div>
          </div>
        </template>
      </el-table-column>

      <el-table-column label="专业技能" min-width="180">
        <template slot-scope="{row}">
          <div class="skills-info">
            <div v-if="row.skills && row.skills.length" class="skills-tags">
              <el-tag
                v-for="skill in row.skills.slice(0, 5)"
                :key="skill.name"
                size="mini"
                type="success"
                class="skill-tag"
              >
                {{ skill.name }}
                <span class="match-rate">{{ skill.match && !isNaN(skill.match) ? Math.floor(skill.match) + '%' : '' }}</span>
              </el-tag>
              <el-tag v-if="row.skills.length > 5" size="mini" type="info">
                +{{ row.skills.length - 5 }}
              </el-tag>
            </div>
            <div v-else class="no-data">未提供技能信息</div>
          </div>
        </template>
      </el-table-column>

      <el-table-column label="工作经历" min-width="180">
        <template slot-scope="{row}">
          <div class="work-info">
            <div class="current-job">
              <div class="company">{{ row.currentCompany || '未提供' }}</div>
              <div class="position">{{ row.currentPosition || '未提供' }}</div>
            </div>
            <div class="experience-tags">
              <el-tag size="mini" type="info">{{ row.experience }}年经验</el-tag>
              <el-tag size="mini" type="info">{{ row.currentSalary || '薪资未知' }}</el-tag>
            </div>
          </div>
        </template>
      </el-table-column>

      <el-table-column label="求职意向" min-width="180">
        <template slot-scope="{row}">
          <div class="intention-info">
            <div class="intention-main">
              <div class="expected-job">
                <i class="el-icon-aim" />
                <span class="label">期望职位：</span>
                <span class="value">{{ row.expectedPosition || '未提供' }}</span>
              </div>
              <div class="expected-location">
                <i class="el-icon-map-location" />
                <span class="label">期望城市：</span>
                <span class="value">{{ row.expectedLocation || '未提供' }}</span>
              </div>
              <div class="expected-salary">
                <i class="el-icon-money" />
                <span class="label">期望薪资：</span>
                <span class="value highlight">{{ row.expectedSalary || '未提供' }}</span>
              </div>
            </div>
            <div class="status-info">
              <el-tag
                :type="row.status === 'pending' ? 'success' : 'warning'"
                size="mini"
                effect="dark"
              >
                {{ row.status === 'pending' ? '随时到岗' : row.status }}
              </el-tag>
            </div>
          </div>
        </template>
      </el-table-column>

      <el-table-column label="操作" width="220" fixed="right">
        <template slot-scope="{row}">
          <div class="action-buttons">
            <el-tooltip content="查看简历" placement="top">
              <el-button 
                type="primary" 
                size="mini" 
                plain
                class="action-btn"
                @click="viewDetail(row)"
              >
                <i class="el-icon-view" />
              </el-button>
            </el-tooltip>
            <el-tooltip content="原始简历" placement="top">
              <el-button 
                type="info" 
                size="mini" 
                plain
                class="action-btn"
                @click="previewOriginalResume(row)"
              >
                <i class="el-icon-document" />
              </el-button>
            </el-tooltip>
            <el-tooltip content="AI解读" placement="top">
              <el-button 
                type="warning" 
                size="mini"
                plain 
                class="action-btn"
                @click="aiAnalyzeResume(row)"
              >
                <i class="el-icon-cpu" />
              </el-button>
            </el-tooltip>
            <el-tooltip content="下载简历" placement="top">
              <el-button 
                type="success" 
                size="mini" 
                plain
                class="action-btn"
                @click="handleDownload(row)"
              >
                <i class="el-icon-download" />
              </el-button>
            </el-tooltip>
            <el-dropdown trigger="click" @command="(command) => handleMoreActions(command, row)">
              <el-button 
                type="primary" 
                size="mini" 
                plain
                class="action-btn"
              >
                <i class="el-icon-more" />
              </el-button>
              <el-dropdown-menu slot="dropdown">
                <el-dropdown-item command="star">
                  <i :class="row.starred ? 'el-icon-star-on' : 'el-icon-star-off'" />{{ row.starred ? '取消收藏' : '收藏简历' }}
                </el-dropdown-item>
                <el-dropdown-item command="sendInvite" divided>
                  <i class="el-icon-message" />发送面试邀请
                </el-dropdown-item>
                <el-dropdown-item command="addToPool">
                  <i class="el-icon-folder-add" />加入人才库
                </el-dropdown-item>
                <el-dropdown-item command="addNote">
                  <i class="el-icon-edit-outline" />添加备注
                </el-dropdown-item>
                <el-dropdown-item command="sendEmail">
                  <i class="el-icon-message" />发送邮件
                </el-dropdown-item>
                <el-dropdown-item command="reject" divided>
                  <i class="el-icon-close" />不合适
                </el-dropdown-item>
              </el-dropdown-menu>
            </el-dropdown>
          </div>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
export default {
  name: 'ResumeResultList',
  props: {
    resultList: {
      type: Array,
      required: true
    }
  },
  methods: {
    viewDetail(row) {
      this.$emit('view-detail', row)
    },
    previewOriginalResume(row) {
      this.$emit('preview-resume', row)
    },
    aiAnalyzeResume(row) {
      this.$emit('ai-analyze', row)
    },
    handleDownload(row) {
      this.$emit('download', row)
    },
    toggleStar(row) {
      this.$emit('toggle-star', row)
    },
    sendInterviewInvite(row) {
      this.$emit('send-invite', row)
    },
    handleMoreActions(command, row) {
      switch(command) {
        case 'star':
          this.toggleStar(row);
          break;
        case 'sendInvite':
          this.sendInterviewInvite(row);
          break;
        default:
          this.$emit('more-actions', { command, row });
      }
    },
    formatDate(date) {
      return new Date(date).toLocaleDateString()
    },
    getStatusType(status) {
      const statusMap = {
        pending: 'success',
        invited: 'warning',
        interviewed: 'primary', 
        rejected: 'danger',
        hired: 'info'
      }
      return statusMap[status] || 'info'
    },
    getStatusText(status) {
      const textMap = {
        pending: '待处理',
        invited: '已邀约',
        interviewed: '已面试',
        rejected: '不合适',
        hired: '已录用'
      }
      return textMap[status] || status
    },
    getSkillMatchType(match) {
      if (!match || isNaN(match)) return 'info'
      if (match >= 85) return 'success'
      if (match >= 70) return 'primary'
      if (match >= 60) return 'warning'
      return 'danger'
    }
  }
}
</script>

<style lang="scss" scoped>
.result-list-container {
  .resume-table {
    border: 1px solid #EBEEF5;
    border-radius: 4px;
    overflow: hidden;
    margin-top: 16px;
    
    :deep(.el-table__row) {
      &:hover {
        background-color: #f5f7fa;
      }
    }

    :deep(.el-table__header) {
      th {
        background-color: #f5f7fa;
        color: #606266;
        font-weight: 600;
        padding: 10px 0;
        text-align: center;
      }
    }

    :deep(.el-table__body) {
      td {
        padding: 12px 8px;
        vertical-align: top;
      }
    }

    ::v-deep .el-table__row {
      height: 180px;
    }

    .candidate-info {
      .primary-info {
        .name-status {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 8px;

          .name-button {
            font-size: 16px;
            font-weight: 600;
            color: #2c3e50;
            padding: 0;

            &:hover {
              color: #409EFF;
            }
          }

          .status-tag {
            font-weight: normal;
          }
        }

        .tags {
          display: flex;
          gap: 5px;
          margin-bottom: 10px;
        }
      }

      .contact-info, .location-info, .update-info {
        font-size: 13px;
        color: #606266;
        margin-top: 5px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;

        i {
          margin-right: 5px;
          color: #909399;
        }
      }
      
      .update-info {
        margin-top: 8px;
        font-style: italic;
      }
    }

    .skills-info {
      .skills-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 5px;

        .skill-tag {
          display: flex;
          align-items: center;
          margin-bottom: 5px;
          
          .match-rate {
            margin-left: 3px;
            font-weight: 600;
          }
        }
      }
      
      .no-data {
        color: #909399;
        font-size: 13px;
      }
    }

    .work-info {
      .current-job {
        margin-bottom: 8px;

        .company {
          font-weight: 500;
          color: #2c3e50;
          margin-bottom: 4px;
        }

        .position {
          color: #606266;
        }
      }

      .experience-tags {
        margin-top: 8px;
        display: flex;
        gap: 5px;
      }
    }

    .intention-info {
      .intention-main {
        > div {
          margin-bottom: 8px;
          display: flex;
          align-items: center;

          i {
            color: #909399;
            margin-right: 5px;
            width: 14px;
          }

          .label {
            color: #909399;
            margin-right: 5px;
            min-width: 70px;
          }

          .value {
            color: #2c3e50;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;

            &.highlight {
              color: #f56c6c;
              font-weight: 500;
            }
          }
        }
      }

      .status-info {
        margin-top: 10px;
        display: flex;
        align-items: center;
        justify-content: space-between;
      }
    }

    .action-buttons {
      display: flex;
      justify-content: center;
      gap: 6px;
      flex-wrap: wrap;
      
      .action-btn {
        padding: 5px 5px;
        margin: 0 1px;
        min-width: 28px;
        
        i {
          margin-right: 0;
          font-size: 14px;
        }
        
        &:hover {
          transform: translateY(-1px);
          transition: all 0.2s;
        }
      }
    }
  }

  ::v-deep .el-dropdown-menu {
    padding: 5px 0;
    
    .el-dropdown-menu__item {
      line-height: 32px;
      padding: 0 15px;
      font-size: 13px;
      
      i {
        margin-right: 8px;
      }
      
      &.divided {
        border-top: 1px solid #ebeef5;
        margin-top: 5px;
        padding-top: 5px;
      }
    }
  }
}
</style>