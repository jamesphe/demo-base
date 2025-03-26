<template>
  <div v-if="!item.hidden">
    <!-- 当只有一个子路由时，直接显示为菜单项 -->
    <template v-if="hasOneShowingChild(item.children, item)">
      <app-link :to="resolvePath(onlyOneChild.path)">
        <el-menu-item :index="resolvePath(onlyOneChild.path)">
          <i v-if="onlyOneChild.meta && onlyOneChild.meta.icon" :class="onlyOneChild.meta.icon" />
          <span slot="title">{{ onlyOneChild.meta && onlyOneChild.meta.title }}</span>
        </el-menu-item>
      </app-link>
    </template>

    <!-- 有多个子路由时才显示为可折叠的子菜单 -->
    <el-submenu v-else ref="subMenu" :index="resolvePath(item.path)">
      <template slot="title">
        <i v-if="item.meta && item.meta.icon" :class="item.meta.icon" />
        <span>{{ item.meta && item.meta.title }}</span>
      </template>
      <sidebar-item
        v-for="child in item.children"
        :key="child.path"
        :is-nest="true"
        :item="child"
        :base-path="resolvePath(item.path)"
        class="nest-menu"
      />
    </el-submenu>
  </div>
</template>

<script>
import path from 'path'
import { isExternal } from '@/utils/validate'
import AppLink from './Link'

export default {
  name: 'SidebarItem',
  components: { AppLink },
  props: {
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
    return {
      onlyOneChild: null
    }
  },
  methods: {
    resolvePath(routePath) {
      if (isExternal(routePath)) {
        return routePath
      }
      if (isExternal(this.basePath)) {
        return this.basePath
      }
      return path.resolve(this.basePath, routePath)
    },
    hasOneShowingChild(children = [], parent) {
      const showingChildren = children.filter(item => {
        if (item.hidden) {
          return false
        }
        // 设置 onlyOneChild 为唯一的子路由
        this.onlyOneChild = item
        return true
      })

      // 当只有一个子路由时，显示为独立菜单项
      if (showingChildren.length === 1 && !parent.meta) {
        return true
      }

      // 没有子路由时，显示父路由
      if (showingChildren.length === 0) {
        this.onlyOneChild = { ...parent, path: '', noShowingChildren: true }
        return true
      }

      return false
    }
  }
}
</script>
