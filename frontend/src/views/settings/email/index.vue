<template>
  <div class="app-container">
    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span>邮箱同步设置</span>
        <el-button style="float: right; padding: 3px 0" type="text" @click="handleAdd">
          <i class="el-icon-plus"></i> 添加邮箱
        </el-button>
      </div>
      
      <!-- 数据表格 -->
      <el-table
        v-loading="listLoading"
        :data="emailList"
        element-loading-text="加载中..."
        border
        fit
        highlight-current-row
        style="width: 100%;"
      >
        <el-table-column align="center" label="ID" width="80">
          <template slot-scope="scope">
            {{ scope.row.id }}
          </template>
        </el-table-column>
        
        <el-table-column align="center" label="邮箱地址" min-width="150">
          <template slot-scope="scope">
            {{ scope.row.email }}
          </template>
        </el-table-column>
        
        <el-table-column align="center" label="IMAP服务器" min-width="180">
          <template slot-scope="scope">
            <template v-if="scope.row && scope.row.imap_server && scope.row.imap_server !== ''">
              {{ scope.row.imap_server }}:{{ scope.row.imap_port }}
            </template>
            <template v-else-if="scope.row && scope.row.imap_port">
              imap.126.com:{{ scope.row.imap_port }}
            </template>
            <template v-else>
              未设置
            </template>
          </template>
        </el-table-column>
        
        <el-table-column align="center" label="SMTP服务器" min-width="180">
          <template slot-scope="scope">
            <template v-if="scope.row && scope.row.smtp_server && scope.row.smtp_server !== ''">
              {{ scope.row.smtp_server }}:{{ scope.row.smtp_port }}
            </template>
            <template v-else-if="scope.row && scope.row.smtp_port">
              smtp.126.com:{{ scope.row.smtp_port }}
            </template>
            <template v-else>
              未设置
            </template>
          </template>
        </el-table-column>

        <el-table-column align="center" label="同步间隔" width="100">
          <template slot-scope="scope">
            {{ scope.row.sync_interval }} 分钟
          </template>
        </el-table-column>

        <el-table-column align="center" label="状态" width="80">
          <template slot-scope="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'info'">
              {{ scope.row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column align="center" label="上次同步时间" width="160">
          <template slot-scope="scope">
            {{ scope.row.last_sync_time ? formatDateTime(scope.row.last_sync_time) : '从未同步' }}
          </template>
        </el-table-column>
        
        <el-table-column align="center" label="操作" min-width="250">
          <template slot-scope="scope">
            <el-button
              size="mini"
              type="primary"
              @click="handleEdit(scope.$index, scope.row)"
            >编辑</el-button>
            <el-button
              size="mini"
              type="success"
              @click="handleManualSync(scope.row)"
            >同步</el-button>
            <el-button
              size="mini"
              :type="scope.row.is_active ? 'warning' : 'success'"
              @click="handleToggleStatus(scope.$index, scope.row)"
            >{{ scope.row.is_active ? '禁用' : '启用' }}</el-button>
            <el-button
              size="mini"
              type="danger"
              @click="handleDelete(scope.$index, scope.row)"
            >删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页控件 -->
      <div class="pagination-container">
        <el-pagination
          background
          layout="total, prev, pager, next"
          :total="pagination.total"
          :current-page.sync="pagination.page"
          :page-size="pagination.per_page"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 添加/编辑对话框 -->
    <el-dialog :title="dialogTitle" :visible.sync="dialogVisible" width="600px">
      <el-form ref="form" :model="form" :rules="rules" label-width="120px">
        <el-form-item label="服务商选择" v-if="!isEdit">
          <el-select v-model="selectedProvider" placeholder="请选择邮件服务商" @change="handleProviderChange" style="width: 100%">
            <el-option v-for="item in emailProviders" :key="item.value" :label="item.label" :value="item.value"></el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="邮箱地址" prop="email">
          <el-input v-model="form.email" placeholder="请输入邮箱地址"></el-input>
        </el-form-item>
        
        <el-form-item label="授权码/密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="请输入邮箱授权码（大多数邮箱需要生成授权码而非直接使用密码）"></el-input>
          <span class="form-tip">
            <i class="el-icon-info"></i> 
            大多数邮箱服务（如QQ、163、Gmail）需要使用专用授权码而非账户密码，
            <el-link type="primary" @click="showAuthCodeHelp">查看如何获取授权码</el-link>
          </span>
        </el-form-item>
        
        <el-form-item label="IMAP服务器" prop="imap_server">
          <el-input v-model="form.imap_server" placeholder="例如: imap.example.com"></el-input>
        </el-form-item>
        
        <el-form-item label="IMAP端口" prop="imap_port">
          <el-input v-model.number="form.imap_port" placeholder="默认: 993"></el-input>
        </el-form-item>
        
        <el-form-item label="SMTP服务器" prop="smtp_server">
          <el-input v-model="form.smtp_server" placeholder="例如: smtp.example.com"></el-input>
        </el-form-item>
        
        <el-form-item label="SMTP端口" prop="smtp_port">
          <el-input v-model.number="form.smtp_port" placeholder="默认: 465"></el-input>
        </el-form-item>
        
        <el-form-item label="同步间隔(分钟)" prop="sync_interval">
          <el-input v-model.number="form.sync_interval" placeholder="默认: 15"></el-input>
        </el-form-item>
        
        <el-form-item label="状态" prop="is_active">
          <el-switch v-model="form.is_active"></el-switch>
        </el-form-item>
        
        <el-form-item label="描述" prop="description">
          <el-input type="textarea" v-model="form.description" placeholder="请输入描述信息"></el-input>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click.native="handleTestConnection" :loading="testLoading">测试连接</el-button>
        </el-form-item>
      </el-form>
      
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </div>
    </el-dialog>

    <!-- 增加授权码帮助对话框 -->
    <el-dialog title="如何获取邮箱授权码" :visible.sync="authHelpVisible" width="650px">
      <div class="auth-help-content">
        <h3>为什么需要授权码？</h3>
        <p>出于安全考虑，大多数邮件服务商不再允许第三方应用直接使用账户密码登录，而是需要生成专用的授权码。</p>
        
        <el-divider></el-divider>
        
        <h3>QQ邮箱 (mail.qq.com)</h3>
        <ol>
          <li>登录网页版QQ邮箱</li>
          <li>点击"设置" > "账户"</li>
          <li>找到"POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务"</li>
          <li>开启"POP3/SMTP服务"和"IMAP/SMTP服务"</li>
          <li>点击"生成授权码"，系统会要求验证身份</li>
          <li>将生成的授权码填入本系统的"授权码/密码"字段</li>
        </ol>
        
        <el-divider></el-divider>
        
        <h3>163邮箱 (mail.163.com)</h3>
        <ol>
          <li>登录网页版163邮箱</li>
          <li>点击"设置" > "POP3/SMTP/IMAP"</li>
          <li>开启"IMAP/SMTP服务"</li>
          <li>点击"授权密码管理" > "新增授权密码"</li>
          <li>按提示完成验证后获取授权码</li>
          <li>将生成的授权码填入本系统的"授权码/密码"字段</li>
        </ol>
        
        <el-divider></el-divider>
        
        <h3>Gmail (mail.google.com)</h3>
        <ol>
          <li>访问Google账号设置 (myaccount.google.com)</li>
          <li>点击"安全性"</li>
          <li>在"登录Google"部分，开启"两步验证"</li>
          <li>然后返回安全性页面，会出现"应用专用密码"选项</li>
          <li>点击"应用专用密码" > "选择应用" > "其他" > 输入一个名称</li>
          <li>点击"生成"获取16位授权码</li>
          <li>将生成的授权码填入本系统的"授权码/密码"字段</li>
        </ol>
        
        <el-divider></el-divider>
        
        <h3>企业邮箱 (阿里/腾讯等)</h3>
        <p>请联系您的企业邮箱管理员获取第三方应用授权方式。</p>
        
        <div class="auth-help-footer">
          <p><strong>注意：</strong> 授权码通常只显示一次，请妥善保存。如更改了邮箱密码，通常需要重新生成授权码。</p>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
import { parseTime } from '@/utils'

export default {
  name: 'EmailSettings',
  data() {
    return {
      dialogVisible: false,
      dialogTitle: '添加邮箱',
      isEdit: false,
      currentIndex: -1,
      testLoading: false,
      selectedProvider: 'custom',
      authHelpVisible: false,
      emailProviders: [
        { label: '自定义', value: 'custom' },
        { label: 'Gmail', value: 'gmail' },
        { label: '163邮箱', value: '163' },
        { label: 'QQ邮箱', value: 'qq' },
        { label: '126邮箱', value: '126' },
        { label: 'Outlook', value: 'outlook' },
        { label: '新浪邮箱', value: 'sina' },
        { label: '腾讯企业邮箱', value: 'exmail' },
        { label: '阿里企业邮箱', value: 'aliyun' }
      ],
      providerConfigs: {
        gmail: {
          imap_server: 'imap.gmail.com',
          imap_port: 993,
          smtp_server: 'smtp.gmail.com',
          smtp_port: 465
        },
        '163': {
          imap_server: 'imap.163.com',
          imap_port: 993,
          smtp_server: 'smtp.163.com',
          smtp_port: 465
        },
        qq: {
          imap_server: 'imap.qq.com',
          imap_port: 993,
          smtp_server: 'smtp.qq.com',
          smtp_port: 465
        },
        '126': {
          imap_server: 'imap.126.com',
          imap_port: 993,
          smtp_server: 'smtp.126.com',
          smtp_port: 465
        },
        outlook: {
          imap_server: 'outlook.office365.com',
          imap_port: 993,
          smtp_server: 'smtp.office365.com',
          smtp_port: 587
        },
        sina: {
          imap_server: 'imap.sina.com',
          imap_port: 993,
          smtp_server: 'smtp.sina.com',
          smtp_port: 465
        },
        exmail: {
          imap_server: 'imap.exmail.qq.com',
          imap_port: 993,
          smtp_server: 'smtp.exmail.qq.com',
          smtp_port: 465
        },
        aliyun: {
          imap_server: 'imap.aliyun.com',
          imap_port: 993,
          smtp_server: 'smtp.aliyun.com',
          smtp_port: 465
        },
        custom: {
          imap_server: '',
          imap_port: 993,
          smtp_server: '',
          smtp_port: 465
        }
      },
      form: {
        email: '',
        password: '',
        imap_server: '',
        imap_port: 993,
        smtp_server: '',
        smtp_port: 465,
        is_active: true,
        sync_interval: 15,
        description: ''
      },
      rules: {
        email: [
          { required: true, message: '请输入邮箱地址', trigger: 'blur' },
          { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' }
        ],
        imap_server: [
          { required: true, message: '请输入IMAP服务器', trigger: 'blur' }
        ],
        smtp_server: [
          { required: true, message: '请输入SMTP服务器', trigger: 'blur' }
        ]
      }
    }
  },
  computed: {
    ...mapGetters('resume-sync-email', [
      'emailList',
      'loading',
      'pagination'
    ]),
    // 列表加载状态
    listLoading() {
      return this.loading
    }
  },
  created() {
    this.getList()
  },
  mounted() {
    // 开发调试: 打印邮箱数据
    console.log('当前邮箱列表数据:', this.emailList)
    // 添加监听
    this.$watch('emailList', (newVal) => {
      console.log('邮箱列表更新:', newVal)
      if (newVal && newVal.length > 0) {
        console.log('第一条数据:', newVal[0])
        console.log('IMAP服务器:', newVal[0].imap_server)
        console.log('IMAP端口:', newVal[0].imap_port)
        console.log('SMTP服务器:', newVal[0].smtp_server)
        console.log('SMTP端口:', newVal[0].smtp_port)
      }
    }, { immediate: true, deep: true })
  },
  methods: {
    ...mapActions('resume-sync-email', [
      'getEmailList',
      'createEmail',
      'updateEmail',
      'deleteEmail',
      'triggerSync',
      'testConnection'
    ]),
    formatDateTime(time) {
      if (!time) return '从未同步';
      
      try {
        // 检查日期是否有效
        const date = new Date(time);
        if (isNaN(date.getTime())) {
          console.error('无效的日期:', time);
          // 尝试从ISO格式字符串中提取日期部分
          if (typeof time === 'string') {
            const matched = time.match(/(\d{4}-\d{2}-\d{2})[T\s](\d{2}:\d{2}:\d{2})/);
            if (matched) {
              return `${matched[1]} ${matched[2]}`;
            }
          }
          return '日期无效';
        }
        
        // 使用直接的日期格式化显示
        const year = date.getFullYear();
        const month = (date.getMonth() + 1).toString().padStart(2, '0');
        const day = date.getDate().toString().padStart(2, '0');
        const hours = date.getHours().toString().padStart(2, '0');
        const minutes = date.getMinutes().toString().padStart(2, '0');
        const seconds = date.getSeconds().toString().padStart(2, '0');
        
        return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
      } catch (error) {
        console.error('日期格式化错误:', error, time);
        return '格式化错误';
      }
    },
    // 获取邮箱列表
    async getList(page = 1) {
      try {
        await this.getEmailList({ 
          page, 
          per_page: this.pagination.per_page 
        })
      } catch (error) {
        this.$message.error('获取邮箱列表失败')
      }
    },
    resetForm() {
      this.selectedProvider = 'custom'
      this.form = {
        email: '',
        password: '',
        imap_server: '',
        imap_port: 993,
        smtp_server: '',
        smtp_port: 465,
        is_active: true,
        sync_interval: 15,
        description: ''
      }
    },
    handleProviderChange(provider) {
      if (provider && this.providerConfigs[provider]) {
        const config = this.providerConfigs[provider]
        this.form.imap_server = config.imap_server
        this.form.imap_port = config.imap_port
        this.form.smtp_server = config.smtp_server
        this.form.smtp_port = config.smtp_port
        
        // 为邮箱地址自动添加后缀
        if (provider !== 'custom') {
          const email = this.form.email || ''
          const atIndex = email.indexOf('@')
          const username = atIndex > -1 ? email.substring(0, atIndex) : email
          
          switch(provider) {
            case 'gmail':
              this.form.email = username ? `${username}@gmail.com` : ''
              break
            case '163':
              this.form.email = username ? `${username}@163.com` : ''
              break
            case 'qq':
              this.form.email = username ? `${username}@qq.com` : ''
              break
            case '126':
              this.form.email = username ? `${username}@126.com` : ''
              break
            case 'outlook':
              this.form.email = username ? `${username}@outlook.com` : ''
              break
            case 'sina':
              this.form.email = username ? `${username}@sina.com` : ''
              break
            case 'exmail':
              // 腾讯企业邮箱需要用户自行输入完整邮箱地址
              break
            case 'aliyun':
              // 阿里企业邮箱需要用户自行输入完整邮箱地址
              break
          }
        }
      }
    },
    handleAdd() {
      this.resetForm()
      this.dialogTitle = '添加邮箱'
      this.isEdit = false
      this.dialogVisible = true
    },
    handleEdit(index, row) {
      this.currentIndex = index
      this.form = { ...row, password: '******' } // 出于安全考虑，不显示真实密码
      this.dialogTitle = '编辑邮箱'
      this.isEdit = true
      this.dialogVisible = true
    },
    async handleToggleStatus(index, row) {
      try {
        const status = !row.is_active
        const message = status ? '启用' : '禁用'
        
        await this.updateEmail({ 
          id: row.id, 
          data: { ...row, is_active: status }
        })
        
        this.$message.success(`${message}成功`)
      } catch (error) {
        console.error('切换状态失败', error)
        this.$message.error('操作失败')
      }
    },
    async handleDelete(index, row) {
      this.$confirm('此操作将永久删除该邮箱配置, 是否继续?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        try {
          await this.deleteEmail(row.id)
          this.$message.success('删除成功')
        } catch (error) {
          console.error('删除失败', error)
          this.$message.error('删除失败')
        }
      }).catch(() => {
        this.$message.info('已取消删除')
      })
    },
    async handleManualSync(row) {
      try {
        this.$message.info('开始同步，请稍候...')
        await this.triggerSync(row.id)
        this.$message.success('同步任务已提交，请稍后查看结果')
        // 延迟3秒后刷新列表
        setTimeout(() => {
          this.getList()
        }, 3000)
      } catch (error) {
        console.error('同步失败', error)
        this.$message.error('同步失败')
      }
    },
    async handleSubmit() {
      this.$refs.form.validate(async valid => {
        if (valid) {
          try {
            if (this.isEdit) {
              // 如果密码是占位符，则不更新密码
              const payload = { ...this.form }
              if (payload.password === '******') {
                delete payload.password
              }
              
              await this.updateEmail({ 
                id: this.form.id, 
                data: payload 
              })
              
              this.$message.success('更新成功')
            } else {
              await this.createEmail(this.form)
              this.$message.success('添加成功')
            }
            
            this.dialogVisible = false
            this.getList() // 刷新列表
          } catch (error) {
            console.error('保存失败', error)
            this.$message.error('保存失败')
          }
        } else {
          console.log('表单验证失败')
          return false
        }
      })
    },
    async handleTestConnection() {
      console.log('handleTestConnection 被调用')
      try {
        // 表单验证
        this.$refs.form.validate(valid => {
          console.log('表单验证结果:', valid)
          if (!valid) {
            console.log('测试连接前表单验证失败')
            this.$message.error('请先完成表单填写')
            return false
          }
          
          // 在验证成功的回调中执行测试
          this.doTestConnection()
          return true
        })
      } catch (err) {
        console.error('验证表单时出错:', err)
        this.$message.error('验证表单时出错')
      }
    },
    
    async doTestConnection() {
      console.log('开始执行测试连接...')
      this.testLoading = true
      try {
        // 构建测试连接的参数对象
        const testParams = {
          email: this.form.email,
          password: this.form.password,
          imap_server: this.form.imap_server,
          imap_port: this.form.imap_port,
          smtp_server: this.form.smtp_server,
          smtp_port: this.form.smtp_port
        }
        
        console.log('测试连接参数:', testParams)
        
        // 如果是编辑模式且密码是占位符，不发送密码
        if (this.isEdit && testParams.password === '******') {
          delete testParams.password
          // 添加ID用于后端获取存储的密码
          testParams.id = this.form.id
          console.log('编辑模式，使用ID获取密码:', this.form.id)
        }
        
        const { success, message } = await this.testConnection(testParams)
        
        // 使用解析后的结果
        if (success === true) {
          this.$message.success('连接测试成功!')
        } else {
          this.$message.error(`连接测试失败: ${message}`)
        }
      } catch (error) {
        console.error('测试连接发生错误:', error)
        this.$message.error(`测试连接失败: ${error.message || '网络错误'}`)
      } finally {
        this.testLoading = false
      }
    },
    showAuthCodeHelp() {
      this.authHelpVisible = true
    },
    // 处理分页变化
    handlePageChange(page) {
      this.getList(page)
    }
  }
}
</script>

<style scoped>
.filter-container {
  padding-bottom: 10px;
}

.form-tip {
  margin-left: 10px;
  font-size: 0.8em;
  color: #909399;
}

.pagination-container {
  margin-top: 20px;
  text-align: center;
}

.auth-help-content {
  line-height: 1.6;
}

.auth-help-content h3 {
  margin-top: 10px;
  margin-bottom: 10px;
  color: #303133;
}

.auth-help-content ol {
  padding-left: 20px;
  margin-bottom: 10px;
}

.auth-help-content ol li {
  margin-bottom: 5px;
}

.auth-help-footer {
  margin-top: 20px;
  padding: 10px;
  background-color: #f8f8f8;
  border-radius: 4px;
}
</style> 