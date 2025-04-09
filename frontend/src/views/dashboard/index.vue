<template>
  <div>
    <!-- 根据角色显示不同的仪表盘 -->
    <admin-dashboard v-if="isAdmin" />
    <tenant-admin-dashboard v-else-if="isTenantAdmin" />
    <tenant-user-dashboard v-else-if="isTenantUser" />
    <editor-dashboard v-else-if="isEditor" />
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import AdminDashboard from './admin'
import TenantAdminDashboard from './tenant-admin'
import TenantUserDashboard from './tenant-user'
import EditorDashboard from './editor'

export default {
  name: 'Dashboard',
  components: {
    AdminDashboard,
    TenantAdminDashboard,
    TenantUserDashboard,
    EditorDashboard
  },
  computed: {
    ...mapGetters([
      'roles'
    ]),
    // 判断用户角色
    isAdmin() {
      return this.roles.includes('admin')
    },
    isTenantAdmin() {
      return this.roles.includes('tenant_admin')
    },
    isTenantUser() {
      return this.roles.includes('tenant_user')
    },
    isEditor() {
      return this.roles.includes('editor')
    }
  }
}
</script>

<style lang="scss" scoped>
.dashboard-container {
  padding: 20px;

  .dashboard-header {
    margin-bottom: 20px;

    h2 {
      margin-bottom: 20px;
      font-weight: 500;
      color: #303133;
    }
  }

  .stat-item {
    display: flex;
    align-items: center;
    padding: 10px;

    .stat-icon {
      font-size: 48px;
      color: #409EFF;
      margin-right: 20px;
    }

    .stat-info {
      .stat-value {
        font-size: 24px;
        font-weight: bold;
        color: #303133;
      }

      .stat-label {
        font-size: 14px;
        color: #909399;
        margin-top: 5px;
      }
    }
  }

  .chart-card {
    margin-bottom: 20px;

    .chart-placeholder {
      height: 300px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: #f5f7fa;
      color: #909399;
    }
  }

  .recent-activities {
    .activity-list {
      .activity-item {
        display: flex;
        align-items: center;
        padding: 12px 0;
        border-bottom: 1px solid #EBEEF5;

        &:last-child {
          border-bottom: none;
        }

        .activity-icon {
          font-size: 20px;
          color: #409EFF;
          margin-right: 12px;
        }

        .activity-content {
          flex: 1;

          .activity-title {
            font-size: 14px;
            color: #303133;
          }

          .activity-time {
            font-size: 12px;
            color: #909399;
            margin-top: 4px;
          }
        }
      }
    }
  }
}
</style>
