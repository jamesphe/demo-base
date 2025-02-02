<template>
  <div v-if="!item.hidden">
    <template v-if="!item.children">
      <app-link :to="resolvePath(item.path)">
        <el-menu-item :index="resolvePath(item.path)">
          <i v-if="item.meta && item.meta.icon" :class="item.meta.icon"></i>
          <span slot="title">{{ item.meta && item.meta.title }}</span>
        </el-menu-item>
      </app-link>
    </template>

    <el-submenu v-else ref="subMenu" :index="resolvePath(item.path)">
      <template slot="title">
        <i v-if="item.meta && item.meta.icon" :class="item.meta.icon"></i>
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
  methods: {
    resolvePath(routePath) {
      if (isExternal(routePath)) {
        return routePath
      }
      if (isExternal(this.basePath)) {
        return this.basePath
      }
      return path.resolve(this.basePath, routePath)
    }
  }
}
</script>
