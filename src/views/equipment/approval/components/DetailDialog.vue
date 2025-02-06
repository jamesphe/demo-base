<template>
  <el-dialog
    title="实训设备申报详情"
    :visible.sync="visible"
    width="70%"
    :close-on-click-modal="false"
  >
    <el-card class="detail-card" shadow="never">
      <!-- 基本信息 -->
      <div class="card-header">
        <i class="el-icon-info"></i>
        <span>基本信息</span>
      </div>
      <el-row :gutter="20">
        <el-col :span="8">
          <div class="info-item">
            <span class="label">申请编号：</span>
            <span class="value">{{ detail.applyCode }}</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="info-item">
            <span class="label">项目名称：</span>
            <span class="value">{{ detail.projectName }}</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="info-item">
            <span class="label">所属部门：</span>
            <span class="value">{{ detail.department }}</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="info-item">
            <span class="label">申报年份：</span>
            <span class="value">{{ detail.year }}</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="info-item">
            <span class="label">审核状态：</span>
            <el-tag :type="detail.status | statusFilter" size="small">
              {{ detail.status | statusTextFilter }}
            </el-tag>
          </div>
        </el-col>
      </el-row>

      <!-- 设备信息 -->
      <div class="card-header" style="margin-top: 20px;">
        <i class="el-icon-cpu"></i>
        <span>设备信息</span>
      </div>
      <el-row :gutter="20">
        <el-col :span="8">
          <div class="info-item">
            <span class="label">设备型号：</span>
            <span class="value">{{ detail.model }}</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="info-item">
            <span class="label">设备价格：</span>
            <span class="value price">{{ detail.price }} 万元</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="info-item">
            <span class="label">是否招标：</span>
            <el-tag size="small" :type="detail.needBidding ? 'warning' : 'info'">
              {{ detail.needBidding ? '需要招标' : '无需招标' }}
            </el-tag>
          </div>
        </el-col>
      </el-row>

      <!-- 实训室信息 -->
      <div class="card-header" style="margin-top: 20px;">
        <i class="el-icon-office-building"></i>
        <span>实训室信息</span>
      </div>
      <el-row :gutter="20">
        <el-col :span="24">
          <div class="info-item">
            <span class="label">实训室布局：</span>
            <span class="value">{{ detail.labLayout }}</span>
          </div>
        </el-col>
      </el-row>

      <!-- 申报材料 -->
      <div class="card-header" style="margin-top: 20px;">
        <i class="el-icon-document"></i>
        <span>申报材料</span>
      </div>
      <el-row :gutter="20">
        <el-col :span="24">
          <div class="info-item">
            <span class="label">论证纪要：</span>
            <div class="value">
              <el-button 
                v-if="detail.argumentationFile"
                type="text"
                icon="el-icon-document"
                @click="handleDownload(detail.argumentationFile)"
              >
                查看论证纪要
              </el-button>
              <span v-else>未上传</span>
            </div>
          </div>
        </el-col>
        <el-col :span="24">
          <div class="info-item">
            <span class="label">申报附件：</span>
            <div class="value">
              <template v-if="detail.attachments && detail.attachments.length">
                <el-button
                  v-for="(file, index) in detail.attachments"
                  :key="index"
                  type="text"
                  icon="el-icon-document"
                  @click="handleDownload(file)"
                >
                  {{ file.name }}
                </el-button>
              </template>
              <span v-else>无附件</span>
            </div>
          </div>
        </el-col>
      </el-row>

      <!-- 审核信息 -->
      <template v-if="detail.status === 'rejected'">
        <div class="card-header" style="margin-top: 20px;">
          <i class="el-icon-warning"></i>
          <span>审核信息</span>
        </div>
        <el-row>
          <el-col :span="24">
            <div class="info-item">
              <span class="label">拒绝原因：</span>
              <span class="value reject-reason">{{ detail.rejectReason }}</span>
            </div>
          </el-col>
        </el-row>
      </template>
    </el-card>

    <div slot="footer" class="dialog-footer">
      <el-button @click="handleClose">关 闭</el-button>
      <template v-if="detail.status === 'pending'">
        <el-button type="success" @click="$emit('approve', detail)">通 过</el-button>
        <el-button type="danger" @click="$emit('reject', detail)">拒 绝</el-button>
      </template>
    </div>
  </el-dialog>
</template>

<script>
export default {
  name: 'DetailDialog',
  filters: {
    statusFilter(status) {
      const statusMap = {
        pending: 'warning',
        approved: 'success',
        rejected: 'danger'
      }
      return statusMap[status]
    },
    statusTextFilter(status) {
      const statusMap = {
        pending: '待审核',
        approved: '已通过',
        rejected: '已拒绝'
      }
      return statusMap[status]
    }
  },
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    detail: {
      type: Object,
      default: () => ({})
    }
  },
  methods: {
    handleClose() {
      this.$emit('update:visible', false)
    },
    handleDownload(file) {
      // 实现文件下载逻辑
      if (file.url) {
        window.open(file.url)
      } else {
        this.$message.warning('文件地址不存在')
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.detail-card {
  .card-header {
    font-size: 16px;
    font-weight: bold;
    margin-bottom: 20px;
    color: #303133;
    
    i {
      margin-right: 8px;
      color: #409EFF;
    }
  }

  .info-item {
    margin-bottom: 15px;
    line-height: 20px;

    .label {
      color: #909399;
      margin-right: 8px;
      display: inline-block;
      width: 84px;
    }

    .value {
      color: #303133;
      
      &.price {
        color: #F56C6C;
        font-weight: bold;
      }
    }

    .reject-reason {
      color: #F56C6C;
    }
  }
}

.el-row {
  margin-bottom: 10px;
}

.dialog-footer {
  text-align: right;
  padding-top: 20px;
}

.el-button [class*="el-icon-"] + span {
  margin-left: 5px;
}
</style>
