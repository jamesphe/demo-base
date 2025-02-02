<template>
  <div class="app-container">
    <el-card class="box-card" v-loading="loading" shadow="hover">
      <!-- 头部区域 -->
      <div slot="header" class="clearfix header-wrapper">
        <div class="left-area">
          <span class="header-title">
            <i class="el-icon-notebook-2" />
            实训项目详情
          </span>
          <el-tag 
            v-if="projectDetail.isVirtual" 
            type="success"
            class="status-tag"
          >
            虚拟仿真项目
          </el-tag>
        </div>
        <div class="right-area">
          <el-button type="warning" icon="el-icon-edit" @click="handleEdit">
            编辑
          </el-button>
          <el-button type="primary" icon="el-icon-back" @click="goBack">
            返回列表
          </el-button>
        </div>
      </div>

      <template v-if="!loading && projectDetail.id">
        <!-- 基本信息卡片 -->
        <el-card class="detail-section" shadow="never">
          <div slot="header" class="section-header">
            <i class="el-icon-info" />
            <span>基本信息</span>
          </div>
          <el-row :gutter="20">
            <el-col :span="8">
              <div class="detail-item">
                <span class="label">项目编号：</span>
                <span class="content highlight">{{ projectDetail.projectCode }}</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="detail-item">
                <span class="label">项目名称：</span>
                <span class="content highlight">{{ projectDetail.name }}</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="detail-item">
                <span class="label">计划课程号：</span>
                <span class="content">{{ projectDetail.courseCode }}</span>
              </div>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="8">
              <div class="detail-item">
                <span class="label">归口专业号：</span>
                <span class="content">{{ projectDetail.majorCode }}</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="detail-item">
                <span class="label">归口专业：</span>
                <span class="content">{{ projectDetail.majorName }}</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="detail-item">
                <span class="label">对外服务：</span>
                <el-tag :type="projectDetail.isExternalService ? 'success' : 'info'" size="small">
                  {{ projectDetail.isExternalService ? '是' : '否' }}
                </el-tag>
              </div>
            </el-col>
          </el-row>
        </el-card>

        <!-- 项目内容卡片 -->
        <el-card class="detail-section" shadow="never">
          <div slot="header" class="section-header">
            <i class="el-icon-document" />
            <span>项目内容</span>
          </div>
          <el-row>
            <el-col :span="24">
              <div class="detail-item">
                <span class="label">配套实训资源：</span>
                <span class="content">{{ projectDetail.trainingResources || '无' }}</span>
              </div>
            </el-col>
          </el-row>

          <el-row>
            <el-col :span="24">
              <div class="detail-item">
                <span class="label">典型任务名称：</span>
                <div class="content content-block">{{ projectDetail.typicalTasks || '无' }}</div>
              </div>
            </el-col>
          </el-row>

          <el-row>
            <el-col :span="24">
              <div class="detail-item">
                <span class="label">技能要求：</span>
                <div class="content content-block">{{ projectDetail.skillRequirements || '无' }}</div>
              </div>
            </el-col>
          </el-row>

          <el-row>
            <el-col :span="24">
              <div class="detail-item">
                <span class="label">考核方式：</span>
                <div class="content content-block">{{ projectDetail.assessmentMethod || '无' }}</div>
              </div>
            </el-col>
          </el-row>
        </el-card>

        <!-- 实训安排卡片 -->
        <el-card class="detail-section" shadow="never">
          <div slot="header" class="section-header">
            <i class="el-icon-date" />
            <span>实训安排</span>
          </div>
          <el-row :gutter="20">
            <el-col :span="8">
              <div class="detail-item">
                <span class="label">模块数量：</span>
                <span class="content">{{ projectDetail.moduleCount }}</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="detail-item">
                <span class="label">实训课时：</span>
                <span class="content">{{ projectDetail.trainingHours }}</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="detail-item">
                <span class="label">学年学期：</span>
                <span class="content">{{ projectDetail.academicYear }} 第{{ projectDetail.semester }}学期</span>
              </div>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="12">
              <div class="detail-item">
                <span class="label">校内实训室：</span>
                <span class="content">{{ projectDetail.trainingRoomCode || '无' }}</span>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="detail-item">
                <span class="label">其他实训地点：</span>
                <span class="content">{{ projectDetail.otherTrainingLocations || '无' }}</span>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </template>

      <el-empty 
        v-else-if="!loading && !projectDetail.id"
        description="未找到项目信息"
      >
        <el-button type="primary" icon="el-icon-back" @click="goBack">返回列表</el-button>
      </el-empty>
    </el-card>
  </div>
</template>

<script>
import { getTrainingProject } from '@/api/training-project'

export default {
  name: 'TrainingProjectDetail',
  data() {
    return {
      loading: true,
      projectDetail: {}
    }
  },
  created() {
    this.fetchData()
  },
  methods: {
    async fetchData() {
      this.loading = true
      try {
        const { data } = await getTrainingProject(parseInt(this.$route.params.id))
        if (data) {
          this.projectDetail = data
        } else {
          this.$message.warning('未找到项目信息')
        }
      } catch (error) {
        console.error('获取项目详情失败:', error)
        this.$message.error('获取项目详情失败')
      } finally {
        this.loading = false
      }
    },
    goBack() {
      this.$router.push('/base/training-project')
    },
    handleEdit() {
      // TODO: 跳转到编辑页面或打开编辑弹窗
      this.$message('编辑功能开发中')
    }
  }
}
</script>

<style lang="scss" scoped>
// 使用与实训室详情页相同的样式变量
$primary-color: #409EFF;
$text-primary: #303133;
$text-regular: #606266;
$text-secondary: #909399;
$border-color: #DCDFE6;

$font-size-large: 18px;
$font-size-medium: 16px;
$font-size-base: 14px;
$font-size-small: 13px;

.header-wrapper {
  display: flex;
  justify-content: space-between;
  align-items: center;

  .left-area {
    display: flex;
    align-items: center;
    
    .header-title {
      font-size: $font-size-large;
      font-weight: 600;
      margin-right: 15px;
      color: $text-primary;
      
      i {
        margin-right: 8px;
        font-size: 20px;
        color: $primary-color;
      }
    }

    .status-tag {
      margin-left: 10px;
      font-size: $font-size-small;
    }
  }

  .right-area {
    .el-button {
      margin-left: 10px;
      font-size: $font-size-base;
    }
  }
}

.detail-section {
  margin-bottom: 20px;
  border-radius: 8px;
  
  &:last-child {
    margin-bottom: 0;
  }

  .section-header {
    font-size: $font-size-medium;
    font-weight: 600;
    color: $text-primary;
    
    i {
      margin-right: 8px;
      color: $primary-color;
    }
  }
}

.detail-item {
  margin-bottom: 20px;
  line-height: 24px;
  font-size: $font-size-base;
  
  &:last-child {
    margin-bottom: 0;
  }
  
  .label {
    display: inline-block;
    min-width: 100px;
    color: $text-secondary;
    font-weight: 500;
  }
  
  .content {
    color: $text-regular;
    
    &:empty::after {
      content: '暂无';
      color: $text-secondary;
      font-style: italic;
    }

    &.highlight {
      color: $primary-color;
      font-weight: 600;
    }

    &.content-block {
      white-space: pre-line;
      padding: 8px 12px;
      background-color: #f8f9fa;
      border-radius: 4px;
      margin-top: 4px;
    }
  }
}

.el-card {
  border-radius: 8px;
  transition: all 0.3s;
  
  &.box-card {
    margin-bottom: 20px;
  }
  
  &::v-deep .el-card__header {
    padding: 15px 20px;
    border-bottom: 1px solid $border-color;
  }
  
  &::v-deep .el-card__body {
    padding: 20px;
  }
}

// 响应式布局
@media screen and (max-width: 1200px) {
  .el-col {
    width: 50% !important;
  }
}

@media screen and (max-width: 768px) {
  .el-col {
    width: 100% !important;
  }
  
  .detail-item {
    margin-bottom: 15px;
    
    .label {
      min-width: 90px;
      font-size: $font-size-small;
    }
    
    .content {
      font-size: $font-size-small;
    }
  }
  
  .header-wrapper {
    flex-direction: column;
    align-items: flex-start;
    
    .right-area {
      margin-top: 10px;
      width: 100%;
      display: flex;
      justify-content: flex-end;
    }
  }
}
</style> 