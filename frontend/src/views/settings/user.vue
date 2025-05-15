<template>
  <div class="user-management">
    <basic-view title="用户管理">
      <!-- 搜索和过滤区域 -->
      <div class="search-filter-container">
        <div class="filter-title">
          <i class="el-icon-search" />
          <span>筛选查询</span>
        </div>
        <el-form :inline="true" :model="searchForm" size="small">
          <el-form-item label="用户名">
            <el-input v-model="searchForm.username" placeholder="请输入用户名" clearable />
          </el-form-item>
          <el-form-item label="邮箱">
            <el-input v-model="searchForm.email" placeholder="请输入邮箱" clearable />
          </el-form-item>
          <el-form-item v-if="isAdmin" label="租户">
            <el-select v-model="searchForm.tenantId" placeholder="请选择租户" clearable style="width: 200px">
              <el-option v-for="tenant in tenants" :key="tenant.id" :value="tenant.id" :label="tenant.name" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" icon="el-icon-search" @click="handleSearch">搜索</el-button>
            <el-button icon="el-icon-refresh" @click="resetSearch">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 操作按钮区域 -->
      <div class="action-container">
        <el-button type="primary" size="small" icon="el-icon-plus" @click="showAddUserModal">添加用户</el-button>
        <el-button v-if="isAdmin" size="small" icon="el-icon-upload2" @click="handleBatchImport">批量导入</el-button>
        <el-button size="small" icon="el-icon-download" @click="handleExport">导出</el-button>
        <el-tooltip content="刷新数据" placement="top">
          <el-button icon="el-icon-refresh" size="small" circle @click="fetchUserList" />
        </el-tooltip>
      </div>

      <!-- 用户列表 -->
      <el-card shadow="never" class="table-card">
        <el-table
          v-loading="loading"
          :data="userList"
          border
          stripe
          highlight-current-row
          style="width: 100%"
          size="small"
        >
          <el-table-column type="index" width="50" align="center" label="#" />
          <el-table-column prop="username" label="用户名" min-width="120" />
          <el-table-column prop="email" label="邮箱" min-width="180" show-overflow-tooltip />
          <el-table-column prop="phone" label="手机号" min-width="120" />
          <el-table-column v-if="isAdmin" prop="tenantName" label="所属租户" min-width="120" />
          <el-table-column label="角色" min-width="150">
            <template slot-scope="scope">
              <el-tag
                v-for="roleName in scope.row.roleNames"
                :key="roleName"
                :type="roleTagType(roleName)"
                class="role-tag"
                size="small"
              >
                {{ roleName }}
              </el-tag>
              <span v-if="!scope.row.roleNames || scope.row.roleNames.length === 0" class="no-data">暂无角色</span>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="100" align="center">
            <template slot-scope="scope">
              <el-switch
                v-model="scope.row.isActive"
                active-color="#13ce66"
                inactive-color="#ff4949"
                @change="handleToggleStatus(scope.row)"
              />
            </template>
          </el-table-column>
          <el-table-column prop="createdAt" label="创建时间" min-width="160" />
          <el-table-column label="操作" width="220" fixed="right">
            <template slot-scope="scope">
              <el-button type="text" size="small" icon="el-icon-edit" @click="handleEdit(scope.row)">编辑</el-button>
              <el-divider direction="vertical" />
              <el-button type="text" size="small" icon="el-icon-s-check" @click="handleRoleAssign(scope.row)">分配角色</el-button>
              <el-divider direction="vertical" />
              <el-popconfirm
                title="确定要删除此用户吗？"
                icon="el-icon-warning"
                icon-color="red"
                @confirm="handleDelete(scope.row)"
              >
                <el-button slot="reference" type="text" size="small" class="delete-btn" icon="el-icon-delete">删除</el-button>
              </el-popconfirm>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div class="pagination-container">
          <el-pagination
            :current-page="pagination.current"
            :page-sizes="[10, 20, 50, 100]"
            :page-size="pagination.pageSize"
            layout="total, sizes, prev, pager, next, jumper"
            :total="pagination.total"
            background
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </el-card>
    </basic-view>

    <!-- 添加/编辑用户弹窗 -->
    <el-dialog
      :title="modalTitle"
      :visible.sync="userModalVisible"
      width="600px"
      :close-on-click-modal="false"
      :destroy-on-close="true"
    >
      <el-form ref="userFormRef" :model="userForm" :rules="rules" label-width="100px" size="small">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" placeholder="请输入邮箱">
            <template slot="prepend">
              <i class="el-icon-message" />
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="userForm.phone" placeholder="请输入手机号">
            <template slot="prepend">
              <i class="el-icon-mobile-phone" />
            </template>
          </el-input>
        </el-form-item>
        <el-form-item v-if="!userForm.id" label="密码" prop="password">
          <el-input v-model="userForm.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        <el-form-item v-if="isAdmin" label="租户" prop="tenantId">
          <el-select
            v-model="userForm.tenantId"
            placeholder="请选择租户"
            style="width: 100%"
            value-key="id"
            @change="handleTenantChange"
          >
            <el-option
              v-for="tenant in tenants"
              :key="tenant.id"
              :value="tenant.id.toString()"
              :label="tenant.name"
            />
          </el-select>
        </el-form-item>
        <!-- 角色选择部分可能导致问题，注释掉 -->
        <!-- <el-form-item label="角色" prop="roles">
          <el-select
            v-model="userForm.roles"
            multiple
            placeholder="请选择角色"
            style="width: 100%"
            collapse-tags
          >
            <el-option v-for="role in availableRoles" :key="role.id" :value="role.id" :label="role.name" />
          </el-select>
        </el-form-item> -->
        <el-form-item label="状态">
          <el-switch
            v-model="userForm.isActive"
            active-text="启用"
            inactive-text="禁用"
            active-color="#13ce66"
            inactive-color="#ff4949"
          />
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button size="small" @click="userModalVisible = false">取 消</el-button>
        <el-button type="primary" size="small" :loading="submitLoading" @click="handleUserModalOk">确 定</el-button>
      </div>
    </el-dialog>

    <!-- 分配角色弹窗 -->
    <el-dialog
      title="分配角色"
      :visible.sync="roleModalVisible"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form :model="roleForm" label-width="100px" size="small">
        <el-form-item label="用户">
          <el-tag v-if="currentUser" type="info">{{ currentUser.username }}</el-tag>
          <el-tag v-if="currentUser" type="success">{{ currentUser.full_name }}</el-tag>
        </el-form-item>
        <el-form-item label="角色" prop="roles">
          <el-select
            v-model="roleForm.roles"
            multiple
            placeholder="请选择角色"
            style="width: 100%"
            collapse-tags
          >
            <el-option
              v-for="role in availableRoles"
              :key="role.id"
              :value="role.id"
              :label="role.name"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button size="small" @click="roleModalVisible = false">取 消</el-button>
        <el-button type="primary" size="small" :loading="submitLoading" @click="handleRoleModalOk">确 定</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { Message } from 'element-ui'
import BasicView from '@/components/BasicView'
import {
  getUserList,
  createUser,
  updateUser,
  deleteUser,
  updateUserRoles,
  getRoleList
} from '@/api/system/user'
import { getTenantList } from '@/api/tenant'

export default {
  name: 'SettingsUser',
  components: {
    BasicView
  },
  data() {
    return {
      isAdmin: false,
      loading: false,
      submitLoading: false,
      userList: [],
      tenants: [],
      availableRoles: [],
      pagination: {
        current: 1,
        pageSize: 10,
        total: 0
      },

      searchForm: {
        username: '',
        email: '',
        tenantId: undefined
      },

      userModalVisible: false,
      modalTitle: '添加用户',
      userForm: {
        id: undefined,
        username: '',
        email: '',
        phone: '',
        password: '',
        tenantId: undefined,
        roles: [],
        isActive: true,
        user_type: 'tenant'
      },

      roleModalVisible: false,
      currentUser: null,
      roleForm: {
        userId: undefined,
        roles: []
      },

      rules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' },
          { min: 2, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
        ],
        email: [
          { required: true, message: '请输入邮箱', trigger: 'blur' },
          { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' },
          { min: 6, message: '密码长度不能小于6个字符', trigger: 'blur' }
        ],
        phone: [
          { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
        ],
        tenantId: [
          { required: this.$store.getters.userRoles && this.$store.getters.userRoles.includes('admin'), message: '请选择租户', trigger: 'change' },
          { type: 'string', transform: (value) => value?.toString(), message: '租户ID必须是字符串类型', trigger: 'change' }
        ]
      }
    }
  },
  mounted() {
    this.checkAdminStatus()
    this.fetchUserList()
    this.fetchTenantList()
    this.fetchRoleList()
  },
  methods: {
    checkAdminStatus() {
      const userRoles = this.$store.getters.userRoles
      this.isAdmin = userRoles && userRoles.includes('admin') && !userRoles.includes('tenant_admin')
    },

    async fetchUserList() {
      this.loading = true
      try {
        const params = {
          keyword: this.searchForm.username || this.searchForm.email || '',
          tenant_id: this.searchForm.tenantId,
          page: this.pagination.current,
          page_size: this.pagination.pageSize
        }

        const { data } = await getUserList(params)
        this.userList = data.map(user => ({
          ...user,
          roles: user.roles || [],
          roleNames: user.roles?.map(role => role.name) || []
        }))
        this.pagination.total = data.length
      } catch (error) {
        Message.error('获取用户列表失败')
        console.error(error)
      } finally {
        this.loading = false
      }
    },

    async fetchTenantList() {
      if (!this.isAdmin) {
        console.log('当前用户不是超级管理员，跳过获取租户列表')
        return
      }

      try {
        const { data } = await getTenantList({ page: 1, limit: 100 })
        console.log('获取到的租户数据:', data)

        this.tenants = data.map(tenant => ({
          id: tenant.id,
          name: tenant.tenantName
        }))
        if (this.userForm.tenantId) {
          this.userForm.tenantId = this.userForm.tenantId.toString()
        }
        console.log('处理后的租户列表:', this.tenants)
      } catch (error) {
        console.error('获取租户列表失败:', error)
        Message.error('获取租户列表失败')
      }
    },

    async fetchRoleList() {
      try {
        const { data } = await getRoleList()
        console.log('获取到的角色列表:', data)
        
        // 根据用户权限过滤可用角色
        if (this.isAdmin) {
          // 超级管理员可以看到所有角色
          this.availableRoles = data.map(role => ({
            id: role.id,
            name: role.description || role.name // 优先使用description，如果没有则使用name
          }))
        } else {
          // 租户管理员可以分配租户用户、HR和面试官角色
          const allowedRoles = ['tenant_user', 'hr', 'interviewer']
          this.availableRoles = data.filter(role => 
            allowedRoles.includes(role.name)
          ).map(role => ({
            id: role.id,
            name: role.description || role.name // 优先使用description，如果没有则使用name
          }))
        }
        
        console.log('处理后的角色列表:', this.availableRoles)
      } catch (error) {
        console.error('获取角色列表失败:', error)
        Message.error('获取角色列表失败')
      }
    },

    getRoleName(roleId) {
      const role = this.availableRoles.find(r => r.id === roleId)
      return role ? role.name : '未知角色'
    },

    roleTagType(roleName) {
      const typeMap = {
        '管理员': 'danger',
        '人力资源': 'success',
        '面试官': 'warning',
        '租户管理员': 'danger',
        '租户用户': 'info'
      }
      return typeMap[roleName] || 'primary'
    },

    handleSearch() {
      this.pagination.current = 1
      this.fetchUserList()
    },

    resetSearch() {
      Object.keys(this.searchForm).forEach(key => {
        this.searchForm[key] = ''
      })
      this.pagination.current = 1
      this.fetchUserList()
    },

    handleSizeChange(size) {
      this.pagination.pageSize = size
      this.fetchUserList()
    },

    handleCurrentChange(current) {
      this.pagination.current = current
      this.fetchUserList()
    },

    showAddUserModal() {
      this.modalTitle = '添加用户'
      Object.keys(this.userForm).forEach(key => {
        if (key === 'roles') {
          this.userForm[key] = []
        } else if (key === 'isActive') {
          this.userForm[key] = true
        } else {
          this.userForm[key] = undefined
        }
      })
      this.userForm.user_type = 'tenant'
      this.userModalVisible = true
      this.$nextTick(() => {
        if (this.$refs.userFormRef) {
          this.$refs.userFormRef.clearValidate()
        }
      })
    },

    handleEdit(record) {
      this.modalTitle = '编辑用户'
      console.log('编辑前的用户数据:', record)

      this.userForm = {
        id: record.id,
        username: record.username,
        email: record.email,
        phone: record.phone,
        tenantId: record.tenantId?.toString(),
        roles: record.roles || [],
        isActive: record.isActive
      }
      console.log('设置到表单的数据:', this.userForm)
      this.userModalVisible = true
    },

    async handleUserModalOk() {
      console.log('提交前的表单数据:', this.userForm)
      console.log('租户ID类型:', typeof this.userForm.tenantId)

      this.$refs.userFormRef.validate(async(valid, fields) => {
        console.log('表单验证结果:', valid)
        console.log('验证失败字段:', fields)

        if (valid) {
          this.submitLoading = true
          try {
            const formData = {
              ...this.userForm,
              tenantId: this.userForm.tenantId?.toString(),
              user_type: this.userForm.user_type || 'tenant'
            }

            console.log('准备提交的数据:', formData)
            console.log('用户类型:', formData.user_type)

            if (this.userForm.id) {
              await updateUser(this.userForm.id, formData)
              Message.success('更新用户成功')
            } else {
              await createUser(formData)
              Message.success('创建用户成功')
            }

            this.userModalVisible = false
            this.fetchUserList()
          } catch (error) {
            console.error('API错误详情:', error.response?.data)
            Message.error(error.response?.data?.detail || '操作失败')
          } finally {
            this.submitLoading = false
          }
        }
      })
    },

    async handleDelete(row) {
      try {
        await deleteUser(row.id)
        Message.success('删除用户成功')
        this.fetchUserList()
      } catch (error) {
        Message.error(error.response?.data?.detail || '删除失败')
      }
    },

    async handleToggleStatus(row) {
      const targetStatus = !row.isActive
      try {
        await updateUser(row.id, {
          isActive: targetStatus
        })
        this.$set(row, 'isActive', targetStatus)
        this.$message.success(`${targetStatus ? '启用' : '禁用'}用户成功`)
      } catch (error) {
        this.$set(row, 'isActive', !targetStatus)
        this.$message.error(error.response?.data?.detail || '操作失败')
      }
    },

    handleRoleAssign(row) {
      this.currentUser = row
      this.roleForm.userId = row.id

      // 确保使用角色ID数组，并转换为数字类型
      this.roleForm.roles = Array.isArray(row.roles)
        ? row.roles.map(role => Number(role.id))
        : []

      console.log('角色分配 - 处理后数据:', {
        userId: this.roleForm.userId,
        roles: this.roleForm.roles,
        rolesType: typeof this.roleForm.roles,
        isArray: Array.isArray(this.roleForm.roles)
      })

      this.roleModalVisible = true
    },

    async handleRoleModalOk() {
      console.log('提交角色数据:', {
        formData: this.roleForm,
        roles: this.roleForm.roles,
        rolesType: typeof this.roleForm.roles,
        isArray: Array.isArray(this.roleForm.roles)
      })

      this.submitLoading = true
      try {
        // 确保发送的是数字数组
        const roleIds = Array.isArray(this.roleForm.roles)
          ? this.roleForm.roles.map(id => Number(id))
          : []

        console.log('准备发送到API的数据:', {
          userId: this.roleForm.userId,
          roleIds,
          roleIdsType: typeof roleIds,
          isArray: Array.isArray(roleIds)
        })

        await updateUserRoles(this.roleForm.userId, roleIds)
        this.$message.success('分配角色成功')
        this.roleModalVisible = false
        this.fetchUserList()
      } catch (error) {
        console.error('分配角色失败:', error.response?.data)
        console.error('错误详情:', {
          status: error.response?.status,
          statusText: error.response?.statusText,
          data: error.response?.data
        })
        this.$message.error(error.response?.data?.message || '分配角色失败')
      } finally {
        this.submitLoading = false
      }
    },

    handleBatchImport() {
      Message.info('批量导入功能开发中')
    },

    handleExport() {
      Message.info('导出功能开发中')
    },

    handleTenantChange(value) {
      this.userForm.tenantId = value?.toString()
      console.log('租户选择改变:', {
        value,
        type: typeof value,
        formTenantId: this.userForm.tenantId,
        formTenantIdType: typeof this.userForm.tenantId
      })
    }
  }
}
</script>

<style scoped>
.user-management {
  width: 100%;
}

.search-filter-container {
  margin-bottom: 20px;
  padding: 18px 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.filter-title {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 15px;
  display: flex;
  align-items: center;
}

.filter-title i {
  margin-right: 8px;
  color: #409EFF;
}

.action-container {
  margin-bottom: 16px;
  display: flex;
  justify-content: flex-start;
  align-items: center;
}

.table-card {
  margin-bottom: 20px;
}

.pagination-container {
  margin-top: 20px;
  text-align: right;
}

.role-tag {
  margin-right: 5px;
  margin-bottom: 5px;
}

.delete-btn {
  color: #F56C6C;
}

.no-data {
  color: #909399;
  font-size: 12px;
}

.el-divider--vertical {
  margin: 0 5px;
}

/* 表格内容垂直居中 */
.el-table .cell {
  display: flex;
  align-items: center;
}

/* 角色标签容器 */
.el-table .cell .role-tag {
  display: inline-block;
}
</style>
