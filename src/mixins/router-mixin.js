export default {
  beforeCreate() {
    // 确保组件实例有 $router
    if (!this.$router && this.$root && this.$root.$router) {
      this.$router = this.$root.$router
    }
  }
}
