<template>
  <el-col :span="span" class="description-item">
    <div class="description-term">{{ label }}</div>
    <div class="description-detail">
      <slot></slot>
    </div>
  </el-col>
</template>

<script>
export default {
  name: 'DescriptionItem',
  props: {
    label: {
      type: String,
      default: ''
    },
    span: {
      type: Number,
      default: 8
    }
  },
  inject: {
    descriptionList: {
      default: () => ({})
    }
  },
  computed: {
    computedSpan() {
      const { column } = this.descriptionList
      return this.span || 24 / column
    }
  }
}
</script>

<style lang="scss" scoped>
.description-item {
  margin-bottom: 16px;
  color: rgba(0, 0, 0, 0.65);
  
  .description-term {
    margin-bottom: 8px;
    color: rgba(0, 0, 0, 0.85);
    font-weight: 500;
  }
  
  .description-detail {
    color: rgba(0, 0, 0, 0.65);
    word-break: break-word;
  }
}
</style> 