<template>
  <div class="user-management">
    <basic-view title="用户管理">
      <!-- 搜索和过滤区域 -->
      <div class="search-filter-container">
        <div class="filter-title">
          <i class="el-icon-search"></i>
          <span>筛选查询</span>
        </div>
        <el-form :inline="true" :model="searchForm" size="small">
          <el-form-item label="用户名">
            <el-input v-model="searchForm.username" placeholder="请输入用户名" clearable />
          </el-form-item>
          <el-form-item label="真实姓名">
            <el-input v-model="searchForm.fullName" placeholder="请输入真实姓名" clearable />
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
            <el-button type="primary" @click="handleSearch" icon="el-icon-search">搜索</el-button>
            <el-button @click="resetSearch" icon="el-icon-refresh">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 操作按钮区域 -->
      <div class="action-container">
        <el-button type="primary" @click="showAddUserModal" size="small" icon="el-icon-plus">添加用户</el-button>
        <el-button v-if="isAdmin" @click="handleBatchImport" size="small" icon="el-icon-upload2">批量导入</el-button>
        <el-button @click="handleExport" size="small" icon="el-icon-download">导出</el-button>
        <el-tooltip content="刷新数据" placement="top">
          <el-button icon="el-icon-refresh" size="small" circle @click="fetchUserList"></el-button>
        </el-tooltip>
      </div>

      <!-- 用户列表 -->
      <el-card shadow="never" class="table-card">
        <el-table
          :data="userList"
          v-loading="loading"
          border
          stripe
          highlight-current-row
          style="width: 100%"
          size="small"
        >
          <el-table-column type="index" width="50" align="center" label="#" />
          <el-table-column prop="username" label="用户名" min-width="120" />
          <el-table-column prop="full_name" label="真实姓名" min-width="120" />
          <el-table-column prop="email" label="邮箱" min-width="180" show-overflow-tooltip />
          <el-table-column prop="phone" label="手机号" min-width="120" />
          <el-table-column v-if="isAdmin" prop="tenant_name" label="所属租户" min-width="120" />
          <el-table-column label="角色" min-width="150">
            <template slot-scope="scope">
              <el-tag 
                v-for="role in scope.row.roles" 
                :key="role.id" 
                :type="roleTagType(role.name)" 
                class="role-tag" 
                size="small"
              >
                {{ role.name }}
              </el-tag>
              <span v-if="!scope.row.roles || scope.row.roles.length === 0" class="no-data">暂无角色</span>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="100" align="center">
            <template slot-scope="scope">
              <el-switch
                v-model="scope.row.is_active"
                active-color="#13ce66"
                inactive-color="#ff4949"
                @change="handleToggleStatus(scope.row)"
              ></el-switch>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" min-width="160" />
          <el-table-column label="操作" width="220" fixed="right">
            <template slot-scope="scope">
              <el-button type="text" size="small" @click="handleEdit(scope.row)" icon="el-icon-edit">编辑</el-button>
              <el-divider direction="vertical" />
              <el-button type="text" size="small" @click="handleRoleAssign(scope.row)" icon="el-icon-s-check">分配角色</el-button>
              <el-divider direction="vertical" />
              <el-popconfirm
                title="确定要删除此用户吗？"
                @confirm="handleDelete(scope.row)"
                icon="el-icon-warning"
                icon-color="red"
              >
                <el-button type="text" size="small" slot="reference" class="delete-btn" icon="el-icon-delete">删除</el-button>
              </el-popconfirm>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div class="pagination-container">
          <el-pagination
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
            :current-page="pagination.current"
            :page-sizes="[10, 20, 50, 100]"
            :page-size="pagination.pageSize"
            layout="total, sizes, prev, pager, next, jumper"
            :total="pagination.total"
            background
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
      <el-form :model="userForm" :rules="rules" ref="userFormRef" label-width="100px" size="small">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="真实姓名" prop="full_name">
          <el-input v-model="userForm.full_name" placeholder="请输入真实姓名" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" placeholder="请输入邮箱">
            <template slot="prepend">
              <i class="el-icon-message"></i>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="userForm.phone" placeholder="请输入手机号">
            <template slot="prepend">
              <i class="el-icon-mobile-phone"></i>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item v-if="!userForm.id" label="密码" prop="password">
          <el-input type="password" v-model="userForm.password" placeholder="请输入密码" show-password />
        </el-form-item>
        <el-form-item v-if="isAdmin" label="租户" prop="tenant_id">
          <el-select v-model="userForm.tenant_id" placeholder="请选择租户" style="width: 100%">
            <el-option v-for="tenant in tenants" :key="tenant.id" :value="tenant.id" :label="tenant.name" />
          </el-select>
        </el-form-item>
        <el-form-item label="角色" prop="roles">
          <el-select
            v-model="userForm.roles"
            multiple
            placeholder="请选择角色"
            style="width: 100%"
            collapse-tags
          >
            <el-option v-for="role in availableRoles" :key="role.id" :value="role.id" :label="role.name" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-switch
            v-model="userForm.is_active"
            active-text="启用"
            inactive-text="禁用"
            active-color="#13ce66"
            inactive-color="#ff4949"
          ></el-switch>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="userModalVisible = false" size="small">取 消</el-button>
        <el-button type="primary" @click="handleUserModalOk" size="small" :loading="submitLoading">确 定</el-button>
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
          <el-tag type="info" v-if="currentUser">{{ currentUser.username }}</el-tag>
          <el-tag type="success" v-if="currentUser">{{ currentUser.full_name }}</el-tag>
        </el-form-item>
        <el-form-item label="角色" prop="roles">
          <el-select
            v-model="roleForm.roles"
            multiple
            placeholder="请选择角色"
            style="width: 100%"
            collapse-tags
          >
            <el-option v-for="role in availableRoles" :key="role.id" :value="role.id" :label="role.name" />
          </el-select>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="roleModalVisible = false" size="small">取 消</el-button>
        <el-button type="primary" @click="handleRoleModalOk" size="small" :loading="submitLoading">确 定</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { Message } from 'element-ui'
import BasicView from '@/components/BasicView'

export default {
  name: 'SettingsUser',
  components: { 
    BasicView
  },
  data() {
    return {
      // 判断当前用户是否为平台管理员
      isAdmin: this.$store.getters.userRoles && this.$store.getters.userRoles.includes('admin'),
      
      // 状态数据
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
      
      // 搜索表单
      searchForm: {
        username: '',
        fullName: '',
        email: '',
        tenantId: undefined
      },
      
      // 用户表单
      userModalVisible: false,
      modalTitle: '添加用户',
      userForm: {
        id: undefined,
        username: '',
        full_name: '',
        email: '',
        phone: '',
        password: '',
        tenant_id: undefined,
        roles: [],
        is_active: true
      },
      
      // 角色分配表单
      roleModalVisible: false,
      currentUser: null,
      roleForm: {
        userId: undefined,
        roles: []
      },
      
      // 表单验证规则
      rules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' },
          { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
        ],
        full_name: [{ required: true, message: '请输入真实姓名', trigger: 'blur' }],
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
        tenant_id: [{ required: this.$store.getters.userRoles && this.$store.getters.userRoles.includes('admin'), message: '请选择租户', trigger: 'change' }]
      }
    }
  },
  methods: {
    // 获取用户列表
    async fetchUserList() {
      this.loading = true
      try {
        const params = {
          page: this.pagination.current,
          page_size: this.pagination.pageSize,
          username: this.searchForm.username || undefined,
          full_name: this.searchForm.fullName || undefined,
          email: this.searchForm.email || undefined,
          tenant_id: this.searchForm.tenantId
        }
        
        // 模拟API调用
        setTimeout(() => {
          this.userList = [
            {
              id: 1,
              username: 'admin',
              full_name: '系统管理员',
              email: 'admin@example.com',
              phone: '13800138000',
              is_active: true,
              tenant_name: '总部',
              roles: [{ id: 1, name: '管理员' }],
              created_at: '2023-01-01 00:00:00'
            },
            {
              id: 2,
              username: 'user1',
              full_name: '普通用户1',
              email: 'user1@example.com',
              phone: '13800138001',
              is_active: true,
              tenant_name: '分支机构1',
              roles: [{ id: 2, name: '普通用户' }],
              created_at: '2023-01-02 00:00:00'
            },
            {
              id: 3,
              username: 'user2',
              full_name: '普通用户2',
              email: 'user2@example.com',
              phone: '13800138002',
              is_active: false,
              tenant_name: '分支机构2',
              roles: [{ id: 3, name: '访客' }],
              created_at: '2023-01-03 00:00:00'
            }
          ]
          this.pagination.total = 3
          this.loading = false
        }, 500)
      } catch (error) {
        Message.error('获取用户列表失败')
        console.error(error)
        this.loading = false
      }
    },
    
    // 获取租户列表（仅平台管理员可见）
    async fetchTenantList() {
      if (!this.isAdmin) return
      
      try {
        // 模拟获取租户列表
        this.tenants = [
          { id: 1, name: '总部' },
          { id: 2, name: '分支机构1' },
          { id: 3, name: '分支机构2' }
        ]
      } catch (error) {
        Message.error('获取租户列表失败')
        console.error(error)
      }
    },
    
    // 获取角色列表
    async fetchRoleList() {
      try {
        // 模拟获取角色列表
        this.availableRoles = [
          { id: 1, name: '管理员' },
          { id: 2, name: '普通用户' },
          { id: 3, name: '访客' }
        ]
      } catch (error) {
        Message.error('获取角色列表失败')
        console.error(error)
      }
    },
    
    // 根据角色名称返回标签类型
    roleTagType(roleName) {
      const typeMap = {
        '管理员': 'danger',
        '普通用户': 'primary',
        '访客': 'info'
      }
      return typeMap[roleName] || 'success'
    },
    
    // 搜索
    handleSearch() {
      this.pagination.current = 1
      this.fetchUserList()
    },
    
    // 重置搜索
    resetSearch() {
      Object.keys(this.searchForm).forEach(key => {
        this.searchForm[key] = ''
      })
      this.pagination.current = 1
      this.fetchUserList()
    },
    
    // 分页处理
    handleSizeChange(size) {
      this.pagination.pageSize = size
      this.fetchUserList()
    },
    
    handleCurrentChange(current) {
      this.pagination.current = current
      this.fetchUserList()
    },
    
    // 显示添加用户弹窗
    showAddUserModal() {
      this.modalTitle = '添加用户'
      Object.keys(this.userForm).forEach(key => {
        if (key === 'roles') {
          this.userForm[key] = []
        } else if (key === 'is_active') {
          this.userForm[key] = true
        } else {
          this.userForm[key] = undefined
        }
      })
      this.userModalVisible = true
      // 在下一个事件循环中重置表单验证
      this.$nextTick(() => {
        if (this.$refs.userFormRef) {
          this.$refs.userFormRef.clearValidate()
        }
      })
    },
    
    // 编辑用户
    handleEdit(record) {
      this.modalTitle = '编辑用户'
      Object.keys(this.userForm).forEach(key => {
        if (key === 'roles') {
          this.userForm[key] = record.roles ? record.roles.map(role => role.id) : []
        } else if (key === 'password') {
          this.userForm[key] = ''
        } else {
          this.userForm[key] = record[key]
        }
      })
      this.userModalVisible = true
      // 在下一个事件循环中重置表单验证
      this.$nextTick(() => {
        if (this.$refs.userFormRef) {
          this.$refs.userFormRef.clearValidate()
        }
      })
    },
    
    // 提交用户表单
    handleUserModalOk() {
      this.$refs.userFormRef.validate(valid => {
        if (valid) {
          this.submitLoading = true
          
          // 模拟API调用
          setTimeout(() => {
            if (this.userForm.id) {
              // 更新用户
              Message.success('更新用户成功')
            } else {
              // 创建用户
              Message.success('创建用户成功')
            }
            
            this.userModalVisible = false
            this.fetchUserList()
            this.submitLoading = false
          }, 800)
        }
      })
    },
    
    // 删除用户
    handleDelete(record) {
      this.loading = true
      // 模拟API调用
      setTimeout(() => {
        Message.success('删除用户成功')
        this.fetchUserList()
      }, 500)
    },
    
    // 切换用户状态
    handleToggleStatus(record) {
      this.loading = true
      // 模拟API调用
      setTimeout(() => {
        Message.success(`${record.is_active ? '启用' : '禁用'}用户成功`)
        this.loading = false
      }, 500)
    },
    
    // 显示分配角色弹窗
    handleRoleAssign(record) {
      this.currentUser = record
      this.roleForm.userId = record.id
      this.roleForm.roles = record.roles ? record.roles.map(role => role.id) : []
      this.roleModalVisible = true
    },
    
    // 提交角色分配
    handleRoleModalOk() {
      this.submitLoading = true
      // 模拟API调用
      setTimeout(() => {
        Message.success('分配角色成功')
        this.roleModalVisible = false
        this.fetchUserList()
        this.submitLoading = false
      }, 800)
    },
    
    // 批量导入
    handleBatchImport() {
      Message.info('批量导入功能开发中')
    },
    
    // 导出
    handleExport() {
      Message.info('导出功能开发中')
    }
  },
  mounted() {
    this.fetchUserList()
    this.fetchTenantList()
    this.fetchRoleList()
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