<template>
  <div class="app-wrapper">
    <sidebar class="sidebar-container" />
    <div class="main-container">
      <div class="content">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script>
import { Sidebar } from './components'

export default {
  name: 'Layout',
  components: {
    Sidebar
  }
}
</script>

<style lang="scss" scoped>
.app-wrapper {
  position: relative;
  height: 100%;
  width: 100%;
  
  .sidebar-container {
    position: fixed;
    top: 0;
    left: 0;
    z-index: 1001;
    width: 210px;
    height: 100%;
    overflow: hidden;
    transition: width 0.28s;
  }
  
  .main-container {
    min-height: 100%;
    margin-left: 210px;
    position: relative;
    
    .content {
      padding: 20px;
    }
  }
}
</style>
