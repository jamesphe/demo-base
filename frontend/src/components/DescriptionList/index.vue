<template>
  <div class="description-list">
    <div class="description-list-title" v-if="title">
      <h4>{{ title }}</h4>
    </div>
    <el-row :gutter="gutter">
      <slot></slot>
    </el-row>
  </div>
</template>

<script>
export default {
  name: 'DescriptionList',
  props: {
    title: {
      type: String,
      default: ''
    },
    gutter: {
      type: Number,
      default: 20
    },
    column: {
      type: Number,
      default: 3
    },
    border: {
      type: Boolean,
      default: false
    }
  },
  provide() {
    return {
      descriptionList: this
    }
  }
}
</script>

<style lang="scss" scoped>
.description-list {
  margin-bottom: 16px;
  padding: 0;
  
  .description-list-title {
    margin-bottom: 16px;
    color: rgba(0, 0, 0, 0.85);
    font-weight: 500;
    font-size: 16px;
  }
  
  &.bordered {
    .description-list-item {
      padding-bottom: 0;
      border-bottom: 1px solid #e8e8e8;
      &:last-child {
        border-bottom: none;
      }
    }
  }
}
</style> 