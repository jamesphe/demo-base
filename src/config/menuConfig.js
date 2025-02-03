export const menuItems = [
  {
    path: '/dashboard',
    title: '首页',
    icon: 'el-icon-house',
    children: [
      {
        path: '/dashboard',
        title: '首页'
      }
    ]
  },
  {
    title: '简历管理',
    icon: 'el-icon-document',
    children: [
      {
        path: '/resume/upload',
        title: '简历上传'
      },
      {
        path: '/resume/parse',
        title: '简历解析'
      },
      {
        path: '/resume/storage',
        title: '简历存储'
      },
      {
        path: '/resume/search',
        title: '简历检索'
      }
    ]
  },
  {
    title: '候选管理',
    icon: 'el-icon-s-custom',
    children: [
      {
        path: '/candidate/profile',
        title: '候选人档案'
      },
      {
        path: '/candidate/evaluation',
        title: '候选人评估'
      },
      {
        path: '/candidate/recommendation',
        title: '候选人推荐'
      }
    ]
  },
  {
    title: '职位管理',
    icon: 'el-icon-suitcase',
    children: [
      {
        path: '/position/publish',
        title: '职位发布'
      },
      {
        path: '/position/maintain',
        title: '职位维护'
      }
    ]
  },
  {
    title: '面试管理',
    icon: 'el-icon-date',
    children: [
      {
        path: '/interview/schedule',
        title: '面试安排'
      },
      {
        path: '/interview/record',
        title: '面试记录'
      }
    ]
  },
  {
    title: '招聘分析',
    icon: 'el-icon-data-line',
    children: [
      {
        path: '/analysis/progress',
        title: '招聘进度'
      },
      {
        path: '/analysis/effect',
        title: '招聘效果'
      }
    ]
  },
  {
    title: '系统设置',
    icon: 'el-icon-setting',
    children: [
      {
        path: '/settings/user',
        title: '用户管理'
      },
      {
        path: '/settings/role',
        title: '角色管理'
      },
      {
        path: '/settings/permission',
        title: '权限管理'
      }
    ]
  }
] 