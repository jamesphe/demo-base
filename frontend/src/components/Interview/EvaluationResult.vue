<template>
  <div class="evaluation-result">
    <el-card>
      <div slot="header" class="clearfix">
        <span>评估结果</span>
        <el-tag 
          :type="getResultTagType" 
          style="float: right"
        >{{ getResultText }}</el-tag>
      </div>
      
      <description-list :column="2" :border="true">
        <description-item label="评估人">
          {{ evaluation.evaluator_name || '系统' }}
        </description-item>
        <description-item label="评估时间">
          {{ formatDateTime(evaluation.created_at) }}
        </description-item>
        <description-item label="综合评分">
          <el-rate
            v-model="evaluation.overall_score"
            disabled
            show-score
          />
        </description-item>
        <description-item label="技术评分" v-if="evaluation.technical_score">
          <el-rate
            v-model="evaluation.technical_score"
            disabled
            show-score
          />
        </description-item>
        <description-item label="沟通评分" v-if="evaluation.communication_score">
          <el-rate
            v-model="evaluation.communication_score"
            disabled
            show-score
          />
        </description-item>
        <description-item label="经验评分" v-if="evaluation.experience_score">
          <el-rate
            v-model="evaluation.experience_score"
            disabled
            show-score
          />
        </description-item>
        <description-item label="文化评分" v-if="evaluation.culture_fit_score">
          <el-rate
            v-model="evaluation.culture_fit_score"
            disabled
            show-score
          />
        </description-item>
      </description-list>

      <div class="conclusion-section">
        <h4>评估结论</h4>
        <p>{{ evaluation.conclusion }}</p>
      </div>

      <div class="details-section" v-if="hasDetails">
        <el-collapse>
          <el-collapse-item title="优势与不足" name="1" v-if="hasStrengthsOrWeaknesses">
            <div v-if="evaluation.strengths && evaluation.strengths.length > 0">
              <h4>优势</h4>
              <el-tag
                v-for="(strength, index) in evaluation.strengths"
                :key="'strength-' + index"
                type="success"
                effect="plain"
                class="tag-item"
              >
                {{ strength }}
              </el-tag>
            </div>
            
            <div v-if="evaluation.weaknesses && evaluation.weaknesses.length > 0">
              <h4>不足</h4>
              <el-tag
                v-for="(weakness, index) in evaluation.weaknesses"
                :key="'weakness-' + index"
                type="danger"
                effect="plain"
                class="tag-item"
              >
                {{ weakness }}
              </el-tag>
            </div>
          </el-collapse-item>
          
          <el-collapse-item title="技术能力评价" name="2" v-if="evaluation.technical_comments">
            <p>{{ evaluation.technical_comments }}</p>
          </el-collapse-item>
          
          <el-collapse-item title="沟通能力评价" name="3" v-if="evaluation.communication_comments">
            <p>{{ evaluation.communication_comments }}</p>
          </el-collapse-item>
          
          <el-collapse-item title="经验评价" name="4" v-if="evaluation.experience_comments">
            <p>{{ evaluation.experience_comments }}</p>
          </el-collapse-item>
          
          <el-collapse-item title="文化匹配评价" name="5" v-if="evaluation.cultural_comments">
            <p>{{ evaluation.cultural_comments }}</p>
          </el-collapse-item>
          
          <el-collapse-item title="其他备注" name="6" v-if="evaluation.comments">
            <p>{{ evaluation.comments }}</p>
          </el-collapse-item>
        </el-collapse>
      </div>
    </el-card>
  </div>
</template>

<script>
import DescriptionList from '@/components/DescriptionList'
import DescriptionItem from '@/components/DescriptionList/Item'

export default {
  name: 'EvaluationResult',
  components: {
    DescriptionList,
    DescriptionItem
  },
  props: {
    evaluation: {
      type: Object,
      required: true
    }
  },
  computed: {
    getResultText() {
      const resultMap = {
        'pass': '通过',
        'fail': '不通过',
        'pending': '待定',
        '通过': '通过',
        '不通过': '不通过',
        '待定': '待定'
      }
      return resultMap[this.evaluation.result] || this.evaluation.result
    },
    getResultTagType() {
      const typeMap = {
        'pass': 'success',
        'fail': 'danger',
        'pending': 'warning',
        '通过': 'success',
        '不通过': 'danger',
        '待定': 'warning'
      }
      return typeMap[this.evaluation.result] || 'info'
    },
    hasStrengthsOrWeaknesses() {
      return (
        (this.evaluation.strengths && this.evaluation.strengths.length > 0) ||
        (this.evaluation.weaknesses && this.evaluation.weaknesses.length > 0)
      )
    },
    hasDetails() {
      return (
        this.hasStrengthsOrWeaknesses ||
        this.evaluation.technical_comments ||
        this.evaluation.communication_comments ||
        this.evaluation.experience_comments ||
        this.evaluation.cultural_comments ||
        this.evaluation.comments
      )
    }
  },
  methods: {
    formatDateTime(timestamp) {
      if (!timestamp) return '-'
      const date = new Date(timestamp)
      return date.toLocaleString('zh-CN')
    }
  }
}
</script>

<style lang="scss" scoped>
.evaluation-result {
  margin-bottom: 20px;
  
  .conclusion-section {
    margin: 15px 0;
    padding: 15px;
    background-color: #f9f9f9;
    border-radius: 4px;
    
    h4 {
      margin-top: 0;
      margin-bottom: 10px;
      color: #606266;
    }
    
    p {
      margin: 0;
      line-height: 1.6;
    }
  }
  
  .details-section {
    margin-top: 20px;
    
    h4 {
      margin-top: 15px;
      margin-bottom: 10px;
      color: #606266;
    }
    
    .tag-item {
      margin-right: 8px;
      margin-bottom: 8px;
    }
  }
  
  :deep(.description-list) {
    background-color: #fff;
    border: 1px solid #ebeef5;
    border-radius: 4px;
    padding: 16px;
    
    .description-term {
      line-height: 1.5;
      padding-right: 10px;
      font-weight: 500;
    }
    
    .description-detail {
      line-height: 1.5;
      padding: 0 10px;
      
      .el-rate {
        margin-top: 4px;
      }
    }
  }
}
</style> 