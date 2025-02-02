<template>
  <div class="app-container">
    <el-card class="box-card" v-loading="loading" shadow="hover">
      <!-- 头部区域 -->
      <div slot="header" class="clearfix header-wrapper">
        <div class="left-area">
          <span class="header-title">
            <i class="el-icon-cpu" />
            设备详情
          </span>
          <el-tag 
            :type="equipmentDetail.status | statusFilter"
            class="status-tag"
          >
            {{ equipmentDetail.status | statusTextFilter }}
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

      <template v-if="!loading && equipmentDetail.id">
        <!-- 基本信息卡片 -->
        <el-card class="detail-section" shadow="never">
          <div slot="header" class="section-header">
            <i class="el-icon-info" />
            <span>基本信息</span>
          </div>
          <el-row :gutter="20">
            <el-col :span="8">
              <div class="detail-item">
                <span class="label">设备编号：</span>
                <span class="content highlight">{{ equipmentDetail.equipmentCode }}</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="detail-item">
                <span class="label">设备名称：</span>
                <span class="content highlight">{{ equipmentDetail.name }}</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="detail-item">
                <span class="label">设备型号：</span>
                <span class="content">{{ equipmentDetail.model }}</span>
              </div>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="8">
              <div class="detail-item">
                <span class="label">所属实训室：</span>
                <span class="content">{{ equipmentDetail.roomName }}</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="detail-item">
                <span class="label">负责人：</span>
                <span class="content">{{ equipmentDetail.manager }}</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="detail-item">
                <span class="label">购置日期：</span>
                <span class="content">{{ equipmentDetail.purchaseDate }}</span>
              </div>
            </el-col>
          </el-row>
        </el-card>

        <!-- 价格信息卡片 -->
        <el-card class="detail-section" shadow="never">
          <div slot="header" class="section-header">
            <i class="el-icon-money" />
            <span>价格信息</span>
          </div>
          <el-row :gutter="20">
            <el-col :span="8">
              <div class="detail-item">
                <span class="label">单价：</span>
                <span class="content">¥ {{ equipmentDetail.price.toFixed(2) }}</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="detail-item">
                <span class="label">数量：</span>
                <span class="content">{{ equipmentDetail.quantity }}</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="detail-item">
                <span class="label">购买年限：</span>
                <span class="content">{{ equipmentDetail.lifespan }} 年</span>
              </div>
            </el-col>
          </el-row>
        </el-card>

        <!-- 供应商信息卡片 -->
        <el-card class="detail-section" shadow="never">
          <div slot="header" class="section-header">
            <i class="el-icon-office-building" />
            <span>供应商信息</span>
          </div>
          <el-row :gutter="20">
            <el-col :span="12">
              <div class="detail-item">
                <span class="label">供应商：</span>
                <span class="content">{{ equipmentDetail.supplier }}</span>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="detail-item">
                <span class="label">生产厂家：</span>
                <span class="content">{{ equipmentDetail.manufacturer }}</span>
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
                <span class="label">备注：</span>
                <span class="content">{{ equipmentDetail.remark || '无' }}</span>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </template>

      <template v-if="!loading && !equipmentDetail.id" class="empty-state">
        <div class="el-empty">
          <div class="el-empty__image" style="width: 160px;">
            <img src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTg0IiBoZWlnaHQ9IjE1MiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KICA8ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPgogICAgPGcgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoMjQgMzEuNjcpIj4KICAgICAgPGVsbGlwc2UgZmlsbC1vcGFjaXR5PSIuOCIgZmlsbD0iI0Y1RjVGNSIgY3g9IjY3Ljc5NyIgY3k9IjEwNi44OSIgcng9IjY3Ljc5NyIgcnk9IjEyLjY2OCIvPgogICAgICA8cGF0aCBkPSJNMTIyLjAzNCA2OS42NzRMOTguMTA5IDQwLjIyOWMtMS4xNDgtMS4zODYtMi44MjYtMi4yMjUtNC41OTMtMi4yMjVoLTUxLjQ0Yy0xLjc2NiAwLTMuNDQ0LjgzOS00LjU5MiAyLjIyNUwxMy41NiA2OS42NzR2MTUuMzgzaDEwOC40NzVWNjkuNjc0eiIgZmlsbD0iI0FFQjhDMiIvPgogICAgICA8cGF0aCBkPSJNMTAxLjUzNyA4Ni4yMTRMODAuNjMgNjEuMTAyYy0xLjAwMS0xLjIwNy0yLjUwNy0xLjg2Ny00LjA0OC0xLjg2N0gzMS43MjRjLTEuNTQgMC0zLjA0Ny42Ni00LjA0OCAxLjg2N0w2Ljc2OSA4Ni4yMTR2MTMuNzkyaDk0Ljc2OFY4Ni4yMTR6IiBmaWxsPSJ1cmwoI2xpbmVhckdyYWRpZW50LTEpIiB0cmFuc2Zvcm09InRyYW5zbGF0ZSgxMy41NikiLz4KICAgICAgPHBhdGggZD0iTTMzLjgzIDBoNjcuOTMzYTQgNCAwIDAgMSA0IDR2OTMuMzQ0YTQgNCAwIDAgMS00IDRIMzMuODNhNCA0IDAgMCAxLTQtNFY0YTQgNCAwIDAgMSA0LTR6IiBmaWxsPSIjRjVGNUY1Ii8+CiAgICAgIDxwYXRoIGQ9Ik00Mi42NzggOS45NTNoNTAuMjM3YTIgMiAwIDAgMSAyIDJWMzYuOTFhMiAyIDAgMCAxLTIgMkg0Mi42NzhhMiAyIDAgMCAxLTItMlYxMS45NTNhMiAyIDAgMCAxIDItMnpNNDIuOTQgNDkuNzY3aDQ5LjcxM2EyLjI2MiAyLjI2MiAwIDEgMSAwIDQuNTI0SDQyLjk0YTIuMjYyIDIuMjYyIDAgMCAxIDAtNC41MjR6TTQyLjk0IDYxLjUzaDQ5LjcxM2EyLjI2MiAyLjI2MiAwIDEgMSAwIDQuNTI1SDQyLjk0YTIuMjYyIDIuMjYyIDAgMCAxIDAtNC41MjV6TTEyMS44MTMgMTA1LjAzMmMtLjc3NSAzLjA3MS0zLjQ5NyA1LjM2LTYuNzM1IDUuMzZIMjAuNTE1Yy0zLjIzOCAwLTUuOTYtMi4yOS02LjczNC01LjM2YTcuMzA5IDcuMzA5IDAgMCAxLS4yMjItMS43OVY2OS42NzVoMjYuMzE4YzIuOTA3IDAgNS4yNSAyLjQ0OCA1LjI1IDUuNDJ2LjA0YzAgMi45NzEgMi4zNyA1LjM3IDUuMjc3IDUuMzdoMzQuNzg1YzIuOTA3IDAgNS4yNzctMi40MjEgNS4yNzctNS4zOTNWNzUuMWMwLTIuOTcyIDIuMzQzLTUuNDI2IDUuMjUtNS40MjZoMjYuMzE4djMzLjU2OWMwIC42MTctLjA3NyAxLjIxNi0uMjIxIDEuNzg5eiIgZmlsbD0iI0RDRTBFNiIvPgogICAgPC9nPgogICAgPHBhdGggZD0iTTE0OS4xMjEgMzMuMjkybC02LjgzIDIuNjVhMSAxIDAgMCAxLTEuMzE3LTEuMjNsMS45MzctNi4yMDdjLTIuNTg5LTIuOTQ0LTQuMTA5LTYuNTM0LTQuMTA5LTEwLjQwOEMxMzguODAyIDguMTAyIDE0OC45MiAwIDE2MS40MDIgMCAxNzMuODgxIDAgMTg0IDguMTAyIDE4NCAxOC4wOTdjMCA5Ljk5NS0xMC4xMTggMTguMDk3LTIyLjU5OSAxOC4wOTctNC41MjggMC04Ljc0NC0xLjA2Ni0xMi4yOC0yLjkwMnoiIGZpbGw9IiNEQ0UwRTYiLz4KICAgIDxnIHRyYW5zZm9ybT0idHJhbnNsYXRlKDE0OS42NSAxNS4zODMpIiBmaWxsPSIjRkZGIj4KICAgICAgPGVsbGlwc2UgY3g9IjIwLjY1NCIgY3k9IjMuMTY3IiByeD0iMi44NDkiIHJ5PSIyLjgxNSIvPgogICAgICA8cGF0aCBkPSJNNS42OTggNS42M0gwTDIuODk4LjcwNHpNOS4yNTkuNzA0aDQuOTg1VjUuNjNIOS4yNTl6Ii8+CiAgICA8L2c+CiAgPC9nPgo8L3N2Zz4K">
          </div>
          <div class="el-empty__description">
            <p>未找到设备信息</p>
          </div>
          <div class="el-empty__bottom">
            <el-button type="primary" @click="goBack">
              返回列表
            </el-button>
          </div>
        </div>
      </template>
    </el-card>
  </div>
</template>

<script>
import { getEquipmentDetail } from '@/api/equipment'

export default {
  name: 'EquipmentDetail',
  filters: {
    statusFilter(status) {
      const statusMap = {
        normal: 'success',
        maintenance: 'warning',
        scrapped: 'danger'
      }
      return statusMap[status]
    },
    statusTextFilter(status) {
      const statusMap = {
        normal: '正常',
        maintenance: '维修中',
        scrapped: '已报废'
      }
      return statusMap[status]
    }
  },
  data() {
    return {
      loading: true,
      equipmentDetail: {}
    }
  },
  created() {
    this.fetchData()
  },
  methods: {
    async fetchData() {
      this.loading = true
      try {
        const id = parseInt(this.$route.params.id)
        if (!id) {
          this.$message.error('无效的设备ID')
          return
        }
        const { data } = await getEquipmentDetail(id)
        if (data) {
          this.equipmentDetail = data
        } else {
          this.$message.warning('未找到设备信息')
        }
      } catch (error) {
        console.error('获取设备详情失败:', error)
        this.$message.error('获取设备详情失败')
      } finally {
        this.loading = false
      }
    },
    goBack() {
      this.$router.push('/equipment/info')
    },
    handleEdit() {
      // TODO: 跳转到编辑页面或打开编辑弹窗
      this.$message('编辑功能开发中')
    }
  }
}
</script>

<style lang="scss" scoped>
// 样式变量定义
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
    }
  }

  .right-area {
    .el-button {
      margin-left: 10px;
    }
  }
}

.detail-section {
  margin-bottom: 20px;

  .section-header {
    font-size: $font-size-medium;
    font-weight: 600;
    color: $text-primary;
    
    i {
      margin-right: 8px;
      color: $primary-color;
    }
  }

  &:last-child {
    margin-bottom: 0;
  }
}

.detail-item {
  margin-bottom: 20px;
  line-height: 24px;
  
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

.empty-state {
  padding: 40px 0;
  text-align: center;

  .el-empty {
    padding: 40px 0;
    
    &__image {
      width: 160px;
      margin: 0 auto;
      
      img {
        width: 100%;
        height: 100%;
        vertical-align: top;
      }
    }
    
    &__description {
      margin-top: 20px;
      
      p {
        margin: 0;
        font-size: 14px;
        color: #909399;
      }
    }
    
    &__bottom {
      margin-top: 20px;
    }
  }
}
</style> 