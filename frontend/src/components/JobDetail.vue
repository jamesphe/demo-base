<template>
  <el-dialog
    :title="dialogTitle"
    :visible.sync="dialogVisible"
    width="65%"
    class="job-detail-dialog"
    :before-close="handleClose"
    @close="handleClose"
  >
    <div v-loading="innerLoading">
      <el-card class="box-card">
        <div slot="header" class="card-header">
          <span>基本信息</span>
        </div>
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="info-item">
              <label>职位名称：</label>
              {{ computedJobData.title || '-' }}
            </div>
          </el-col>
          <el-col :span="12">
            <div class="info-item">
              <label>职位类型：</label>
              <el-tag :type="computedJobData.type === 'fulltime' ? 'primary' : computedJobData.type === 'parttime' ? 'success' : 'warning'">
                {{ computedJobData.type === 'fulltime' ? '全职' : computedJobData.type === 'parttime' ? '兼职' : '实习' }}
              </el-tag>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="info-item">
              <label>所属部门：</label>
              {{ computedJobData.department || '-' }}
            </div>
          </el-col>
          <el-col :span="12">
            <div class="info-item">
              <label>工作地点：</label>
              {{ computedJobData.location || '-' }}
            </div>
          </el-col>
          <el-col :span="12">
            <div class="info-item">
              <label>薪资范围：</label>
              <span class="salary-text">{{ computedJobData.salaryMin }}-{{ computedJobData.salaryMax }}K/{{ computedJobData.salaryUnit === 'month' ? '月' : '年' }}</span>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="info-item">
              <label>招聘人数：</label>
              {{ computedJobData.headcount || '-' }} 人
            </div>
          </el-col>
        </el-row>
      </el-card>

      <el-card class="box-card">
        <div slot="header" class="card-header">
          <span>要求与职责</span>
        </div>
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="info-item">
              <label>学历要求：</label>
              <el-tag size="mini" type="info">
                {{ getEducationText(computedJobData.educationRequired) }}
              </el-tag>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="info-item">
              <label>经验要求：</label>
              {{ computedJobData.experienceRequired || '-' }}
            </div>
          </el-col>
        </el-row>
        <div class="info-section">
          <h4>职位描述</h4>
          <p class="description-text">{{ computedJobData.description || '-' }}</p>
        </div>
        <div class="info-section">
          <h4>任职要求</h4>
          <p class="description-text">{{ computedJobData.requirements || '-' }}</p>
        </div>
      </el-card>

      <el-card v-if="computedJobData.benefits && computedJobData.benefits.length" class="box-card">
        <div slot="header" class="card-header">
          <span>福利待遇</span>
        </div>
        <div class="benefits-list">
          <el-tag
            v-for="(benefit, index) in computedJobData.benefits"
            :key="index"
            size="small"
            type="success"
            effect="plain"
            class="benefit-tag"
          >
            {{ getBenefitLabel(benefit) }}
          </el-tag>
        </div>
      </el-card>
    </div>
    <div slot="footer" class="dialog-footer" v-if="showFooter">
      <slot name="footer">
        <el-button @click="handleClose">关闭</el-button>
      </slot>
    </div>
  </el-dialog>
</template>

<script>
import { mapActions } from 'vuex'
import Vue from 'vue'

// 创建一个帮助函数用于快速调用职位详情
export const showJobDetail = async function(vm, jobId, title = '职位详情') {
  if (!vm.$store) {
    console.error('组件必须有 $store 属性')
    return
  }

  console.log('showJobDetail被调用，jobId:', jobId)

  // 创建DOM容器并添加唯一ID
  const container = document.createElement('div')
  const containerId = 'job-detail-container-' + Date.now()
  container.id = containerId
  document.body.appendChild(container)
  console.log('创建DOM容器成功, ID:', containerId)

  // 保存DOM引用到全局
  window._jobDetailContainers = window._jobDetailContainers || {}
  window._jobDetailContainers[containerId] = container

  // 改为直接使用现有组件的方式显示
  const JobDetailComponent = vm.$options.components.JobDetail || 
                           require('./JobDetail.vue').default

  // 获取职位数据
  let jobData = {}  // 初始化为空对象而非null
  let loading = true
  
  try {
    // 创建Vue实例
    const instance = new Vue({
      store: vm.$store,
      data: {
        visible: true
      },
      render(h) {
        const propsData = {
          visible: this.visible,
          jobId: jobId,
          jobData: vm._cachedJobData || {}, // 不使用响应式数据
          initialLoading: vm._isLoading || false,
          dialogTitle: title
        }
        
        return h(JobDetailComponent, {
          props: propsData,
          on: {
            'update:visible': (value) => {
              console.log('接收到update:visible事件:', value)
              this.visible = value
              
              if (!value) {
                // 直接在这里处理关闭逻辑
                console.log('关闭弹窗，开始清理资源')
                
                // 清除缓存
                delete vm._cachedJobData
                delete vm._isLoading
                
                // 确保对话框完全关闭后再移除DOM节点
                setTimeout(() => {
                  console.log('准备销毁实例并移除DOM节点, ID:', containerId)
                  
                  // 尝试多种方式获取容器引用
                  const containerEl = window._jobDetailContainers[containerId] || 
                                      document.getElementById(containerId) ||
                                      container
                  
                  // 先解除所有事件监听和引用
                  try {
                    instance.$destroy()
                    console.log('实例销毁成功')
                  } catch (e) {
                    console.error('销毁实例失败:', e)
                  }
                  
                  // 然后移除DOM节点
                  try {
                    if (containerEl && document.body.contains(containerEl)) {
                      document.body.removeChild(containerEl)
                      console.log('DOM节点成功移除')
                    } else {
                      // 尝试直接查找可能的容器
                      const possibleDialogs = document.querySelectorAll('.el-dialog__wrapper')
                      possibleDialogs.forEach(dialog => {
                        if (!dialog.children.length || dialog.style.display === 'none') {
                          if (dialog.parentNode) {
                            dialog.parentNode.removeChild(dialog)
                            console.log('找到并移除游离的对话框元素')
                          }
                        }
                      })
                      
                      console.log('找不到原始容器节点，尝试清理完成')
                    }
                    
                    // 清理全局引用
                    if (window._jobDetailContainers && window._jobDetailContainers[containerId]) {
                      delete window._jobDetailContainers[containerId]
                    }
                    
                    // 确保遮罩被移除
                    const masks = document.querySelectorAll('.v-modal')
                    masks.forEach(mask => {
                      if (mask.parentNode) {
                        mask.parentNode.removeChild(mask)
                        console.log('移除遮罩层')
                      }
                    })
                  } catch (e) {
                    console.error('移除DOM失败:', e)
                  }
                }, 300)  // 适度延迟确保动画完成
              }
            },
            'close': () => {
              console.log('接收到close事件，直接销毁')
              // 不再调用handleClose方法，避免循环
              setTimeout(() => {
                try {
                  // 销毁组件实例
                  instance.$destroy()
                  
                  // 由update:visible事件处理程序负责清理DOM
                  console.log('实例已销毁，DOM清理由update:visible负责')
                } catch (error) {
                  console.error('销毁实例出错:', error)
                }
              }, 100)
            }
          },
          ref: 'jobDetail'
        })
      }
    }).$mount(container)

    console.log('Vue实例挂载成功')
    
    // 加载职位数据
    try {
      const jobDetail = await vm.$store.dispatch('position/getPositionDetail', jobId)
      console.log('获取到职位数据:', jobDetail)
      
      // 检查jobDetail是否有效
      if (!jobDetail) {
        throw new Error('获取职位数据失败，返回为空')
      }
      
      // 转换数据格式
      const formattedData = {
        title: jobDetail.title || '',
        type: jobDetail.jobType || 'fulltime',
        department: jobDetail.department || '',
        location: jobDetail.location || '',
        salaryMin: jobDetail.salaryMin || 0,
        salaryMax: jobDetail.salaryMax || 0,
        salaryUnit: jobDetail.salaryType === '月薪' ? 'month' : 'year',
        description: jobDetail.description || '',
        requirements: jobDetail.requirements || '',
        benefits: jobDetail.benefits ? jobDetail.benefits.split(',') : [],
        experienceRequired: jobDetail.experienceRequired || '',
        educationRequired: jobDetail.educationRequired || '',
        headcount: jobDetail.headcount || 1
      }
      
      // 更新数据
      vm._cachedJobData = formattedData
      vm._isLoading = false
      
      // 强制刷新组件，必须单独处理
      const childComponent = instance.$children[0]
      if (childComponent) {
        console.log('找到JobDetail组件实例，更新数据')
        childComponent.innerJobData = formattedData
        childComponent.innerLoading = false
      }
      
      console.log('数据加载完成，数据为:', formattedData)
    } catch (error) {
      console.error('加载职位数据出错:', error)
      vm._isLoading = false
      vm.$message.error('加载职位详情失败: ' + error.message)
    }
    
    return instance
  } catch (error) {
    console.error('创建职位详情弹窗失败:', error)
    vm.$message.error('职位详情弹窗创建失败')
    if (document.body.contains(container)) {
      document.body.removeChild(container)
    }
  }
}

export default {
  name: 'JobDetail',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    jobId: {
      type: [String, Number],
      default: null
    },
    jobData: {
      type: Object,
      default: () => ({})
    },
    loading: {
      type: Boolean,
      default: false
    },
    initialLoading: {
      type: Boolean,
      default: false
    },
    dialogTitle: {
      type: String,
      default: '职位详情'
    },
    showFooter: {
      type: Boolean,
      default: true
    }
  },
  data() {
    return {
      innerJobData: {},
      innerLoading: this.initialLoading,
      _isClosing: false
    }
  },
  watch: {
    jobData: {
      handler(newValue) {
        this.innerJobData = { ...newValue }
      },
      immediate: true,
      deep: true
    },
    loading: {
      handler(newValue) {
        this.innerLoading = newValue
      },
      immediate: true
    }
  },
  computed: {
    dialogVisible: {
      get() {
        console.log('获取dialogVisible，当前visible值:', this.visible)
        return this.visible
      },
      set(val) {
        console.log('设置dialogVisible为:', val)
        this.$emit('update:visible', val)
        
        // 确保事件确实被发出并记录日志
        this.$nextTick(() => {
          console.log('设置后visible值:', this.visible)
          if (this.visible !== val) {
            console.warn('visible属性未被正确更新')
          }
        })
      }
    },
    // 计算处理后的数据
    computedJobData() {
      // 确保始终返回一个对象，即使innerJobData和jobData都为空
      return Object.keys(this.innerJobData).length > 0 ? this.innerJobData : (this.jobData || {})
    }
  },
  mounted() {
    console.log('JobDetail组件已挂载，dialogVisible:', this.dialogVisible)
    // 监听ESC键盘事件
    document.addEventListener('keydown', this.handleEscKey)
  },
  destroyed() {
    // 清理事件监听
    document.removeEventListener('keydown', this.handleEscKey)
  },
  methods: {
    ...mapActions('position', [
      'getPositionDetail'
    ]),
    handleEscKey(e) {
      if (e.key === 'Escape' && this.dialogVisible) {
        console.log('检测到ESC按键，关闭对话框')
        this.handleClose()
      }
    },
    handleClose() {
      console.log('handleClose被调用，当前dialogVisible值:', this.dialogVisible)
      
      // 防止重复调用和循环
      if (this._isClosing) {
        console.log('已经在关闭中，跳过重复操作')
        return
      }
      
      // 标记为正在关闭
      this._isClosing = true
      
      // 直接发出事件而不是通过计算属性
      this.$emit('update:visible', false)
      this.$emit('close')
      
      // 强制修改DOM状态（仅用于紧急情况）
      this.$nextTick(() => {
        try {
          if (this.$el && this.$el.querySelector) {
            const dialog = this.$el.querySelector('.el-dialog__wrapper')
            if (dialog) {
              dialog.style.display = 'none'
              console.log('强制隐藏对话框')
              
              // 移除遮罩层
              const masks = document.querySelectorAll('.v-modal')
              masks.forEach(mask => {
                if (mask && mask.parentNode) {
                  try {
                    mask.parentNode.removeChild(mask)
                    console.log('移除遮罩层')
                  } catch (e) {
                    console.error('移除遮罩层失败:', e)
                  }
                }
              })
            }
          }
          
          // 立即尝试关闭所有可能的el-dialog组件
          const bodyEl = document.body
          if (bodyEl) {
            const allDialogs = bodyEl.querySelectorAll('.el-dialog__wrapper')
            console.log('找到', allDialogs.length, '个对话框元素')
            
            allDialogs.forEach(dialogEl => {
              // 如果对话框缺少子元素或已经隐藏，尝试移除它
              if (!dialogEl.children.length || 
                  dialogEl.style.display === 'none' ||
                  dialogEl.classList.contains('is-hidden')) {
                console.log('找到需要清理的对话框')
                dialogEl.style.display = 'none'
                // 尝试触发关闭事件
                const closeBtn = dialogEl.querySelector('.el-dialog__headerbtn')
                if (closeBtn) {
                  closeBtn.click()
                  console.log('触发对话框关闭按钮点击')
                }
              }
            })
          }
        } catch (e) {
          console.error('清理DOM时出错:', e)
        }
        
        console.log('DOM更新后dialogVisible值:', this.dialogVisible)
        // 200ms后重置标记，允许下一次关闭
        setTimeout(() => {
          this._isClosing = false
        }, 200)
      })
    },
    getEducationText(education) {
      const educationMap = {
        'bachelor': '本科',
        'master': '硕士',
        'phd': '博士',
        'college': '大专',
        'highschool': '高中',
        'other': '其他'
      }
      return educationMap[education?.toLowerCase()] || education || '-'
    },
    getBenefitLabel(value) {
      const benefitMap = {
        'insurance': '五险一金',
        'annual_bonus': '年终奖',
        'overtime_pay': '加班补助',
        'meal': '餐补',
        'transportation': '交通补助',
        'communication': '通讯补贴',
        'holiday_benefits': '节日福利',
        'paid_leave': '带薪年假',
        'health_check': '定期体检',
        'travel': '员工旅游'
      }
      return benefitMap[value] || value
    }
  }
}
</script>

<style lang="scss" scoped>
.job-detail-dialog {
  ::v-deep .el-dialog__body {
    padding: 24px;
  }
  
  .box-card {
    margin-bottom: 20px;
    border-radius: 8px;

    .card-header {
      display: flex;
      align-items: center;
      font-size: 16px;
      font-weight: 500;
    }
  }

  .info-item {
    margin-bottom: 15px;
    display: flex;
    align-items: center;

    label {
      min-width: 80px;
      color: #606266;
      font-weight: 500;
      margin-right: 10px;
    }
  }

  .info-section {
    margin-top: 20px;

    h4 {
      margin: 0 0 10px;
      color: #303133;
      font-size: 15px;
      font-weight: 500;
    }

    .description-text {
      margin: 0;
      color: #606266;
      line-height: 1.8;
      white-space: pre-line;
    }
  }

  .benefits-list {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;

    .benefit-tag {
      margin-right: 5px;
    }
  }

  .salary-text {
    color: #f56c6c;
    font-weight: 500;
    background: #fef0f0;
    padding: 2px 8px;
    border-radius: 4px;
  }
}

::v-deep .el-dialog {
  border-radius: 8px;
  overflow: hidden;

  .el-dialog__header {
    margin: 0;
    padding: 20px 30px;
    border-bottom: 1px solid #e4e7ed;
    background: #fff;

    .el-dialog__title {
      font-size: 16px;
      font-weight: 600;
      color: #303133;
    }
  }

  .el-dialog__headerbtn {
    top: 20px;
    right: 20px;
  }

  @media screen and (max-width: 1200px) {
    width: 95% !important;
    margin: 0 auto;
  }
}
</style> 