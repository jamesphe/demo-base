import request from '@/utils/request'

// 模拟数据
const mockProjects = [
  {
    id: 1,
    projectCode: 'TP001',
    name: '计算机组装与维护实训',
    isVirtual: true,
    majorCode: 'CS001',
    majorName: '计算机科学与技术',
    courseCode: 'C001',
    trainingResources: '计算机配件、工具箱、教学视频',
    typicalTasks: '1. 计算机组装\n2. 系统安装\n3. 故障诊断',
    skillRequirements: '掌握计算机硬件组装、系统安装、故障排查等技能',
    assessmentMethod: '实操考核 60%\n理论考试 40%',
    moduleCount: 3,
    trainingHours: 32,
    isExternalService: false,
    academicYear: '2023-2024',
    semester: '1',
    otherTrainingLocations: '无',
    trainingRoomCode: 'TR001'
  },
  {
    id: 2,
    projectCode: 'TP002',
    name: '网络设备配置实训',
    isVirtual: false,
    majorCode: 'CS002',
    majorName: '网络工程',
    courseCode: 'C002',
    trainingResources: '路由器、交换机、网线、配置线、实训工具',
    typicalTasks: '1. 网络设备基本配置\n2. VLAN配置\n3. 路由协议配置\n4. ACL配置\n5. NAT配置',
    skillRequirements: '掌握网络设备配置、网络规划、故障排除等技能',
    assessmentMethod: '实操考核 70%\n方案设计 20%\n出勤率 10%',
    moduleCount: 5,
    trainingHours: 48,
    isExternalService: true,
    academicYear: '2023-2024',
    semester: '1',
    otherTrainingLocations: '思科网络学院',
    trainingRoomCode: 'TR002'
  },
  {
    id: 3,
    projectCode: 'TP003',
    name: 'Web全栈开发实训',
    isVirtual: false,
    majorCode: 'CS001',
    majorName: '计算机科学与技术',
    courseCode: 'C003',
    trainingResources: '开发服务器、数据库服务器、项目案例、开发文档',
    typicalTasks: '1. 前端界面开发\n2. 后端接口开发\n3. 数据库设计\n4. 项目部署',
    skillRequirements: '掌握前后端开发技术、数据库设计、项目部署等技能',
    assessmentMethod: '项目完成度 50%\n代码质量 30%\n文档规范 20%',
    moduleCount: 4,
    trainingHours: 64,
    isExternalService: false,
    academicYear: '2023-2024',
    semester: '2',
    otherTrainingLocations: '无',
    trainingRoomCode: 'TR003'
  },
  {
    id: 4,
    projectCode: 'TP004',
    name: '人工智能应用开发实训',
    isVirtual: true,
    majorCode: 'CS003',
    majorName: '人工智能',
    courseCode: 'C004',
    trainingResources: 'GPU服务器、深度学习框架、数据集、算法模型',
    typicalTasks: '1. 数据预处理\n2. 模型训练\n3. 模型优化\n4. 应用部署',
    skillRequirements: '掌握机器学习算法、深度学习框架使用、模型训练与优化等技能',
    assessmentMethod: '模型性能 40%\n创新应用 30%\n答辩表现 30%',
    moduleCount: 4,
    trainingHours: 56,
    isExternalService: true,
    academicYear: '2023-2024',
    semester: '2',
    otherTrainingLocations: 'AI创新实验室',
    trainingRoomCode: 'TR004'
  },
  {
    id: 5,
    projectCode: 'TP005',
    name: '嵌入式系统开发实训',
    isVirtual: false,
    majorCode: 'CS004',
    majorName: '物联网工程',
    courseCode: 'C005',
    trainingResources: '开发板、传感器套件、示波器、编程器',
    typicalTasks: '1. 硬件电路设计\n2. 驱动程序开发\n3. 应用程序开发\n4. 系统测试',
    skillRequirements: '掌握嵌入式硬件设计、驱动开发、应用开发等技能',
    assessmentMethod: '作品完成度 60%\n文档质量 20%\n答辩表现 20%',
    moduleCount: 4,
    trainingHours: 48,
    isExternalService: false,
    academicYear: '2023-2024',
    semester: '1',
    otherTrainingLocations: '无',
    trainingRoomCode: 'TR005'
  },
  {
    id: 6,
    projectCode: 'TP006',
    name: '数据分析与可视化实训',
    isVirtual: true,
    majorCode: 'CS005',
    majorName: '数据科学与大数据技术',
    courseCode: 'C006',
    trainingResources: '数据分析软件、数据集、可视化工具、案例资料',
    typicalTasks: '1. 数据清洗与预处理\n2. 统计分析\n3. 数据建模\n4. 可视化展示',
    skillRequirements: '掌握数据处理、统计分析、数据可视化等技能',
    assessmentMethod: '分析报告 40%\n可视化效果 30%\n演示讲解 30%',
    moduleCount: 4,
    trainingHours: 40,
    isExternalService: true,
    academicYear: '2023-2024',
    semester: '2',
    otherTrainingLocations: '大数据实验室',
    trainingRoomCode: 'TR006'
  },
  {
    id: 7,
    projectCode: 'TP007',
    name: '移动应用开发实训',
    isVirtual: false,
    majorCode: 'CS001',
    majorName: '计算机科学与技术',
    courseCode: 'C007',
    trainingResources: '移动开发工具、测试设备、UI设计工具',
    typicalTasks: '1. UI界面设计\n2. 功能模块开发\n3. 数据存储处理\n4. 应用发布',
    skillRequirements: '掌握移动应用开发、UI设计、数据处理等技能',
    assessmentMethod: '作品完成度 50%\n用户体验 30%\n答辩表现 20%',
    moduleCount: 4,
    trainingHours: 48,
    isExternalService: false,
    academicYear: '2023-2024',
    semester: '2',
    otherTrainingLocations: '无',
    trainingRoomCode: 'TR007'
  }
]

// 获取项目列表
export function getTrainingProjects(query) {
  // 开发环境使用模拟数据
  if (process.env.NODE_ENV === 'development') {
    return Promise.resolve({
      code: 20000,
      data: {
        total: mockProjects.length,
        items: mockProjects
      }
    })
  }
  
  return request({
    url: '/api/training-projects',
    method: 'get',
    params: query
  })
}

// 获取项目详情
export function getTrainingProject(id) {
  // 开发环境使用模拟数据
  if (process.env.NODE_ENV === 'development') {
    const project = mockProjects.find(p => p.id === id)
    return Promise.resolve({
      code: 20000,
      data: project
    })
  }
  
  return request({
    url: `/api/training-projects/${id}`,
    method: 'get'
  })
}

// 创建项目
export function createTrainingProject(data) {
  return request({
    url: '/api/training-projects',
    method: 'post',
    data
  })
}

// 更新项目
export function updateTrainingProject(id, data) {
  return request({
    url: `/api/training-projects/${id}`,
    method: 'put',
    data
  })
}

// 删除项目
export function deleteTrainingProject(id) {
  return request({
    url: `/api/training-projects/${id}`,
    method: 'delete'
  })
} 