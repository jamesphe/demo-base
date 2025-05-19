<template>
  <div class="next-step-actions">
    <el-card shadow="hover">
      <div slot="header" class="clearfix">
        <span>下一步操作</span>
        <el-button
          style="float: right; padding: 3px 0"
          type="text"
          @click="refreshOptions"
          :disabled="loading"
        >
          <i class="el-icon-refresh"></i> 刷新
        </el-button>
      </div>
      
      <div v-loading="loading">
        <el-empty description="暂无可用操作" v-if="!options || options.length === 0" />
        
        <div v-else class="actions-container">
          <el-button
            v-for="option in options"
            :key="option.action"
            :type="option.type || 'default'"
            :icon="option.icon"
            class="action-button"
            @click="executeAction(option)"
            :loading="executing && currentAction === option.action"
          >
            {{ option.label }}
          </el-button>
        </div>
        
        <!-- 安排面试弹窗 -->
        <el-dialog
          :title="getDialogTitle"
          :visible.sync="scheduleDialogVisible"
          width="650px"
        >
          <el-form
            ref="scheduleForm"
            :model="scheduleForm"
            label-width="120px"
            :rules="scheduleRules"
          >
            <el-form-item label="面试时间" prop="schedule_time">
              <el-date-picker
                v-model="scheduleForm.schedule_time"
                type="datetime"
                placeholder="选择面试时间"
                style="width: 100%"
                value-format="yyyy-MM-dd HH:mm:ss"
                :picker-options="{
                  disabledDate(time) {
                    return time.getTime() < Date.now() - 8.64e7
                  }
                }"
              />
            </el-form-item>
            
            <el-form-item label="面试时长" prop="duration">
              <el-input-number 
                v-model="scheduleForm.duration" 
                :min="30" 
                :max="240" 
                :step="30" 
                style="width: 100%"
              /> 分钟
            </el-form-item>
            
            <el-form-item label="面试地点" prop="location">
              <el-input v-model="scheduleForm.location" placeholder="线上会议/公司会议室" />
            </el-form-item>
            
            <el-form-item label="面试官" prop="interviewers">
              <el-select
                v-model="scheduleForm.interviewers"
                multiple
                filterable
                placeholder="请选择面试官"
                style="width: 100%"
              >
                <el-option
                  v-for="interviewer in interviewers"
                  :key="interviewer.id"
                  :label="interviewer.name || interviewer.username"
                  :value="interviewer.id"
                />
              </el-select>
            </el-form-item>
            
            <el-form-item label="备注" prop="notes">
              <el-input
                type="textarea"
                :rows="3"
                v-model="scheduleForm.notes"
                placeholder="面试注意事项或特殊要求"
              />
            </el-form-item>
          </el-form>
          
          <span slot="footer" class="dialog-footer">
            <el-button @click="scheduleDialogVisible = false">取 消</el-button>
            <el-button type="primary" @click="submitSchedule" :loading="executing">确 定</el-button>
          </span>
        </el-dialog>
        
        <!-- Offer弹窗 -->
        <el-dialog
          title="发送Offer"
          :visible.sync="offerDialogVisible"
          width="650px"
        >
          <el-alert
            title="将为此候选人创建Offer，确认后将跳转至Offer详情页进行完善"
            type="info"
            :closable="false"
            show-icon
          />
          
          <div style="margin-top: 20px; text-align: right;">
            <el-button @click="offerDialogVisible = false">取 消</el-button>
            <el-button type="primary" @click="submitOffer" :loading="executing">确 定</el-button>
          </div>
        </el-dialog>
        
        <!-- 拒绝候选人弹窗 -->
        <el-dialog
          title="拒绝候选人"
          :visible.sync="rejectDialogVisible"
          width="650px"
        >
          <el-form
            ref="rejectForm"
            :model="rejectForm"
            label-width="120px"
            :rules="rejectRules"
          >
            <el-form-item label="拒绝原因" prop="reason">
              <el-input
                type="textarea"
                :rows="4"
                v-model="rejectForm.reason"
                placeholder="请详细描述拒绝原因，这将帮助我们改进招聘流程"
              />
            </el-form-item>
            
            <el-form-item label="是否发送通知">
              <el-switch v-model="rejectForm.sendNotification" />
            </el-form-item>
          </el-form>
          
          <span slot="footer" class="dialog-footer">
            <el-button @click="rejectDialogVisible = false">取 消</el-button>
            <el-button type="danger" @click="submitReject" :loading="executing">确认拒绝</el-button>
          </span>
        </el-dialog>
        
        <!-- 添加备注弹窗 -->
        <el-dialog
          title="添加备注"
          :visible.sync="notesDialogVisible"
          width="650px"
        >
          <el-form
            ref="notesForm"
            :model="notesForm"
            label-width="120px"
            :rules="notesRules"
          >
            <el-form-item label="备注内容" prop="notes">
              <el-input
                type="textarea"
                :rows="4"
                v-model="notesForm.notes"
                placeholder="请输入备注内容"
              />
            </el-form-item>
          </el-form>
          
          <span slot="footer" class="dialog-footer">
            <el-button @click="notesDialogVisible = false">取 消</el-button>
            <el-button type="primary" @click="submitNotes" :loading="executing">确 定</el-button>
          </span>
        </el-dialog>
        
      </div>
    </el-card>
  </div>
</template>

<script>
import { mapActions } from 'vuex'

export default {
  name: 'NextStepActions',
  props: {
    interviewId: {
      type: Number,
      required: true
    },
    interviewType: {
      type: String,
      default: 'first'
    },
    evaluation: {
      type: Object,
      required: true
    },
    interviewers: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      loading: false,
      executing: false,
      options: [],
      currentAction: '',
      
      // 弹窗显示控制
      scheduleDialogVisible: false,
      offerDialogVisible: false,
      rejectDialogVisible: false,
      notesDialogVisible: false,
      
      // 表单数据
      scheduleForm: {
        schedule_time: '',
        duration: 60,
        location: '',
        interviewers: [],
        notes: ''
      },
      rejectForm: {
        reason: '',
        sendNotification: true
      },
      notesForm: {
        notes: ''
      },
      
      // 表单验证规则
      scheduleRules: {
        schedule_time: [
          { required: true, message: '请选择面试时间', trigger: 'change' }
        ],
        interviewers: [
          { required: true, message: '请选择至少一位面试官', trigger: 'change' }
        ]
      },
      rejectRules: {
        reason: [
          { required: true, message: '请填写拒绝原因', trigger: 'blur' }
        ]
      },
      notesRules: {
        notes: [
          { required: true, message: '请填写备注内容', trigger: 'blur' }
        ]
      },
      
      // 当前选择的操作
      currentOption: null
    }
  },
  computed: {
    getDialogTitle() {
      const typeMap = {
        first: '安排初试',
        second: '安排复试',
        final: '安排终试'
      }
      return typeMap[this.currentOption?.params?.interview_type] || '安排面试'
    }
  },
  created() {
    this.loadNextStepOptions()
  },
  methods: {
    ...mapActions('interview/evaluation', [
      'getNextSteps',
      'executeNextStep'
    ]),
    
    async loadNextStepOptions() {
      this.loading = true
      try {
        const options = await this.getNextSteps(this.interviewId)
        this.options = options
      } catch (error) {
        console.error('获取下一步选项失败:', error)
        this.$message.error('获取下一步选项失败')
      } finally {
        this.loading = false
      }
    },
    
    refreshOptions() {
      this.loadNextStepOptions()
    },
    
    executeAction(option) {
      this.currentOption = option
      this.currentAction = option.action
      
      switch (option.action) {
        case 'schedule_next_interview':
          this.scheduleDialogVisible = true
          break
        case 'send_offer':
          this.offerDialogVisible = true
          break
        case 'reject_candidate':
          this.rejectDialogVisible = true
          break
        case 'add_notes':
          this.notesDialogVisible = true
          break
        default:
          this.$message.warning('未知操作类型')
      }
    },
    
    async submitSchedule() {
      try {
        await this.$refs.scheduleForm.validate()
        
        this.executing = true
        // 合并当前选项参数和表单数据
        const nextStep = {
          action: this.currentOption.action,
          params: {
            ...this.currentOption.params,
            ...this.scheduleForm
          }
        }
        
        const result = await this.executeNextStep({
          interviewId: this.interviewId,
          nextStep
        })
        
        this.$message.success('面试安排成功')
        this.scheduleDialogVisible = false
        this.$emit('action-completed', result)
      } catch (error) {
        if (error !== 'cancel') {
          console.error('安排面试失败:', error)
          this.$message.error('安排面试失败')
        }
      } finally {
        this.executing = false
      }
    },
    
    async submitOffer() {
      this.executing = true
      try {
        const nextStep = {
          action: this.currentOption.action,
          params: this.currentOption.params
        }
        
        const result = await this.executeNextStep({
          interviewId: this.interviewId,
          nextStep
        })
        
        this.$message.success('Offer创建成功')
        this.offerDialogVisible = false
        this.$emit('action-completed', result)
        
        // 如果返回了offer_id，跳转到Offer详情页
        if (result && result.offer_id) {
          this.$confirm('Offer已创建，是否立即前往Offer详情页面？', '提示', {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'info'
          }).then(() => {
            this.$router.push(`/offers/${result.offer_id}`)
          }).catch(() => {})
        }
      } catch (error) {
        console.error('创建Offer失败:', error)
        this.$message.error('创建Offer失败')
      } finally {
        this.executing = false
      }
    },
    
    async submitReject() {
      try {
        await this.$refs.rejectForm.validate()
        
        this.executing = true
        const nextStep = {
          action: this.currentOption.action,
          params: {
            ...this.currentOption.params,
            reason: this.rejectForm.reason,
            send_notification: this.rejectForm.sendNotification
          }
        }
        
        const result = await this.executeNextStep({
          interviewId: this.interviewId,
          nextStep
        })
        
        this.$message.success('已拒绝候选人')
        this.rejectDialogVisible = false
        this.$emit('action-completed', result)
      } catch (error) {
        if (error !== 'cancel') {
          console.error('拒绝候选人失败:', error)
          this.$message.error('拒绝候选人失败')
        }
      } finally {
        this.executing = false
      }
    },
    
    async submitNotes() {
      try {
        await this.$refs.notesForm.validate()
        
        this.executing = true
        const nextStep = {
          action: this.currentOption.action,
          params: {
            notes: this.notesForm.notes
          }
        }
        
        const result = await this.executeNextStep({
          interviewId: this.interviewId,
          nextStep
        })
        
        this.$message.success('备注已添加')
        this.notesDialogVisible = false
        this.$emit('action-completed', result)
      } catch (error) {
        if (error !== 'cancel') {
          console.error('添加备注失败:', error)
          this.$message.error('添加备注失败')
        }
      } finally {
        this.executing = false
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.next-step-actions {
  margin-top: 20px;
  
  .actions-container {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    
    .action-button {
      min-width: 120px;
      margin-bottom: 10px;
    }
  }
}
</style> 