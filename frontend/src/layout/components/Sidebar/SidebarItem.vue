<template>
  <div v-if="!item.hidden">
    <!-- 当只有一个子路由时，直接显示为菜单项 -->
    <template v-if="hasOneShowingChild(item.children, item)">
      <app-link
        :to="resolvePath(onlyOneChild.path)"
      >
        <el-menu-item
          :index="resolvePath(onlyOneChild.path)"
          :class="{'submenu-title-noDropdown':isNest}"
        >
          <i v-if="onlyOneChild.meta && onlyOneChild.meta.icon" :class="onlyOneChild.meta.icon" />
          <span slot="title">{{ onlyOneChild.meta && onlyOneChild.meta.title }}</span>
        </el-menu-item>
      </app-link>
    </template>

    <!-- 有多个子路由时才显示为可折叠的子菜单 -->
    <el-submenu v-else ref="subMenu" :index="resolvePath(item.path)" popper-append-to-body>
      <template slot="title">
        <i v-if="item.meta && item.meta.icon" :class="item.meta.icon" />
        <span slot="title">{{ item.meta && item.meta.title }}</span>
      </template>
      <sidebar-item
        v-for="child in item.children"
        :key="child.path"
        :is-nest="true"
        :item="child"
        :base-path="resolvePath(child.path)"
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
    this.onlyOneChild = null
    return {}
  },
  methods: {
    resolvePath(routePath) {
      // 如果是外部链接，直接返回
      if (isExternal(routePath)) {
        return routePath
      }

      // 如果是绝对路径，直接返回
      if (routePath.startsWith('/')) {
        return routePath
      }

      // 如果 basePath 是外部链接，返回 basePath
      if (isExternal(this.basePath)) {
        return this.basePath
      }

      // 解析相对路径
      return path.resolve(this.basePath, routePath)
    },
    hasOneShowingChild(children = [], parent) {
      const showingChildren = children.filter(item => {
        if (item.hidden) {
          return false
        }
        this.onlyOneChild = item
        return true
      })

      // 当只有一个子路由时，显示为独立菜单项
      if (showingChildren.length === 1) {
        return true
      }

      // 没有子路由时，显示父路由
      if (showingChildren.length === 0) {
        this.onlyOneChild = { ...parent, path: '', noShowingChildren: true }
        return true
      }

      return false
    },
    handleClick(e) {
      console.log('AppLink clicked:', {
        event: e,
        path: this.resolvePath(this.onlyOneChild.path)
      })
    },
    handleMenuClick(e) {
      console.log('Menu item clicked:', {
        event: e,
        item: this.onlyOneChild,
        resolvedPath: this.resolvePath(this.onlyOneChild.path)
      })
    },
    isActive(route) {
      const active = this.$route.path === this.resolvePath(route.path) ||
                    (route.meta && route.meta.activeMenu === this.$route.path)
      console.log('Checking active state:', {
        routePath: route.path,
        currentPath: this.$route.path,
        resolvedPath: this.resolvePath(route.path),
        activeMenu: route.meta && route.meta.activeMenu,
        isActive: active
      })
      return active
    }
  }
}
</script>

<style lang="scss" scoped>
@import "~@/styles/variables.scss";

.el-menu-item, .el-submenu__title {
  &:hover {
    background-color: $menuHover !important;
  }
}

.el-menu-item.is-active {
  color: $menuActiveText !important;
  font-weight: 600;
  background-color: $menuHover !important;
  border-right: 3px solid $menuActiveText;
}

.el-menu-item {
  height: 50px;
  line-height: 50px;
}

.el-submenu__title {
  height: 50px;
  line-height: 50px;
}
</style>
