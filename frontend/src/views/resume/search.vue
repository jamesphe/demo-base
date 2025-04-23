<template>
  <basic-view title="简历检索">
    <div class="search-container">
      <!-- 搜索表单组件 -->
      <resume-search-form 
        :search-form="searchForm" 
        @search="handleSearch" 
        @reset="resetForm"
        @reset-advanced="resetAdvancedForm"
      />

      <!-- 搜索结果 -->
      <div v-loading="loading" class="search-result">
        <div class="result-header">
          <span class="result-count">共找到 {{ total }} 份简历</span>
          <div class="view-controls">
            <el-radio-group v-model="viewMode" size="small">
              <el-radio-button label="list">列表视图</el-radio-button>
              <el-radio-button label="card">卡片视图</el-radio-button>
            </el-radio-group>
            <el-select v-model="sortBy" size="small" style="margin-left: 10px">
              <el-option label="更新时间" value="updateTime" />
              <el-option label="相关度" value="relevance" />
              <el-option label="工作年限" value="experience" />
            </el-select>
          </div>
        </div>

        <!-- 列表视图 -->
        <resume-result-list 
          v-if="viewMode === 'list'"
          :result-list="resultList"
          @view-detail="viewDetail"
          @preview-resume="previewOriginalResume"
          @ai-analyze="aiAnalyzeResume"
          @download="handleDownload"
          @toggle-star="toggleStar"
          @send-invite="sendInterviewInvite"
          @more-actions="handleMoreActions"
        />

        <!-- 卡片视图 -->
        <resume-result-card
          v-else
          :result-list="resultList"
          @view-detail="viewDetail"
          @preview-resume="previewOriginalResume"
          @ai-analyze="aiAnalyzeResume"
          @download="handleDownload"
          @toggle-star="toggleStar"
          @more-actions="handleMoreActions"
        />

        <!-- 分页 -->
        <div class="pagination-container">
          <el-pagination
            background
            :current-page="page.current"
            :page-sizes="[12, 24, 36, 48]"
            :page-size="page.size"
            layout="total, sizes, prev, pager, next, jumper"
            :total="total"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </div>

      <!-- 简历详情对话框 -->
      <el-dialog
        title="简历详情"
        :visible.sync="detailVisible"
        width="70%"
        :before-close="handleDetailClose"
        custom-class="resume-detail-dialog"
      >
        <resume-detail
          :detail="currentDetail"
          :loading="detailLoading"
        />
      </el-dialog>

      <!-- 原始简历预览对话框 -->
      <resume-preview
        :visible.sync="previewVisible"
        :resume-id="currentResumeId"
        :file-name="currentFileName"
        @close="handlePreviewClose"
      />

      <!-- AI解读对话框 -->
      <ai-analysis-dialog
        :visible.sync="aiAnalysisVisible"
        :resume="currentAnalyzedResume"
      />
    </div>
  </basic-view>
</template>

<script>
import BasicView from '@/components/BasicView'
import ResumeDetail from '@/components/ResumeDetail'
import ResumePreview from '@/components/ResumePreview'
import ResumeSearchForm from '@/components/Resume/SearchForm'
import ResumeResultList from '@/components/Resume/ResultList'
import ResumeResultCard from '@/components/Resume/ResultCard'
import AiAnalysisDialog from '@/components/Resume/AiAnalysisDialog'
import { mapState, mapGetters, mapActions } from 'vuex'

export default {
  name: 'ResumeSearch',
  components: {
    BasicView,
    ResumeDetail,
    ResumePreview,
    ResumeSearchForm,
    ResumeResultList,
    ResumeResultCard,
    AiAnalysisDialog
  },
  data() {
    return {
      searchForm: {
        keyword: '',
        minAge: null,
        maxAge: null,
        gender: '',
        political: '',
        education: '',
        school: '',
        major: '',
        experience: '',
        currentPosition: '',
        industry: '',
        expectedPosition: '',
        expectedIndustry: '',
        expectedLocation: '',
        minSalary: null,
        maxSalary: null,
        jobStatus: '',
        currentLocation: '',
        skills: [],
        languages: [],
        certificates: [],
        additionalRequirements: ''
      },
      viewMode: 'list',
      sortBy: 'updateTime',
      page: {
        current: 1,
        size: 12
      },
      detailVisible: false,
      previewVisible: false,
      currentResumeId: null,
      currentFileName: '',
      aiAnalysisVisible: false,
      currentAnalyzedResume: null
    }
  },
  computed: {
    ...mapState('resume', ['loading']),
    ...mapGetters('resume', [
      'searchResult',
      'detailLoading',
      'currentDetail'
    ]),
    resultList() {
      return this.searchResult.items || []
    },
    total() {
      return this.searchResult.total || 0
    }
  },
  created() {
    console.log('ResumeSearch组件已创建')
    this.handleSearch()
  },
  methods: {
    ...mapActions('resume', [
      'searchResumes',
      'downloadResume',
      'toggleResumeStar',
      'exportSearchResult',
      'getResumeDetail'
    ]),

    // 搜索
    async handleSearch() {
      console.log('开始执行搜索，当前页码:', this.page.current, '每页数量:', this.page.size)
      try {
        const params = {
          page: this.page.current,
          pageSize: this.page.size,
          keyword: this.searchForm.keyword,
          experience: this.searchForm.experience,
          education: this.searchForm.education,
          skills: this.searchForm.skills.join(','),
          sort: this.sortBy,
          expectedLocation: this.searchForm.expectedLocation,
          // 高级搜索条件
          minAge: this.searchForm.minAge,
          maxAge: this.searchForm.maxAge,
          gender: this.searchForm.gender,
          school: this.searchForm.school,
          major: this.searchForm.major,
          currentPosition: this.searchForm.currentPosition,
          industry: this.searchForm.industry,
          expectedPosition: this.searchForm.expectedPosition,
          expectedIndustry: this.searchForm.expectedIndustry,
          minSalary: this.searchForm.minSalary,
          maxSalary: this.searchForm.maxSalary,
          jobStatus: this.searchForm.jobStatus,
          languages: this.searchForm.languages ? this.searchForm.languages.join(',') : '',
          certificates: this.searchForm.certificates ? this.searchForm.certificates.join(',') : '',
          additionalRequirements: this.searchForm.additionalRequirements
        }

        console.log('搜索参数:', params)
        await this.searchResumes(params)
        console.log('搜索完成，结果数量:', this.resultList.length)
      } catch (error) {
        console.error('搜索失败:', error)
        this.$message.error('搜索失败，请稍后重试')
      }
    },

    // 重置表单
    resetForm() {
      this.searchForm = {
        keyword: '',
        minAge: null,
        maxAge: null,
        gender: '',
        political: '',
        education: '',
        school: '',
        major: '',
        experience: '',
        currentPosition: '',
        industry: '',
        expectedPosition: '',
        expectedIndustry: '',
        expectedLocation: '',
        minSalary: null,
        maxSalary: null,
        jobStatus: '',
        currentLocation: '',
        skills: [],
        languages: [],
        certificates: [],
        additionalRequirements: ''
      }
      this.handleSearch()
    },

    // 重置高级筛选条件
    resetAdvancedForm() {
      // 保留快速筛选区的值
      const quickSearchValues = {
        keyword: this.searchForm.keyword,
        experience: this.searchForm.experience,
        education: this.searchForm.education,
        expectedLocation: this.searchForm.expectedLocation
      }
      
      // 重置整个表单
      this.searchForm = {
        keyword: '',
        minAge: null,
        maxAge: null,
        gender: '',
        political: '',
        education: '',
        school: '',
        major: '',
        experience: '',
        currentPosition: '',
        industry: '',
        expectedPosition: '',
        expectedIndustry: '',
        expectedLocation: '',
        minSalary: null,
        maxSalary: null,
        jobStatus: '',
        currentLocation: '',
        skills: [],
        languages: [],
        certificates: [],
        additionalRequirements: ''
      }
      
      // 恢复快速筛选区的值
      Object.keys(quickSearchValues).forEach(key => {
        this.searchForm[key] = quickSearchValues[key]
      })
    },

    // 导出结果
    async handleExport() {
      try {
        const params = {
          keyword: this.searchForm.keyword,
          experience: this.searchForm.experience,
          education: this.searchForm.education,
          skills: this.searchForm.skills.join(','),
          sort: this.sortBy
        }

        await this.exportSearchResult(params)
        this.$message.success('导出成功')
      } catch (error) {
        this.$message.error('导出失败，请稍后重试')
      }
    },

    // 查看详情
    async viewDetail(row) {
      console.log('开始获取简历详情，行数据：', row)
      this.detailVisible = true
      try {
        const detail = await this.getResumeDetail(row.id)
        console.log('获取简历详情成功，当前详情数据：', detail)

        // 检查数据是否有效
        if (!detail) {
          throw new Error('获取简历详情失败：数据为空')
        }
      } catch (error) {
        console.error('获取简历详情失败:', error)
        this.$message.error('获取简历详情失败，请稍后重试')
        this.detailVisible = false
      }
    },

    // 关闭详情
    handleDetailClose() {
      console.log('关闭简历详情对话框')
      this.detailVisible = false
      // 清空当前详情数据
      this.$store.commit('resume/SET_CURRENT_DETAIL', null)
    },

    // 下载简历
    async handleDownload(row) {
      try {
        await this.downloadResume({ id: row.id, fileName: row.fileName })
        this.$message.success('下载成功')
      } catch (error) {
        this.$message.error('下载失败，请稍后重试')
      }
    },

    // 收藏/取消收藏
    async toggleStar(row) {
      try {
        await this.toggleResumeStar({ id: row.id, starred: !row.starred })
        this.$message.success(row.starred ? '已取消收藏' : '已收藏')
      } catch (error) {
        this.$message.error('操作失败，请稍后重试')
      }
    },

    // 分页大小改变
    handleSizeChange(val) {
      this.page.size = val
      this.handleSearch()
    },

    // 当前页改变
    handleCurrentChange(val) {
      this.page.current = val
      this.handleSearch()
    },

    handleMoreActions({ command, row }) {
      switch (command) {
        case 'addToPool':
          this.addToTalentPool(row)
          break
        case 'addNote':
          this.addNote(row)
          break
        case 'sendEmail':
          this.sendEmail(row)
          break
        case 'reject':
          this.rejectCandidate(row)
          break
        case 'sendInterviewInvite':
          this.sendInterviewInvite(row)
          break
      }
    },

    sendInterviewInvite(row) {
      this.$message({
        message: '正在开发面试邀请功能...',
        type: 'info'
      })
    },

    sendEmail(row) {
      this.$message({
        message: '邮件发送功能开发中...',
        type: 'info'
      })
    },

    rejectCandidate(row) {
      this.$confirm('确定将该候选人标记为"不合适"吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        // TODO: 调用API更新状态
        this.$message({
          type: 'success',
          message: '已标记为不合适'
        })
      }).catch(() => {})
    },

    addToTalentPool(row) {
      this.$message({
        message: '已添加到人才库',
        type: 'success'
      })
    },

    addNote(row) {
      this.$prompt('请输入备注内容', '添加备注', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputPlaceholder: '请输入备注信息...'
      }).then(({ value }) => {
        this.$message({
          type: 'success',
          message: '备注已添加'
        })
      }).catch(() => {})
    },

    // 预览原始简历
    previewOriginalResume(row) {
      console.log('预览原始简历:', row)
      this.currentResumeId = row.id
      this.currentFileName = row.fileName || ''
      this.previewVisible = true
    },

    // 关闭预览
    handlePreviewClose() {
      this.previewVisible = false
      this.currentResumeId = null
      this.currentFileName = ''
    },

    // AI解读简历
    aiAnalyzeResume(row) {
      this.currentAnalyzedResume = row
      this.aiAnalysisVisible = true
    }
  }
}
</script>

<style lang="scss" scoped>
.search-container {
  padding: 20px;
  background-color: #f5f7fa;

  .search-result {
    background-color: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
    overflow: hidden;
    margin-top: 20px;

    .result-header {
      padding: 16px 24px;
      border-bottom: 1px solid #ebeef5;
      display: flex;
      justify-content: space-between;
      align-items: center;

      .result-count {
        font-size: 14px;
        color: #606266;
        font-weight: 500;
      }

      .view-controls {
        display: flex;
        align-items: center;
        gap: 12px;
      }
    }
  }

  // 分页器样式
  .pagination-container {
    margin-top: 20px;
    padding: 16px;
    display: flex;
    justify-content: flex-end;
  }
}

.resume-detail-dialog {
  :deep(.el-dialog__body) {
    padding: 20px 30px;
  }
}
</style>
