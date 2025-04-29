<template>
  <div>
    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span>职位匹配关键词设置</span>
        <el-button style="float: right; padding: 3px 0" type="text" @click="handleAdd">
          <i class="el-icon-plus"></i> 添加关键词
        </el-button>
      </div>
      
      <!-- 数据表格 -->
      <el-table
        v-loading="listLoading"
        :data="keywordList"
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
        
        <el-table-column align="center" label="职位" min-width="120">
          <template slot-scope="scope">
            {{ scope.row.job_title || '未知职位' }}
          </template>
        </el-table-column>
        
        <el-table-column align="center" label="关键词" min-width="120">
          <template slot-scope="scope">
            {{ scope.row.keyword }}
          </template>
        </el-table-column>
        
        <el-table-column align="center" label="描述" min-width="150">
          <template slot-scope="scope">
            {{ scope.row.description || '-' }}
          </template>
        </el-table-column>
        
        <el-table-column align="center" label="操作" width="150">
          <template slot-scope="scope">
            <el-button
              size="mini"
              type="primary"
              @click="handleEdit(scope.$index, scope.row)"
            >编辑</el-button>
            <el-button
              size="mini"
              type="danger"
              @click="handleDelete(scope.$index, scope.row)"
            >删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 添加/编辑对话框 -->
    <el-dialog :title="dialogTitle" :visible.sync="dialogVisible" width="500px">
      <el-form ref="form" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="职位" prop="job_id">
          <el-select v-model="form.job_id" placeholder="请选择职位" filterable>
            <el-option
              v-for="item in jobOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            ></el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="关键词" prop="keyword">
          <el-input v-model="form.keyword" placeholder="请输入匹配关键词"></el-input>
        </el-form-item>
        
        <el-form-item label="描述" prop="description">
          <el-input type="textarea" v-model="form.description" placeholder="请输入描述信息"></el-input>
        </el-form-item>
      </el-form>
      
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
import { getPositionList } from '@/api/position'

export default {
  name: 'EmailKeywords',
  props: {
    emailId: {
      type: [Number, String],
      required: true
    }
  },
  data() {
    return {
      jobOptions: [],
      dialogVisible: false,
      dialogTitle: '添加关键词',
      isEdit: false,
      currentIndex: -1,
      form: {
        job_id: undefined,
        keyword: '',
        description: ''
      },
      rules: {
        job_id: [
          { required: true, message: '请选择职位', trigger: 'change' }
        ],
        keyword: [
          { required: true, message: '请输入关键词', trigger: 'blur' }
        ]
      }
    }
  },
  computed: {
    ...mapGetters('resume-sync-email', [
      'keywords',
      'loading'
    ]),
    keywordList() {
      return this.keywords
    },
    listLoading() {
      return this.loading
    }
  },
  created() {
    this.getKeywords(this.emailId).catch(error => {
      this.$message.error('获取关键词列表失败')
    })
    this.getJobs()
  },
  methods: {
    ...mapActions('resume-sync-email', [
      'getKeywords',
      'createKeyword',
      'updateKeyword',
      'deleteKeyword'
    ]),
    async getJobs() {
      try {
        const { data } = await getPositionList({ status: 'active' })
        this.jobOptions = data.map(job => ({
          label: job.title,
          value: job.id
        }))
      } catch (error) {
        console.error('获取职位列表失败', error)
        this.$message.error('获取职位列表失败')
      }
    },
    resetForm() {
      this.form = {
        job_id: undefined,
        keyword: '',
        description: ''
      }
    },
    handleAdd() {
      this.resetForm()
      this.dialogTitle = '添加关键词'
      this.isEdit = false
      this.dialogVisible = true
    },
    handleEdit(index, row) {
      this.currentIndex = index
      this.form = { ...row }
      this.dialogTitle = '编辑关键词'
      this.isEdit = true
      this.dialogVisible = true
    },
    async handleDelete(index, row) {
      this.$confirm('此操作将永久删除该关键词, 是否继续?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        try {
          await this.deleteKeyword({ 
            emailId: this.emailId, 
            keywordId: row.id 
          })
          this.$message.success('删除成功')
        } catch (error) {
          console.error('删除失败', error)
          this.$message.error('删除失败')
        }
      }).catch(() => {
        this.$message.info('已取消删除')
      })
    },
    async handleSubmit() {
      this.$refs.form.validate(async valid => {
        if (valid) {
          try {
            if (this.isEdit) {
              await this.updateKeyword({
                emailId: this.emailId,
                keywordId: this.form.id,
                data: this.form
              })
              
              this.$message.success('更新成功')
            } else {
              await this.createKeyword({
                emailId: this.emailId,
                data: this.form
              })
              
              this.$message.success('添加成功')
            }
            
            this.dialogVisible = false
          } catch (error) {
            console.error('保存失败', error)
            this.$message.error('保存失败')
          }
        } else {
          console.log('表单验证失败')
          return false
        }
      })
    }
  }
}
</script>

<style scoped>
.filter-container {
  padding-bottom: 10px;
}
</style> 