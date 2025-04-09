<template>
  <div class="app-container">
    <el-form ref="form" :model="positionForm" :rules="rules" label-width="120px" class="position-form">
      <el-card class="box-card">
        <div slot="header" class="card-header">
          <span>基本信息</span>
          <small class="text-muted">请填写职位基本信息</small>
        </div>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="职位名称" prop="title">
              <el-input v-model="positionForm.title" placeholder="请输入职位名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="职位类型" prop="job_type">
              <el-select v-model="positionForm.job_type" placeholder="请选择职位类型" style="width: 100%">
                <el-option label="全职" value="fulltime" />
                <el-option label="兼职" value="parttime" />
                <el-option label="实习" value="intern" />
                <el-option label="外包" value="outsource" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="所属部门" prop="department">
              <el-input v-model="positionForm.department" placeholder="请输入所属部门" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="招聘人数" prop="headcount">
              <el-input-number v-model="positionForm.headcount" :min="1" :max="999" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="工作地点" prop="location">
          <el-input
            v-model="positionForm.location"
            placeholder="请输入工作地点，如: 北京市朝阳区望京SOHO"
            :maxlength="255"
            show-word-limit
          />
        </el-form-item>
      </el-card>

      <el-card class="box-card">
        <div slot="header" class="card-header">
          <span>薪资福利</span>
          <small class="text-muted">请设置薪资范围和福利待遇</small>
        </div>

        <el-form-item label="薪资范围" prop="salary" class="salary-range">
          <el-col :span="8">
            <el-input-number
              v-model="positionForm.salary_min"
              :min="1"
              :step="1"
              controls-position="right"
              placeholder="最低薪资"
            />
          </el-col>
          <el-col :span="1" class="salary-separator">
            <span>至</span>
          </el-col>
          <el-col :span="8">
            <el-input-number
              v-model="positionForm.salary_max"
              :min="positionForm.salary_min || 1"
              :step="1"
              controls-position="right"
              placeholder="最高薪资"
            />
          </el-col>
          <el-col :span="6" :offset="1">
            <el-select v-model="positionForm.salary_type" style="width: 100%">
              <el-option label="月薪" value="month" />
              <el-option label="年薪" value="year" />
              <el-option label="面议" value="negotiate" />
            </el-select>
          </el-col>
        </el-form-item>

        <el-form-item label="薪资构成" prop="salary_structure">
          <el-input
            v-model="positionForm.salary_structure"
            type="textarea"
            placeholder="例如：基本工资 + 绩效奖金 + 年终奖"
            :rows="2"
          />
        </el-form-item>

        <el-form-item label="福利待遇" prop="benefits">
          <el-checkbox-group v-model="positionForm.benefits" class="benefit-group">
            <el-checkbox label="五险一金">五险一金</el-checkbox>
            <el-checkbox label="年终奖">年终奖</el-checkbox>
            <el-checkbox label="加班补助">加班补助</el-checkbox>
            <el-checkbox label="餐补">餐补</el-checkbox>
            <el-checkbox label="交通补助">交通补助</el-checkbox>
            <el-checkbox label="通讯补贴">通讯补贴</el-checkbox>
            <el-checkbox label="节日福利">节日福利</el-checkbox>
            <el-checkbox label="带薪年假">带薪年假</el-checkbox>
            <el-checkbox label="定期体检">定期体检</el-checkbox>
            <el-checkbox label="员工旅游">员工旅游</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
      </el-card>

      <el-card class="box-card">
        <div slot="header" class="card-header">
          <span>要求与职责</span>
          <small class="text-muted">请详细描述职位要求与职责</small>
        </div>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="学历要求" prop="education_required">
              <el-select v-model="positionForm.education_required" style="width: 100%">
                <el-option label="不限" value="none" />
                <el-option label="大专" value="college" />
                <el-option label="本科" value="bachelor" />
                <el-option label="硕士" value="master" />
                <el-option label="博士" value="doctor" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="工作经验" prop="experience_required">
              <el-select v-model="positionForm.experience_required" style="width: 100%">
                <el-option label="经验不限" value="none" />
                <el-option label="应届生" value="fresh" />
                <el-option label="1年以下" value="0-1" />
                <el-option label="1-3年" value="1-3" />
                <el-option label="3-5年" value="3-5" />
                <el-option label="5-10年" value="5-10" />
                <el-option label="10年以上" value="10+" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="职位描述" prop="description">
          <el-input
            v-model="positionForm.description"
            type="textarea"
            :rows="6"
            placeholder="请详细描述该职位的主要工作内容、职责范围等"
          />
        </el-form-item>

        <el-form-item label="任职要求" prop="requirements">
          <el-input
            v-model="positionForm.requirements"
            type="textarea"
            :rows="6"
            placeholder="请详细描述该职位的任职要求，如专业技能、语言要求、性格特征等"
          />
        </el-form-item>

        <el-form-item label="加分项" prop="preferences">
          <el-input
            v-model="positionForm.preferences"
            type="textarea"
            :rows="4"
            placeholder="请描述可以加分的条件（选填）"
          />
        </el-form-item>
      </el-card>

      <div class="form-footer">
        <el-button icon="el-icon-refresh-left" @click="resetForm">
          重置表单
        </el-button>
        <el-button type="primary" icon="el-icon-check" @click="submitForm">
          发布职位
        </el-button>
      </div>
    </el-form>
  </div>
</template>

<script>
// eslint-disable-next-line no-unused-vars
import { mapGetters } from 'vuex'

export default {
  name: 'PositionPublish',
  data() {
    // 自定义验证器：验证最高薪资必须大于最低薪资
    const validateSalary = (rule, value, callback) => {
      if (this.positionForm.salary_type === 'negotiate') {
        callback()
      } else if (this.positionForm.salary_max && this.positionForm.salary_min) {
        if (this.positionForm.salary_max < this.positionForm.salary_min) {
          callback(new Error('最高薪资不能低于最低薪资'))
        } else {
          callback()
        }
      } else {
        callback()
      }
    }

    return {
      positionForm: {
        title: '高级前端开发工程师',
        job_type: 'fulltime',
        department: '技术部',
        headcount: 2,
        location: '北京市朝阳区望京SOHO T1座',
        salary_min: 25,
        salary_max: 35,
        salary_type: 'month',
        salary_structure: '基本工资(15K) + 绩效奖金(5K) + 年终奖(2-3个月) + 项目奖金',
        benefits: ['五险一金', '年终奖', '加班补助', '餐补', '定期体检', '带薪年假'],
        education_required: 'bachelor',
        experience_required: '3-5',
        description: `岗位职责：
1. 负责公司前端项目的架构设计和开发工作；
2. 负责前端技术选型，制定并规范团队开发规范；
3. 负责项目性能优化，提升用户体验；
4. 研究和引入新的前端技术，提升团队技术能力；
5. 参与项目技术评审，解决项目开发过程中的技术难题；
6. 指导初级工程师，促进团队技术成长。`,
        requirements: `任职要求：
1. 本科及以上学历，计算机相关专业；
2. 3年以上前端开发经验，有大型项目经验；
3. 精通 HTML5、CSS3、JavaScript，熟悉 ES6+ 特性；
4. 精通 Vue.js 技术栈，有 Vue3 实际项目经验；
5. 熟悉前端工程化，如 Webpack、Vite、ESLint 等工具；
6. 熟悉 Node.js，有全栈开发经验优先；
7. 有良好的代码风格和编程习惯，注重代码质量；
8. 具备良好的团队协作能力和沟通能力。`,
        preferences: `加分项：
1. 有开源项目经验或技术博客；
2. 熟悉 TypeScript、React、小程序开发；
3. 有大型 SaaS 平台开发经验；
4. 有团队管理经验；
5. 有良好的英语读写能力。`
      },
      rules: {
        title: [
          { required: true, message: '请输入职位名称', trigger: 'blur' },
          { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
        ],
        job_type: [
          { required: true, message: '请选择职位类型', trigger: 'change' }
        ],
        department: [
          { required: true, message: '请输入所属部门', trigger: 'blur' }
        ],
        headcount: [
          { required: true, message: '请输入招聘人数', trigger: 'blur' }
        ],
        location: [
          { required: true, message: '请输入工作地点', trigger: 'blur' },
          { min: 2, max: 255, message: '长度在 2 到 255 个字符', trigger: 'blur' }
        ],
        salary: [{ validator: validateSalary, trigger: 'change' }],
        description: [
          { required: true, message: '请输入职位描述', trigger: 'blur' },
          { min: 50, message: '职位描述不能少于50个字符', trigger: 'blur' }
        ],
        requirements: [
          { required: true, message: '请输入任职要求', trigger: 'blur' },
          { min: 50, message: '任职要求不能少于50个字符', trigger: 'blur' }
        ]
      }
    }
  },
  methods: {
    resetForm() {
      this.$confirm('确定要重置表单吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.$refs.form.resetFields()
        this.$message.success('表单已重置')
      }).catch(() => {})
    },
    async submitForm() {
      try {
        await this.$refs.form.validate()

        // 转换数据格式
        const formData = {
          ...this.positionForm,
          // 确保字段名称与后端一致
          title: this.positionForm.title,
          job_type: this.positionForm.job_type,
          department: this.positionForm.department, // 确保这个字段被包含
          headcount: this.positionForm.headcount,
          salary_min: this.positionForm.salary_min,
          salary_max: this.positionForm.salary_max,
          salary_type: this.getSalaryType(this.positionForm.salary_type),
          salary_structure: this.positionForm.salary_structure,
          location: this.positionForm.location,
          experience_required: this.positionForm.experience_required,
          education_required: this.positionForm.education_required,
          description: this.positionForm.description,
          requirements: this.positionForm.requirements,
          benefits: this.positionForm.benefits.join(','),
          preferences: this.positionForm.preferences
        }

        const loading = this.$loading({
          lock: true,
          text: '正在发布职位...',
          spinner: 'el-icon-loading',
          background: 'rgba(0, 0, 0, 0.7)'
        })

        try {
          console.log('formData', formData)
          await this.$store.dispatch('position/publishPosition', formData)
          this.$message.success('职位发布成功')
          this.$router.push('/position/maintain')
        } finally {
          loading.close()
        }
      } catch (error) {
        console.error('职位发布失败:', error)
        this.$message.error('职位发布失败，请检查表单内容后重试')
      }
    },

    getSalaryType(type) {
      const typeMap = {
        'month': '月薪',
        'year': '年薪',
        'negotiate': '面议'
      }
      return typeMap[type] || '月薪'
    }
  }
}
</script>

<style lang="scss" scoped>
.app-container {
  padding: 20px;
  background-color: #f5f7fa;

  .position-form {
    max-width: 1200px;
    margin: 0 auto;
  }
}

.box-card {
  margin-bottom: 20px;
  border-radius: 8px;

  .card-header {
    display: flex;
    align-items: center;

    .text-muted {
      margin-left: 10px;
      font-size: 12px;
      color: #909399;
    }
  }
}

.salary-range {
  .salary-separator {
    text-align: center;
    line-height: 40px;
  }

  .el-input-number {
    width: 100%;
  }
}

.benefit-group {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

.form-footer {
  margin-top: 30px;
  text-align: center;

  .el-button {
    min-width: 120px;
    margin: 0 10px;
  }
}

::v-deep .el-card__header {
  padding: 15px 20px;
  border-bottom: 1px solid #ebeef5;
  background: #fafafa;
}

::v-deep .el-card__body {
  padding: 20px;
}
</style>
