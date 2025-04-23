<template>
  <div class="search-form-container">
    <!-- 快速筛选区 -->
    <div class="quick-search">
      <el-form :inline="true" :model="form" size="small">
        <el-form-item label="关键词">
          <el-input
            v-model="form.keyword"
            placeholder="姓名/技能/公司/职位"
            style="width: 200px;"
          />
        </el-form-item>
        <el-form-item label="工作年限">
          <el-select v-model="form.experience" placeholder="不限" style="width: 120px;">
            <el-option label="不限" value="" />
            <el-option label="应届生" value="0" />
            <el-option label="1-3年" value="1-3" />
            <el-option label="3-5年" value="3-5" />
            <el-option label="5-10年" value="5-10" />
            <el-option label="10年以上" value="10+" />
          </el-select>
        </el-form-item>
        <el-form-item label="学历">
          <el-select v-model="form.education" placeholder="不限" style="width: 120px;">
            <el-option label="不限" value="" />
            <el-option label="大专" value="college" />
            <el-option label="本科" value="bachelor" />
            <el-option label="硕士" value="master" />
            <el-option label="博士" value="doctor" />
          </el-select>
        </el-form-item>
        <el-form-item label="期望城市">
          <el-select
            v-model="form.expectedLocation"
            filterable
            allow-create
            placeholder="请选择或输入"
            style="width: 160px;"
          >
            <el-option label="不限" value="" />
            <el-option label="北京" value="北京" />
            <el-option label="上海" value="上海" />
            <el-option label="广州" value="广州" />
            <el-option label="深圳" value="深圳" />
            <el-option label="杭州" value="杭州" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <i class="el-icon-search" />搜索
          </el-button>
          <el-button @click="resetForm">
            <i class="el-icon-refresh" />重置
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 高级筛选面板 -->
    <div class="search-panel">
      <el-collapse v-model="activeCollapse">
        <el-collapse-item name="advanced">
          <template slot="title">
            <div class="collapse-header">
              <div class="header-left">
                <i class="el-icon-arrow-right" />
                <span class="title">高级筛选</span>
                <el-tag size="small" type="info" class="condition-count">已选 {{ selectedConditionCount }} 项</el-tag>
              </div>
              <div class="header-right">
                <el-button type="text" class="reset-btn" @click.stop="resetAdvancedForm">
                  <i class="el-icon-refresh" />重置高级条件
                </el-button>
              </div>
            </div>
          </template>

          <el-form ref="searchForm" :model="form" label-width="90px" size="small" class="search-form">
            <!-- 基础信息 -->
            <div class="search-section">
              <div class="section-header">
                <div class="header-icon">
                  <i class="el-icon-user" />
                </div>
                <span class="header-title">基础信息</span>
              </div>
              <div class="section-content">
                <el-row :gutter="20">
                  <el-col :span="8">
                    <el-form-item label="年龄范围">
                      <el-input-number v-model="form.minAge" :min="16" :max="100" size="small" class="age-input" placeholder="最小" />
                      <span class="separator">-</span>
                      <el-input-number v-model="form.maxAge" :min="16" :max="100" size="small" class="age-input" placeholder="最大" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="8">
                    <el-form-item label="性别">
                      <el-radio-group v-model="form.gender">
                        <el-radio label="">不限</el-radio>
                        <el-radio label="M">男</el-radio>
                        <el-radio label="F">女</el-radio>
                      </el-radio-group>
                    </el-form-item>
                  </el-col>
                  <el-col :span="8">
                    <el-form-item label="政治面貌">
                      <el-select v-model="form.political" placeholder="不限" clearable>
                        <el-option label="不限" value="" />
                        <el-option label="中共党员" value="党员" />
                        <el-option label="共青团员" value="团员" />
                        <el-option label="群众" value="群众" />
                      </el-select>
                    </el-form-item>
                  </el-col>
                </el-row>
              </div>
            </div>

            <!-- 教育背景 -->
            <div class="search-section">
              <div class="section-header">
                <div class="header-icon">
                  <i class="el-icon-reading" />
                </div>
                <span class="header-title">教育背景</span>
              </div>
              <div class="section-content">
                <el-row :gutter="20">
                  <el-col :span="8">
                    <el-form-item label="毕业院校">
                      <el-input v-model="form.school" placeholder="输入学校名称" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="8">
                    <el-form-item label="专业">
                      <el-input v-model="form.major" placeholder="输入专业名称" />
                    </el-form-item>
                  </el-col>
                </el-row>
              </div>
            </div>

            <!-- 工作经验 -->
            <div class="search-section">
              <div class="section-header">
                <div class="header-icon">
                  <i class="el-icon-office-building" />
                </div>
                <span class="header-title">工作经验</span>
              </div>
              <div class="section-content">
                <el-row :gutter="20">
                  <el-col :span="8">
                    <el-form-item label="当前职位">
                      <el-input v-model="form.currentPosition" placeholder="输入职位" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="8">
                    <el-form-item label="所在行业">
                      <el-input v-model="form.industry" placeholder="输入行业" />
                    </el-form-item>
                  </el-col>
                </el-row>
              </div>
            </div>

            <!-- 求职意向 -->
            <div class="search-section">
              <div class="section-header">
                <div class="header-icon">
                  <i class="el-icon-aim" />
                </div>
                <span class="header-title">求职意向</span>
              </div>
              <div class="section-content">
                <el-row :gutter="20">
                  <el-col :span="8">
                    <el-form-item label="期望职位">
                      <el-input v-model="form.expectedPosition" placeholder="输入职位" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="8">
                    <el-form-item label="期望行业">
                      <el-input v-model="form.expectedIndustry" placeholder="输入行业" />
                    </el-form-item>
                  </el-col>
                </el-row>
                <el-row :gutter="20">
                  <el-col :span="8">
                    <el-form-item label="期望薪资">
                      <el-input-number v-model="form.minSalary" :min="0" size="small" class="salary-input" placeholder="最低" />
                      <span class="separator">-</span>
                      <el-input-number v-model="form.maxSalary" :min="0" size="small" class="salary-input" placeholder="最高" />
                      <span class="unit">K</span>
                    </el-form-item>
                  </el-col>
                  <el-col :span="8">
                    <el-form-item label="求职状态">
                      <el-select v-model="form.jobStatus" placeholder="不限" clearable>
                        <el-option label="不限" value="" />
                        <el-option label="在职看机会" value="looking" />
                        <el-option label="离职待业" value="available" />
                        <el-option label="暂不找工作" value="unavailable" />
                      </el-select>
                    </el-form-item>
                  </el-col>
                </el-row>
              </div>
            </div>

            <!-- 技能与资质 -->
            <div class="search-section">
              <div class="section-header">
                <div class="header-icon">
                  <i class="el-icon-medal" />
                </div>
                <span class="header-title">技能与资质</span>
              </div>
              <div class="section-content">
                <el-row :gutter="20">
                  <el-col :span="8">
                    <el-form-item label="专业技能">
                      <el-select
                        v-model="form.skills"
                        multiple
                        filterable
                        allow-create
                        default-first-option
                        placeholder="请选择或输入"
                        class="skill-select"
                      >
                        <el-option
                          v-for="item in skillOptions"
                          :key="item.value"
                          :label="item.label"
                          :value="item.value"
                        />
                      </el-select>
                    </el-form-item>
                  </el-col>
                  <el-col :span="8">
                    <el-form-item label="语言能力">
                      <el-select
                        v-model="form.languages"
                        multiple
                        filterable
                        placeholder="请选择语言"
                      >
                        <el-option label="英语" value="english" />
                        <el-option label="日语" value="japanese" />
                        <el-option label="韩语" value="korean" />
                        <el-option label="法语" value="french" />
                        <el-option label="德语" value="german" />
                      </el-select>
                    </el-form-item>
                  </el-col>
                  <el-col :span="8">
                    <el-form-item label="证书">
                      <el-select
                        v-model="form.certificates"
                        multiple
                        filterable
                        allow-create
                        default-first-option
                        placeholder="请选择或输入"
                      >
                        <el-option label="CPA" value="cpa" />
                        <el-option label="法律职业资格" value="legal" />
                        <el-option label="教师资格" value="teacher" />
                        <el-option label="注册建筑师" value="architect" />
                      </el-select>
                    </el-form-item>
                  </el-col>
                </el-row>
              </div>
            </div>

            <!-- 额外要求 -->
            <div class="search-section">
              <div class="section-header">
                <div class="header-icon">
                  <i class="el-icon-more" />
                </div>
                <span class="header-title">额外要求</span>
              </div>
              <div class="section-content">
                <el-form-item>
                  <el-input
                    v-model="form.additionalRequirements"
                    type="textarea"
                    :rows="3"
                    placeholder="请输入其他额外要求，将通过智能匹配方式查找符合要求的简历..."
                  />
                </el-form-item>
              </div>
            </div>

            <!-- 高级筛选按钮区 -->
            <div class="advanced-actions">
              <el-button type="text" @click="resetAdvancedForm">
                <i class="el-icon-refresh" />重置高级条件
              </el-button>
              <el-button type="primary" @click="handleSearch">
                <i class="el-icon-search" />开始筛查
              </el-button>
            </div>
          </el-form>
        </el-collapse-item>
      </el-collapse>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ResumeSearchForm',
  props: {
    searchForm: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      activeCollapse: [],
      form: this.searchForm,
      skillOptions: [
        { value: 'java', label: 'Java' },
        { value: 'python', label: 'Python' },
        { value: 'javascript', label: 'JavaScript' },
        { value: 'vue', label: 'Vue.js' },
        { value: 'react', label: 'React' },
        { value: 'node', label: 'Node.js' }
      ]
    }
  },
  computed: {
    selectedConditionCount() {
      let count = 0
      const form = this.form

      // 计算已选条件数量
      if (form.minAge || form.maxAge) count++
      if (form.gender) count++
      if (form.political) count++
      if (form.education) count++
      if (form.school) count++
      if (form.major) count++
      if (form.experience) count++
      if (form.currentPosition) count++
      if (form.industry) count++
      if (form.expectedPosition) count++
      if (form.expectedIndustry) count++
      if (form.expectedLocation) count++
      if (form.minSalary || form.maxSalary) count++
      if (form.jobStatus) count++
      if (form.currentLocation) count++
      if (form.skills && form.skills.length) count++
      if (form.languages && form.languages.length) count++
      if (form.certificates && form.certificates.length) count++
      if (form.additionalRequirements) count++

      return count
    }
  },
  methods: {
    handleSearch() {
      this.$emit('search')
    },
    resetForm() {
      this.$refs.searchForm.resetFields()
      this.$emit('reset')
    },
    resetAdvancedForm() {
      // 保留快速筛选区的值
      const quickSearchValues = {
        keyword: this.form.keyword,
        experience: this.form.experience,
        education: this.form.education,
        expectedLocation: this.form.expectedLocation
      }
      
      // 重置整个表单
      this.$refs.searchForm.resetFields()
      
      // 恢复快速筛选区的值
      Object.keys(quickSearchValues).forEach(key => {
        this.form[key] = quickSearchValues[key]
      })
      
      this.$emit('reset-advanced')
    }
  }
}
</script>

<style lang="scss" scoped>
.search-form-container {
  .quick-search {
    background-color: #fff;
    padding: 16px;
    border-radius: 8px;
    margin-bottom: 16px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);

    :deep(.el-form--inline) {
      .el-form-item {
        margin-right: 16px;
        margin-bottom: 0;

        &:last-child {
          margin-right: 0;
        }

        .el-form-item__label {
          color: #606266;
        }
      }
    }
  }

  .search-panel {
    background-color: #fff;
    border-radius: 12px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
    margin-bottom: 20px;
    overflow: hidden;

    .collapse-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      width: 100%;

      .header-left {
        display: flex;
        align-items: center;
        gap: 12px;

        i {
          font-size: 16px;
          color: #409EFF;
          transition: transform 0.3s;
        }

        .title {
          font-size: 16px;
          font-weight: 600;
          color: #1f2937;
        }

        .condition-count {
          font-size: 12px;
          padding: 2px 8px;
          border-radius: 4px;
          background-color: #f3f4f6;
          color: #6b7280;
          border: none;
        }
      }

      .header-right {
        .reset-btn {
          font-size: 13px;
          color: #6b7280;
          padding: 4px 12px;
          border-radius: 4px;
          transition: all 0.3s;

          &:hover {
            color: #409EFF;
            background-color: #ecf5ff;
          }

          i {
            margin-right: 4px;
            font-size: 14px;
          }
        }
      }
    }

    :deep(.el-collapse-item__header) {
      padding: 16px 24px;
      font-weight: 500;
      border-bottom: 1px solid #e5e7eb;

      &.is-active {
        .el-icon-arrow-right {
          transform: rotate(90deg);
        }
      }
    }

    .search-form {
      padding: 24px;

      .search-section {
        background-color: #f9fafb;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 16px;

        &:last-of-type {
          margin-bottom: 0;
        }

        .section-header {
          display: flex;
          align-items: center;
          margin-bottom: 12px;
          padding-bottom: 8px;
          border-bottom: 1px dashed #e5e7eb;

          .header-icon {
            width: 28px;
            height: 28px;
            border-radius: 6px;
            margin-right: 8px;

            i {
              font-size: 16px;
            }
          }

          .header-title {
            font-size: 14px;
          }
        }

        .section-content {
          .el-row {
            margin-bottom: 12px;

            &:last-child {
              margin-bottom: 0;
            }
          }

          .el-form-item {
            margin-bottom: 0;

            :deep(.el-form-item__label) {
              padding-right: 8px;
              line-height: 32px;
            }

            :deep(.el-input__inner),
            :deep(.el-select .el-input__inner) {
              height: 32px;
              line-height: 32px;
            }

            :deep(.el-input-number) {
              line-height: 30px;
            }
          }
        }
      }

      .advanced-actions {
        padding: 16px;
        text-align: right;
        border-top: 1px solid #e5e7eb;
        margin-top: 16px;
        display: flex;
        justify-content: flex-end;
        gap: 12px;

        .el-button {
          &[type="text"] {
            margin-right: auto;
          }

          &[type="primary"] {
            min-width: 120px;
          }
        }
      }
    }
  }
}

.separator {
  margin: 0 5px;
}

.age-input, .salary-input {
  width: 80px;
}

.unit {
  margin-left: 5px;
  color: #909399;
}
</style> 