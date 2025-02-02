<template>
  <div class="app-container">
    <el-card class="box-card" v-loading="loading" shadow="hover">
      <!-- 头部区域 -->
      <div slot="header" class="clearfix header-wrapper">
        <div class="left-area">
          <span class="header-title">
            <i class="el-icon-school" />
            实训室详情
          </span>
          <el-tag 
            v-if="roomDetail.status" 
            :type="roomDetail.status | statusFilter"
            class="status-tag"
          >
            {{ roomDetail.status | statusTextFilter }}
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

      <template v-if="!loading && roomDetail.id">
        <!-- 基本信息卡片 -->
        <el-card class="detail-section" shadow="never">
          <div slot="header" class="section-header">
            <i class="el-icon-info" />
            <span>基本信息</span>
          </div>
          <el-row :gutter="20">
            <el-col :span="8">
              <div class="detail-item">
                <span class="label">实训室号：</span>
                <span class="content highlight">{{ roomDetail.roomCode }}</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="detail-item">
                <span class="label">实训室名称：</span>
                <span class="content highlight">{{ roomDetail.name }}</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="detail-item">
                <span class="label">所属基地：</span>
                <span class="content">{{ roomDetail.baseName }}</span>
              </div>
            </el-col>
          </el-row>
        </el-card>

        <!-- 房间信息卡片 -->
        <el-card class="detail-section" shadow="never">
          <div slot="header" class="section-header">
            <i class="el-icon-office-building" />
            <span>房间信息</span>
          </div>
          <el-row :gutter="20">
            <el-col :span="8">
              <div class="detail-item">
                <span class="label">房间号：</span>
                <span class="content">{{ roomDetail.physicalRoomNo }}</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="detail-item">
                <span class="label">房间名称：</span>
                <span class="content">{{ roomDetail.physicalRoomName }}</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="detail-item">
                <span class="label">建立日期：</span>
                <span class="content">{{ roomDetail.establishDate }}</span>
              </div>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="8">
              <div class="detail-item">
                <span class="label">建筑面积：</span>
                <span class="content">{{ roomDetail.buildingArea }} ㎡</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="detail-item">
                <span class="label">使用面积：</span>
                <span class="content">{{ roomDetail.usableArea }} ㎡</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="detail-item">
                <span class="label">工位数：</span>
                <span class="content">{{ roomDetail.capacity }}</span>
              </div>
            </el-col>
          </el-row>
        </el-card>

        <!-- 管理信息卡片 -->
        <el-card class="detail-section" shadow="never">
          <div slot="header" class="section-header">
            <i class="el-icon-setting" />
            <span>管理信息</span>
          </div>
          <el-row :gutter="20">
            <el-col :span="8">
              <div class="detail-item">
                <span class="label">负责人工号：</span>
                <span class="content">{{ roomDetail.managerId }}</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="detail-item">
                <span class="label">设备台套数：</span>
                <span class="content">{{ roomDetail.deviceCount }}</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="detail-item">
                <span class="label">每周课时数：</span>
                <span class="content">{{ roomDetail.weeklyClassHours }}</span>
              </div>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="12">
              <div class="detail-item">
                <span class="label">合作企业：</span>
                <span class="content">{{ roomDetail.cooperativeCompany || '无' }}</span>
              </div>
            </el-col>
          </el-row>
        </el-card>

        <!-- 其他信息卡片 -->
        <el-card class="detail-section" shadow="never">
          <div slot="header" class="section-header">
            <i class="el-icon-more" />
            <span>其他信息</span>
          </div>
          <el-row>
            <el-col :span="24">
              <div class="detail-item">
                <span class="label">配套设施：</span>
                <span class="content">{{ roomDetail.facilities || '无' }}</span>
              </div>
            </el-col>
          </el-row>

          <el-row>
            <el-col :span="24">
              <div class="detail-item">
                <span class="label">备注：</span>
                <span class="content">{{ roomDetail.remark || '无' }}</span>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </template>

      <el-empty 
        v-else-if="!loading && !roomDetail.id"
        description="未找到实训室信息"
      >
        <el-button type="primary" icon="el-icon-back" @click="goBack">返回列表</el-button>
      </el-empty>
    </el-card>
  </div>
</template>

<script>
import { getTrainingRoom } from '@/api/training-room'

export default {
  name: 'TrainingRoomDetail',
  filters: {
    statusFilter(status) {
      const statusMap = {
        available: 'success',
        maintenance: 'warning',
        occupied: 'danger'
      }
      return statusMap[status]
    },
    statusTextFilter(status) {
      const statusMap = {
        available: '可用',
        maintenance: '维护中',
        occupied: '已预约'
      }
      return statusMap[status]
    }
  },
  data() {
    return {
      loading: true,
      roomDetail: {}
    }
  },
  created() {
    this.fetchData()
  },
  methods: {
    async fetchData() {
      this.loading = true
      try {
        const { data } = await getTrainingRoom(this.$route.params.id)
        if (data) {
          this.roomDetail = data
        } else {
          this.$message.warning('未找到实训室信息')
        }
      } catch (error) {
        console.error('获取实训室详情失败:', error)
        this.$message.error('获取实训室详情失败')
      } finally {
        this.loading = false
      }
    },
    goBack() {
      this.$router.push('/base/training-room')
    },
    handleEdit() {
      // 跳转到编辑页面或打开编辑弹窗
      this.$message('编辑功能开发中')
    }
  }
}
</script>

<style lang="scss" scoped>
// 添加全局变量
$primary-color: #409EFF;
$text-primary: #303133;
$text-regular: #606266;
$text-secondary: #909399;
$border-color: #DCDFE6;

// 字体大小变量
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
      font-size: $font-size-base;
    }

    &.highlight {
      color: $primary-color;
      font-weight: 600;
      font-size: $font-size-base;
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
    font-size: $font-size-base;
  }
  
  &::v-deep .el-card__body {
    padding: 20px;
    font-size: $font-size-base;
  }

  // 统一卡片内部组件字体
  &::v-deep {
    .el-tag {
      font-size: $font-size-small;
    }
    
    .el-button {
      font-size: $font-size-base;
    }
    
    .el-empty__description {
      font-size: $font-size-base;
    }
  }
}

// 响应式布局
@media screen and (max-width: 1200px) {
  .el-col {
    width: 50% !important;
  }
  
  .detail-item {
    .label {
      font-size: $font-size-base;
    }
    .content {
      font-size: $font-size-base;
    }
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
    
    .left-area {
      .header-title {
        font-size: $font-size-medium;
      }
    }
    
    .right-area {
      margin-top: 10px;
      width: 100%;
      display: flex;
      justify-content: flex-end;
      
      .el-button {
        font-size: $font-size-small;
      }
    }
  }
  
  .detail-section {
    .section-header {
      font-size: $font-size-base;
    }
  }
}
</style> 