<template>
  <div class="resume-cards">
    <div v-for="item in resultList" :key="item.id" class="resume-card">
      <div class="card-header">
        <div class="header-left">
          <span class="name" @click="viewDetail(item)">{{ item.name }}</span>
          <span :class="['gender-tag', item.gender === 'F' ? 'female' : 'male']">
            {{ item.gender === 'F' ? '女' : '男' }}
          </span>
          <span class="age-tag">{{ item.age }}岁</span>
          <el-tag size="mini" :type="getStatusType(item.status)" effect="dark" class="status-mini-tag">
            {{ getStatusText(item.status) }}
          </el-tag>
        </div>
        <div class="header-right">
          <span class="education-tag">{{ item.education }}</span>
        </div>
      </div>
      
      <div class="card-content">
        <div class="content-section">
          <div class="section-title">
            <i class="el-icon-office-building" />当前工作
          </div>
          <div class="company-info">
            <div class="company">{{ item.currentCompany || '未提供' }}</div>
            <div class="position">{{ item.currentPosition || '未提供' }}</div>
          </div>
          <div class="work-info">
            <span><i class="el-icon-time" />{{ item.experience }}年经验</span>
            <span><i class="el-icon-money" />{{ item.currentSalary || '未提供' }}</span>
          </div>
        </div>
        
        <div class="content-section">
          <div class="section-title">
            <i class="el-icon-aim" />求职意向
          </div>
          <div class="intention-info">
            <div class="info-item">
              <i class="el-icon-user" />
              {{ item.expectedPosition || '未提供' }}
            </div>
            <div class="info-item">
              <i class="el-icon-location" />
              {{ item.expectedLocation || '未提供' }}
            </div>
            <div class="info-item">
              <i class="el-icon-money" />
              {{ item.expectedSalary || '未提供' }}
            </div>
          </div>
        </div>
        
        <div class="contact-info">
          <div class="contact-item">
            <i class="el-icon-phone" />{{ item.phone || '未提供' }}
          </div>
          <div class="contact-item">
            <i class="el-icon-message" />{{ item.email || '未提供' }}
          </div>
        </div>
        
        <div class="status-bar">
          <span class="update-time">更新于：{{ formatDate(item.updateTime) }}</span>
          <span v-if="item.tags && item.tags.length > 0" class="candidate-tags">
            <el-tag v-for="tag in item.tags.slice(0, 2)" :key="tag" size="mini" type="info">{{ tag }}</el-tag>
          </span>
        </div>
      </div>
      
      <div class="card-footer">
        <el-tooltip content="查看详情" placement="top">
          <el-button type="text" @click="viewDetail(item)">
            <i class="el-icon-view" />
          </el-button>
        </el-tooltip>
        
        <el-tooltip content="预览原件" placement="top">
          <el-button type="text" @click="previewOriginalResume(item)">
            <i class="el-icon-document" />
          </el-button>
        </el-tooltip>
        
        <el-tooltip content="AI解读" placement="top">
          <el-button type="text" @click="aiAnalyzeResume(item)">
            <i class="el-icon-cpu" />
          </el-button>
        </el-tooltip>
        
        <el-tooltip content="下载简历" placement="top">
          <el-button type="text" @click="handleDownload(item)">
            <i class="el-icon-download" />
          </el-button>
        </el-tooltip>
        
        <el-tooltip :content="item.starred ? '取消收藏' : '收藏'" placement="top">
          <el-button
            type="text"
            :class="{'starred': item.starred}"
            @click="toggleStar(item)"
          >
            <i :class="item.starred ? 'el-icon-star-on' : 'el-icon-star-off'" />
          </el-button>
        </el-tooltip>
        
        <el-tooltip content="更多操作" placement="top">
          <el-dropdown trigger="click" @command="(command) => handleMoreActions(command, item)">
            <el-button type="text">
              <i class="el-icon-more" />
            </el-button>
            <el-dropdown-menu slot="dropdown">
              <el-dropdown-item command="sendInterviewInvite">
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
        </el-tooltip>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ResumeResultCard',
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
    handleMoreActions(command, row) {
      this.$emit('more-actions', { command, row })
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
    }
  }
}
</script>

<style lang="scss" scoped>
.resume-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-top: 16px;
}

.resume-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.25s ease;
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  height: 100%;

  &:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
    border-color: #e6f2ff;
  }

  .card-header {
    padding: 14px 16px;
    border-bottom: 1px solid #f0f2f5;
    background: #f9fafc;
    display: flex;
    justify-content: space-between;
    align-items: center;

    .header-left {
      display: flex;
      align-items: center;
      flex-wrap: wrap;
      gap: 6px;

      .name {
        font-size: 18px;
        font-weight: 600;
        color: #303133;
        cursor: pointer;
        transition: color 0.2s;
        max-width: 120px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;

        &:hover {
          color: #409EFF;
        }
      }

      .gender-tag {
        padding: 2px 8px;
        font-size: 13px;
        border-radius: 4px;
        line-height: 1.5;

        &.male {
          background-color: #e1f3ff;
          color: #409EFF;
        }

        &.female {
          background-color: #fde2e2;
          color: #f56c6c;
        }
      }

      .age-tag {
        padding: 2px 8px;
        font-size: 13px;
        background-color: #f0f2f5;
        color: #606266;
        border-radius: 4px;
        line-height: 1.5;
      }
    }

    .header-right {
      .education-tag {
        padding: 2px 8px;
        font-size: 13px;
        background-color: #f0f9eb;
        color: #67c23a;
        border-radius: 4px;
        font-weight: 500;
      }
    }
  }

  .card-content {
    padding: 14px 16px;
    flex: 1;
    display: flex;
    flex-direction: column;

    .content-section {
      margin-bottom: 12px;
      position: relative;

      &:last-child {
        margin-bottom: 0;
      }

      .section-title {
        font-size: 15px;
        font-weight: 600;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        font-weight: 500;

        i {
          margin-right: 4px;
          font-size: 16px;
          color: #909399;
        }
      }

      .company-info {
        margin-bottom: 6px;

        .company {
          font-size: 16px;
          font-weight: 600;
          color: #303133;
          margin-bottom: 2px;
          display: block;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .position {
          color: #606266;
          font-size: 14px;
          display: block;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
      }

      .work-info {
        display: flex;
        align-items: center;
        gap: 12px;
        color: #909399;
        font-size: 14px;

        span {
          display: flex;
          align-items: center;

          i {
            margin-right: 4px;
            font-size: 16px;
          }
        }
      }

      .intention-info {
        display: grid;
        grid-template-columns: repeat(1, 1fr);
        gap: 6px;

        .info-item {
          display: flex;
          align-items: center;
          font-size: 14px;
          color: #606266;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;

          i {
            margin-right: 4px;
            color: #909399;
            font-size: 16px;
            flex-shrink: 0;
          }
        }
      }
    }

    .contact-info {
      display: flex;
      justify-content: space-between;
      padding-top: 12px;
      margin-top: 12px;
      border-top: 1px dashed #ebeef5;

      .contact-item {
        display: flex;
        align-items: center;
        font-size: 14px;
        color: #606266;
        max-width: 45%;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;

        i {
          margin-right: 4px;
          color: #909399;
          font-size: 16px;
          flex-shrink: 0;
        }
      }
    }

    .status-bar {
      margin-top: 12px;
      display: flex;
      justify-content: space-between;
      align-items: center;

      .update-time {
        font-size: 13px;
        color: #909399;
      }

      .status-tag {
        font-size: 13px;
        font-weight: 500; 
        padding: 1px 8px;
        border-radius: 4px;
        line-height: 1.5;
      }

      .status-ready {
        background-color: #f0f9eb;
        color: #67c23a;
      }

      .status-processing {
        background-color: #ecf5ff;
        color: #409EFF;
      }
    }
  }

  .card-footer {
    padding: 10px 16px;
    border-top: 1px solid #f0f2f5;
    background: #f9fafc;
    display: flex;
    justify-content: space-around;
    gap: 8px;

    .el-button {
      padding: 0;
      font-size: 15px;
      min-width: fit-content;
      flex: 1;
      text-align: center;
      display: flex;
      align-items: center;
      justify-content: center;

      &.starred {
        color: #e6a23c;
      }

      i {
        margin-right: 4px;
        font-size: 16px;
      }
    }
  }
}

.status-mini-tag {
  font-size: 13px;
  padding: 1px 8px;
  height: 22px;
  line-height: 20px;
}

.candidate-tags {
  display: flex;
  gap: 4px;
  
  :deep(.el-tag) {
    background-color: #f5f7fa;
    color: #909399;
    border-color: #e4e7ed;
    font-size: 13px;
  }
}

.starred {
  color: #E6A23C !important;
}
</style> 