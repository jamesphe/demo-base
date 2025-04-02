<template>
  <el-card class="trial-management">
    <div slot="header" class="clearfix">
      <span>试用申请管理</span>
      <el-button style="float: right; padding: 3px 0" type="text" @click="refreshData">
        刷新
      </el-button>
    </div>

    <el-table
      v-loading="loading"
      :data="trialList"
      style="width: 100%"
      :header-cell-style="{background:'#f5f7fa'}"
    >
      <el-table-column
        prop="company"
        label="申请企业"
      />

      <el-table-column
        prop="contact"
        label="联系人"
        width="100"
      />

      <el-table-column
        prop="applyTime"
        label="申请时间"
        width="180"
      />

      <el-table-column
        prop="status"
        label="状态"
        width="100"
      >
        <template slot-scope="{row}">
          <el-tag :type="getStatusType(row.status)">
            {{ getStatusText(row.status) }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column
        label="操作"
        width="150"
        align="center"
      >
        <template slot-scope="{row}">
          <el-button
            v-if="row.status === 'pending'"
            size="mini"
            type="text"
            @click="handleApprove(row)"
          >
            审批
          </el-button>
          <el-button
            v-if="row.status === 'approved'"
            size="mini"
            type="text"
            @click="handleSetup(row)"
          >
            配置
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<script>
export default {
  name: 'TrialManagement',
  data() {
    return {
      loading: false,
      trialList: [
        {
          company: '创新科技有限公司',
          contact: '张三',
          applyTime: '2024-03-21 09:30:00',
          status: 'pending'
        },
        {
          company: '未来科技有限公司',
          contact: '李四',
          applyTime: '2024-03-20 15:20:00',
          status: 'approved'
        }
      ]
    }
  },
  methods: {
    refreshData() {
      this.loading = true
      // TODO: 调用API获取最新数据
      setTimeout(() => {
        this.loading = false
      }, 800)
    },
    getStatusType(status) {
      const typeMap = {
        pending: 'warning',
        approved: 'success',
        rejected: 'danger'
      }
      return typeMap[status]
    },
    getStatusText(status) {
      const textMap = {
        pending: '待审批',
        approved: '已通过',
        rejected: '已拒绝'
      }
      return textMap[status]
    },
    handleApprove(trial) {
      // TODO: 实现审批逻辑
    },
    handleSetup(trial) {
      // TODO: 跳转到试用租户配置页面
    }
  }
}
</script>
