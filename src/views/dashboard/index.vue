<template>
  <div class="dashboard-container">
    <component :is="currentRole" />
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import adminDashboard from './admin'
import tenantAdminDashboard from './tenant-admin'
import tenantUserDashboard from './tenant-user'

export default {
  name: 'Dashboard',
  components: {
    adminDashboard,
    tenantAdminDashboard,
    tenantUserDashboard
  },
  data() {
    return {
      currentRole: 'tenantUserDashboard' // 默认显示租户用户仪表盘
    }
  },
  computed: {
    ...mapGetters([
      'roles'
    ])
  },
  created() {
    // 根据角色判断显示哪个仪表盘
    if (this.roles.includes('admin')) {
      this.currentRole = 'adminDashboard'
    } else if (this.roles.includes('tenant_admin')) {
      this.currentRole = 'tenantAdminDashboard'
    }
  }
}
</script>
