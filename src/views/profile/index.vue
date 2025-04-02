<template>
  <div class="app-container">
    <div v-if="user">
      <el-row :gutter="20">
        <el-col :span="6" :xs="24">
          <user-card :user="user" />
          <el-card class="role-card">
            <div slot="header">
              <span>角色权限</span>
            </div>
            <div class="role-tags">
              <el-tag
                v-for="role in userRoles"
                :key="role.id"
                :type="role.type"
                class="role-tag"
              >
                {{ role.name }}
              </el-tag>
            </div>
          </el-card>
        </el-col>

        <el-col :span="18" :xs="24">
          <el-card>
            <el-tabs v-model="activeTab">
              <el-tab-pane label="基本信息" name="basic">
                <basic-info :user="user" />
              </el-tab-pane>

              <el-tab-pane label="安全设置" name="security">
                <security-settings :user="user" />
              </el-tab-pane>

              <el-tab-pane
                v-if="isTenantUser"
                label="企业信息"
                name="company"
              >
                <company-info :user="user" />
              </el-tab-pane>

              <el-tab-pane label="操作日志" name="logs">
                <operation-logs :user="user" />
              </el-tab-pane>
            </el-tabs>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import UserCard from './components/UserCard'
import BasicInfo from './components/BasicInfo'
import SecuritySettings from './components/SecuritySettings'
import CompanyInfo from './components/CompanyInfo'
import OperationLogs from './components/OperationLogs'

export default {
  name: 'Profile',
  components: {
    UserCard,
    BasicInfo,
    SecuritySettings,
    CompanyInfo,
    OperationLogs
  },
  data() {
    return {
      user: {},
      activeTab: 'basic',
      userRoles: [
        { id: 1, name: '平台管理员', type: 'danger' },
        { id: 2, name: '数据审核员', type: 'warning' }
      ]
    }
  },
  computed: {
    ...mapGetters([
      'name',
      'avatar',
      'roles'
    ]),
    isTenantUser() {
      return this.roles.includes('tenant_admin') || this.roles.includes('tenant_hr')
    }
  },
  created() {
    this.getUser()
  },
  methods: {
    getUser() {
      this.user = {
        name: this.name,
        role: this.roles.join(' | '),
        email: 'admin@test.com',
        avatar: this.avatar,
        phone: '13800138000',
        department: '技术部',
        position: '系统管理员',
        lastLoginTime: '2024-03-31 10:30:00',
        lastLoginIp: '192.168.1.100'
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.role-card {
  margin-top: 20px;
  .role-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    .role-tag {
      margin-right: 5px;
      margin-bottom: 5px;
    }
  }
}

.el-card {
  margin-bottom: 20px;
}

@media (max-width: 768px) {
  .el-col {
    margin-bottom: 20px;
  }
}
</style>
