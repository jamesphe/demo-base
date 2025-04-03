import Vue from 'vue'
import Vuex from 'vuex'
import getters from './getters'
import user from './modules/user'
import route from './modules/route'
import permission from './modules/permission'
import trial from './modules/trial'
import tenant from './modules/tenant'
import position from './modules/position'
import resume from './modules/resume'
import jobApplication from './modules/job-application'

Vue.use(Vuex)

// https://webpack.js.org/guides/dependency-management/#requirecontext
const modulesFiles = require.context('./modules', true, /\.js$/)

// you do not need `import app from './modules/app'`
// it will auto require all vuex module from modules file
const modulesList = modulesFiles.keys().reduce((modules, modulePath) => {
  // set './app.js' => 'app'
  const moduleName = modulePath.replace(/^\.\/(.*)\.\w+$/, '$1')
  const value = modulesFiles(modulePath)
  modules[moduleName] = value.default
  return modules
}, {})

const store = new Vuex.Store({
  modules: {
    user,
    route,
    trial,
    ...modulesList,
    permission,
    tenant,
    position,
    resume,
    jobApplication
  },
  getters
})

export default store
