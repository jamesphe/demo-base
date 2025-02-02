<template>
  <div v-if="!item.hidden">
    <template v-if="!item.children">
      <el-menu-item :index="resolvePath(item.path || '')">
        <i v-if="item.icon" :class="item.icon"></i>
        <span slot="title">{{ item.title }}</span>
      </el-menu-item>
    </template>

    <el-submenu v-else :index="resolvePath(item.path || item.title)">
      <template slot="title">
        <i v-if="item.icon" :class="item.icon"></i>
        <span>{{ item.title }}</span>
      </template>
      <sidebar-item
        v-for="child in item.children"
        :key="child.path || child.title"
        :item="child"
        :base-path="resolvePath(child.path || '')"
      />
    </el-submenu>
  </div>
</template>

<script>
import path from 'path'
import { isExternal } from '@/utils/validate'
import Item from './Item'
import AppLink from './Link'
import FixiOSBug from './FixiOSBug'

export default {
  name: 'SidebarItem',
  components: { Item, AppLink },
  mixins: [FixiOSBug],
  props: {
    // route object
    item: {
      type: Object,
      required: true
    },
    isNest: {
      type: Boolean,
      default: false
    },
    basePath: {
      type: String,
      default: ''
    }
  },
  data() {
    // To fix https://github.com/PanJiaChen/vue-admin-template/issues/237
    // TODO: refactor with render function
    this.onlyOneChild = null
    return {}
  },
  methods: {
    hasOneShowingChild(children = [], parent) {
      const showingChildren = children.filter(item => {
        if (item.hidden) {
          return false
        } else {
          // Temp set(will be used if only has one showing child)
          this.onlyOneChild = item
          return true
        }
      })

      // When there is only one child router, the child router is displayed by default
      if (showingChildren.length === 1) {
        return true
      }

      // Show parent if there are no child router to display
      if (showingChildren.length === 0) {
        this.onlyOneChild = { ... parent, path: '', noShowingChildren: true }
        return true
      }

      return false
    },
    resolvePath(routePath) {
      if (!routePath) return ''
      if (this.isExternalLink(routePath)) {
        return routePath
      }
      return path.resolve(this.basePath || '', routePath)
    },
    isExternalLink(path) {
      return /^(https?:|mailto:|tel:)/.test(path)
    }
  }
}
</script>
