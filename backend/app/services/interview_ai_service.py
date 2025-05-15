from typing import Dict, Any, List, AsyncGenerator
from sqlalchemy.orm import Session
from fastapi import HTTPException
import logging

from app.services.resume_service import resume_service
from app.services.job_service import job_service
from app.services.llm_service import llm_service
from app.schemas.interview import InterviewGuideRequest

logger = logging.getLogger(__name__)


class InterviewAIService:
    def _format_skills(self, skills: List[Dict]) -> str:
        """格式化技能列表
        
        Args:
            skills: 技能列表，每个技能是一个字典，包含name和level等信息
            
        Returns:
            格式化后的技能字符串，例如：'Python(熟练)、Java(精通)、Go(了解)'
        """
        if not skills:
            return "未提供技能信息"
        
        try:
            formatted_skills = []
            for skill in skills:
                if isinstance(skill, dict):
                    # 如果是字典格式，尝试获取name和level
                    name = skill.get('name', '')
                    level = skill.get('level', '')
                    if name and level:
                        formatted_skills.append(f"{name}({level})")
                    elif name:
                        formatted_skills.append(name)
                elif isinstance(skill, str):
                    # 如果是字符串格式，直接使用
                    formatted_skills.append(skill)
                
            return "、".join(formatted_skills) if formatted_skills else \
                   "未提供技能信息"
            
        except Exception as e:
            logger.error(f"格式化技能信息失败: {str(e)}")
            return "技能信息格式化失败"

    def _format_work_experience(self, work_experience: List[Dict]) -> str:
        """格式化工作经验"""
        if not work_experience:
            return "未提供工作经验"
        
        formatted = []
        for exp in work_experience:
            exp_str = (
                f"- {exp.get('company', '未知公司')} | "
                f"{exp.get('position', '未知职位')}\n"
            )
            exp_str += (
                f"  时间：{exp.get('start_date', '')} 至 "
                f"{exp.get('end_date', '')}\n"
            )
            if exp.get('description'):
                exp_str += f"  描述：{exp.get('description')}\n"
            formatted.append(exp_str)
        
        return "\n".join(formatted)

    def _format_education(self, education: List[Dict]) -> str:
        """格式化教育经历"""
        if not education:
            return "未提供教育经历"
        
        formatted = []
        for edu in education:
            edu_str = (
                f"- {edu.get('school', '未知学校')} | "
                f"{edu.get('major', '未知专业')} | "
                f"{edu.get('degree', '未知学位')}"
            )
            formatted.append(edu_str)
        
        return "\n".join(formatted)

    def _format_job_requirements(self, requirements: Dict) -> str:
        """格式化职位要求"""
        if not requirements:
            return "未提供职位要求"
        
        formatted = []
        if requirements.get('experience'):
            formatted.append(f"工作经验：{requirements['experience']}")
        if requirements.get('education'):
            formatted.append(f"学历要求：{requirements['education']}")
        if requirements.get('skills'):
            formatted.append(f"技能要求：{', '.join(requirements['skills'])}")
        if requirements.get('description'):
            formatted.append(f"职位描述：{requirements['description']}")
        
        return "\n".join(formatted)

    async def generate_interview_guide(
        self,
        db: Session,
        request: InterviewGuideRequest
    ) -> Dict[str, Any]:
        """生成面试指导文档"""
        try:
            logger.info(
                f"开始生成面试指导文档: resumeId={request.resumeId}, "
                f"jobId={request.jobId}"
            )
            
            # 1. 获取简历详情
            resume = await resume_service.get_resume_detail(
                db, 
                resume_id=request.resumeId
            )
            if not resume:
                raise HTTPException(status_code=404, detail="简历不存在")
            
            # 2. 获取职位详情
            job = await job_service.get_job_detail(
                db, 
                job_id=request.jobId
            )
            if not job:
                raise HTTPException(status_code=404, detail="职位不存在")
            
            logger.info("成功获取简历和职位信息")
            
            # 3. 构建系统提示词
            base_system_prompt = """你是一位专业的面试指导专家。请根据提供的候选人信息和职位要求，
生成一份详细且高度针对性的面试指导文档。"""

            # 根据面试官角色调整系统提示词和文档结构
            role_specific_content = {
                "部门负责人": {
                    "prompt": """作为部门负责人，你应更关注：
1. 候选人的管理潜力和领导能力
2. 技术视野和战略思维
3. 跨部门协作能力
4. 项目管理和资源调配能力
5. 团队建设和人才培养能力

评估时，请特别关注候选人简历中显示的管理经验、团队规模、项目复杂度等信息，
并与招聘职位的管理要求进行匹配分析。

在设计面试问题时，应重点考察候选人的大局观、决策能力和管理思路，
确保问题针对候选人的具体背景和应聘职位，而不是泛泛而谈。""",
                    "structure": """请按照以下结构生成文档：

# 面试指导文档

## 一、候选人综合评估
- 领导潜力评估
- 管理经验分析
- 技术视野评价
- 职业发展契合度

## 二、管理能力考察要点
- 团队管理经验
- 资源调配能力
- 项目全局把控能力
- 危机处理能力

## 三、技术决策考察
- 技术选型思路
- 架构规划能力
- 技术风险评估
- 技术团队建设

## 四、沟通协作能力
- 跨部门协作经验
- 向上沟通能力
- 团队激励方式
- 冲突处理方法

## 五、面试问题建议
- 管理经验问题（3-4个）
  * 为每个问题提供参考答案和评分要点
- 团队建设问题（3-4个）
  * 为每个问题提供参考答案和评分要点
- 技术战略问题（3-4个）
  * 为每个问题提供参考答案和评分要点
- 领导力问题（3-4个）
  * 为每个问题提供参考答案和评分要点

## 六、评估参考标准
- 领导力评分标准
- 管理能力评分标准
- 战略思维评分标准
- 综合评价和建议

请确保建议具有针对性和实用性，并与候选人背景和职位要求紧密结合。每个问题都必须包含详细的参考答案，以便作为部门负责人的你可以根据候选人的回答进行准确评估。"""
                },
                "技术面试官": {
                    "prompt": """作为技术面试官，你应更关注：
1. 候选人的技术深度和广度
2. 核心技术原理的理解
3. 系统设计和架构能力
4. 代码质量和编程思维
5. 技术问题解决能力

评估时，请详细分析候选人简历中的技术栈、项目经验和技术关键词，
将其与招聘职位要求的技术能力进行针对性匹配。

在设计面试问题时，应基于候选人的实际技术背景和项目经历设计有深度的问题，
确保问题聚焦在与应聘职位最相关的技术领域。""",
                    "structure": """请按照以下结构生成文档：

# 面试指导文档

## 一、候选人技术背景分析
- 技术栈匹配度分析
- 核心技能深度评估
- 技术广度评价
- 专业成长轨迹

## 二、技术能力考察要点
- 核心技术原理理解
- 算法与数据结构掌握
- 系统设计能力
- 代码质量与风格

## 三、项目经验考察
- 技术难点解决经验
- 架构设计思路
- 性能优化经验
- 技术选型判断

## 四、工程实践能力
- 测试与质量保障
- 开发流程与规范
- 问题诊断与调试
- 技术文档能力

## 五、面试问题建议
- 基础技术问题（3-4个）
  * 为每个问题提供参考答案和评分要点
- 项目实战问题（3-4个）
  * 为每个问题提供参考答案和评分要点
- 系统设计问题（3-4个）
  * 为每个问题提供参考答案和评分要点
- 编程实现问题（3-4个）
  * 为每个问题提供参考答案和评分要点

## 六、技术评估标准
- 技术基础评分标准
- 工程能力评分标准
- 架构思维评分标准
- 综合技术评价

请确保问题具有技术深度和广度，并与候选人的技术背景和职位要求紧密结合。每个问题都必须包含详细的参考答案，以便作为技术面试官的你可以根据候选人的回答进行准确评估。"""
                },
                "人事面试官": {
                    "prompt": """作为人事面试官，你应更关注：
1. 候选人的沟通表达能力
2. 团队协作和人际关系处理
3. 职业规划和发展动机
4. 文化契合度和价值观
5. 学习能力和适应能力

评估时，请关注候选人的职业轨迹、跳槽原因、团队角色等信息，
判断其是否符合公司文化和团队氛围。

在设计面试问题时，应结合候选人简历中的经历和职位需求设计情景化问题，
评估候选人在实际工作环境中的软技能表现和适应能力。""",
                    "structure": """请按照以下结构生成文档：

# 面试指导文档

## 一、候选人背景综述
- 职业经历连贯性
- 跳槽频率与原因
- 价值观与企业文化契合
- 职业发展意向评估

## 二、软技能评估要点
- 沟通表达能力
- 团队协作意识
- 压力应对方式
- 学习适应能力

## 三、职业素养考察
- 职业道德与价值观
- 工作责任感
- 时间管理能力
- 职业规划清晰度

## 四、发展潜力评估
- 学习能力与成长意愿
- 自我驱动力
- 创新思维
- 长期职业规划

## 五、面试问题建议
- 职业选择问题（3-4个）
  * 为每个问题提供参考答案和评分要点
- 情景应对问题（3-4个）
  * 为每个问题提供参考答案和评分要点
- 软技能考察问题（3-4个）
  * 为每个问题提供参考答案和评分要点
- 文化契合度问题（3-4个）
  * 为每个问题提供参考答案和评分要点

## 六、综合评估参考
- 软技能评分标准
- 文化契合度评分标准
- 发展潜力评分标准
- 整体录用建议

请确保问题能全面评估候选人的综合素质，重点关注软技能和文化契合度。每个问题都必须包含详细的参考答案，以便作为人事面试官的你可以根据候选人的回答进行准确评估。"""
                },
                "其他": {
                    "prompt": """请根据面试官的具体角色，调整面试关注点和问题设计。

评估时，应全面分析候选人简历与职位要求的匹配度，找出需要重点考察的领域。

确保问题既能考察候选人的专业能力，又能满足特定角色的评估需求，
且所有问题都应直接针对候选人的具体情况和应聘职位制定。""",
                    "structure": """请按照以下结构生成文档：

# 面试指导文档

## 一、候选人背景分析
- 技能匹配度分析
- 经验匹配度分析
- 教育背景评估
- 职业发展轨迹分析

## 二、技术评估要点
- 核心技能考察点
- 技术深度考察建议
- 实践经验验证方向

## 三、项目经验考察
- 项目难点分析建议
- 技术决策考察点
- 项目管理能力评估

## 四、综合素质评估
- 学习能力评估
- 团队协作能力
- 问题解决能力
- 沟通表达能力

## 五、面试问题建议
- 技术基础问题（3-4个）
  * 为每个问题提供参考答案和评分要点
- 项目实践问题（3-4个）
  * 为每个问题提供参考答案和评分要点
- 技术深度问题（3-4个）
  * 为每个问题提供参考答案和评分要点
- 综合素质问题（3-4个）
  * 为每个问题提供参考答案和评分要点

## 六、评估参考标准
- 技术能力评分标准
- 项目经验评分标准
- 综合素质评分标准
- 整体评估建议

请确保建议具有针对性和实用性，并与候选人背景和职位要求紧密结合。每个问题都必须包含详细的参考答案，以便面试官可以根据候选人的回答进行准确评估。"""
                }
            }

            # 获取角色特定的内容
            role_content = role_specific_content.get(request.role, role_specific_content["其他"])
            
            # 构建完整的系统提示词
            system_prompt = f"{base_system_prompt}\n\n{role_content['prompt']}\n\n{role_content['structure']}"

            # 4. 构建主要提示词
            prompt = f"""请为以下面试生成指导文档：

候选人信息：
姓名：{resume.name}
当前职位：{resume.current_position or "未提供"}
工作年限：{resume.experience_years or "未提供"}
最高学历：{resume.highest_education or "未提供"}
技术栈：{self._format_skills(resume.skills)}

工作经历：
{self._format_work_experience(resume.work_experience)}

教育经历：
{self._format_education(resume.education)}

职位信息：
职位名称：{job.title}
部门：{job.department or "未提供"}
职位要求：
{self._format_job_requirements(job.requirements)}

面试官角色：{request.role}

面试关注点：
{request.focusPoints.content}

请根据以上信息，生成一份高度定制化的面试指导文档。特别注意：
1. 面试问题必须基于候选人的具体技术栈和项目经历精确设计
2. 评估要点应直接对应招聘职位的具体要求
3. 所有分析和问题必须与候选人和职位的实际情况紧密结合
4. 根据面试官角色({request.role})定制文档结构和内容深度
5. 确保问题同时具有针对性和深度，不可过于笼统
6. 为每个问题提供针对此候选人情况的参考答案和评分要点"""

            logger.info("提示词构建完成，开始调用LLM服务")

            # 5. 调用LLM服务生成文档
            response = await llm_service.generate_completion(
                prompt=prompt,
                system_prompt=system_prompt,
                db=db,
                max_tokens=3000  # 确保生成足够长的文档，增加token限制以容纳参考答案
            )
            
            logger.info("面试指导文档生成完成")
            
            return {"content": response["content"]}
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"生成面试指导文档失败: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"生成面试指导文档失败: {str(e)}"
            )

    async def stream_interview_guide(
        self,
        db: Session,
        request: InterviewGuideRequest
    ) -> AsyncGenerator[str, None]:
        """流式生成面试指导文档"""
        try:
            logger.info(
                f"开始流式生成面试指导文档: resumeId={request.resumeId}, "
                f"jobId={request.jobId}"
            )
            
            # 1. 获取简历详情
            resume = await resume_service.get_resume_detail(
                db, 
                resume_id=request.resumeId
            )
            if not resume:
                raise HTTPException(status_code=404, detail="简历不存在")
            
            # 2. 获取职位详情
            job = await job_service.get_job_detail(
                db, 
                job_id=request.jobId
            )
            if not job:
                raise HTTPException(status_code=404, detail="职位不存在")
            
            logger.info("成功获取简历和职位信息")
            
            # 3. 构建系统提示词
            base_system_prompt = """你是一位专业的面试指导专家。请根据提供的候选人信息和职位要求，
生成一份详细且高度针对性的面试指导文档。"""

            # 根据面试官角色调整系统提示词和文档结构
            role_specific_content = {
                "部门负责人": {
                    "prompt": """作为部门负责人，你应更关注：
1. 候选人的管理潜力和领导能力
2. 技术视野和战略思维
3. 跨部门协作能力
4. 项目管理和资源调配能力
5. 团队建设和人才培养能力

评估时，请特别关注候选人简历中显示的管理经验、团队规模、项目复杂度等信息，
并与招聘职位的管理要求进行匹配分析。

在设计面试问题时，应重点考察候选人的大局观、决策能力和管理思路，
确保问题针对候选人的具体背景和应聘职位，而不是泛泛而谈。""",
                    "structure": """请按照以下结构生成文档：

# 面试指导文档

## 一、候选人综合评估
- 领导潜力评估
- 管理经验分析
- 技术视野评价
- 职业发展契合度

## 二、管理能力考察要点
- 团队管理经验
- 资源调配能力
- 项目全局把控能力
- 危机处理能力

## 三、技术决策考察
- 技术选型思路
- 架构规划能力
- 技术风险评估
- 技术团队建设

## 四、沟通协作能力
- 跨部门协作经验
- 向上沟通能力
- 团队激励方式
- 冲突处理方法

## 五、面试问题建议
- 管理经验问题（3-4个）
  * 为每个问题提供参考答案和评分要点
- 团队建设问题（3-4个）
  * 为每个问题提供参考答案和评分要点
- 技术战略问题（3-4个）
  * 为每个问题提供参考答案和评分要点
- 领导力问题（3-4个）
  * 为每个问题提供参考答案和评分要点

## 六、评估参考标准
- 领导力评分标准
- 管理能力评分标准
- 战略思维评分标准
- 综合评价和建议

请确保建议具有针对性和实用性，并与候选人背景和职位要求紧密结合。每个问题都必须包含详细的参考答案，以便作为部门负责人的你可以根据候选人的回答进行准确评估。"""
                },
                "技术面试官": {
                    "prompt": """作为技术面试官，你应更关注：
1. 候选人的技术深度和广度
2. 核心技术原理的理解
3. 系统设计和架构能力
4. 代码质量和编程思维
5. 技术问题解决能力

评估时，请详细分析候选人简历中的技术栈、项目经验和技术关键词，
将其与招聘职位要求的技术能力进行针对性匹配。

在设计面试问题时，应基于候选人的实际技术背景和项目经历设计有深度的问题，
确保问题聚焦在与应聘职位最相关的技术领域。""",
                    "structure": """请按照以下结构生成文档：

# 面试指导文档

## 一、候选人技术背景分析
- 技术栈匹配度分析
- 核心技能深度评估
- 技术广度评价
- 专业成长轨迹

## 二、技术能力考察要点
- 核心技术原理理解
- 算法与数据结构掌握
- 系统设计能力
- 代码质量与风格

## 三、项目经验考察
- 技术难点解决经验
- 架构设计思路
- 性能优化经验
- 技术选型判断

## 四、工程实践能力
- 测试与质量保障
- 开发流程与规范
- 问题诊断与调试
- 技术文档能力

## 五、面试问题建议
- 基础技术问题（3-4个）
  * 为每个问题提供参考答案和评分要点
- 项目实战问题（3-4个）
  * 为每个问题提供参考答案和评分要点
- 系统设计问题（3-4个）
  * 为每个问题提供参考答案和评分要点
- 编程实现问题（3-4个）
  * 为每个问题提供参考答案和评分要点

## 六、技术评估标准
- 技术基础评分标准
- 工程能力评分标准
- 架构思维评分标准
- 综合技术评价

请确保问题具有技术深度和广度，并与候选人的技术背景和职位要求紧密结合。每个问题都必须包含详细的参考答案，以便作为技术面试官的你可以根据候选人的回答进行准确评估。"""
                },
                "人事面试官": {
                    "prompt": """作为人事面试官，你应更关注：
1. 候选人的沟通表达能力
2. 团队协作和人际关系处理
3. 职业规划和发展动机
4. 文化契合度和价值观
5. 学习能力和适应能力

评估时，请关注候选人的职业轨迹、跳槽原因、团队角色等信息，
判断其是否符合公司文化和团队氛围。

在设计面试问题时，应结合候选人简历中的经历和职位需求设计情景化问题，
评估候选人在实际工作环境中的软技能表现和适应能力。""",
                    "structure": """请按照以下结构生成文档：

# 面试指导文档

## 一、候选人背景综述
- 职业经历连贯性
- 跳槽频率与原因
- 价值观与企业文化契合
- 职业发展意向评估

## 二、软技能评估要点
- 沟通表达能力
- 团队协作意识
- 压力应对方式
- 学习适应能力

## 三、职业素养考察
- 职业道德与价值观
- 工作责任感
- 时间管理能力
- 职业规划清晰度

## 四、发展潜力评估
- 学习能力与成长意愿
- 自我驱动力
- 创新思维
- 长期职业规划

## 五、面试问题建议
- 职业选择问题（3-4个）
  * 为每个问题提供参考答案和评分要点
- 情景应对问题（3-4个）
  * 为每个问题提供参考答案和评分要点
- 软技能考察问题（3-4个）
  * 为每个问题提供参考答案和评分要点
- 文化契合度问题（3-4个）
  * 为每个问题提供参考答案和评分要点

## 六、综合评估参考
- 软技能评分标准
- 文化契合度评分标准
- 发展潜力评分标准
- 整体录用建议

请确保问题能全面评估候选人的综合素质，重点关注软技能和文化契合度。每个问题都必须包含详细的参考答案，以便作为人事面试官的你可以根据候选人的回答进行准确评估。"""
                },
                "其他": {
                    "prompt": """请根据面试官的具体角色，调整面试关注点和问题设计。

评估时，应全面分析候选人简历与职位要求的匹配度，找出需要重点考察的领域。

确保问题既能考察候选人的专业能力，又能满足特定角色的评估需求，
且所有问题都应直接针对候选人的具体情况和应聘职位制定。""",
                    "structure": """请按照以下结构生成文档：

# 面试指导文档

## 一、候选人背景分析
- 技能匹配度分析
- 经验匹配度分析
- 教育背景评估
- 职业发展轨迹分析

## 二、技术评估要点
- 核心技能考察点
- 技术深度考察建议
- 实践经验验证方向

## 三、项目经验考察
- 项目难点分析建议
- 技术决策考察点
- 项目管理能力评估

## 四、综合素质评估
- 学习能力评估
- 团队协作能力
- 问题解决能力
- 沟通表达能力

## 五、面试问题建议
- 技术基础问题（3-4个）
  * 为每个问题提供参考答案和评分要点
- 项目实践问题（3-4个）
  * 为每个问题提供参考答案和评分要点
- 技术深度问题（3-4个）
  * 为每个问题提供参考答案和评分要点
- 综合素质问题（3-4个）
  * 为每个问题提供参考答案和评分要点

## 六、评估参考标准
- 技术能力评分标准
- 项目经验评分标准
- 综合素质评分标准
- 整体评估建议

请确保建议具有针对性和实用性，并与候选人背景和职位要求紧密结合。每个问题都必须包含详细的参考答案，以便面试官可以根据候选人的回答进行准确评估。"""
                }
            }

            # 获取角色特定的内容
            role_content = role_specific_content.get(request.role, role_specific_content["其他"])
            
            # 构建完整的系统提示词
            system_prompt = f"{base_system_prompt}\n\n{role_content['prompt']}\n\n{role_content['structure']}"

            # 4. 构建主要提示词
            prompt = f"""请为以下面试生成指导文档：

候选人信息：
姓名：{resume.name}
当前职位：{resume.current_position or "未提供"}
工作年限：{resume.experience_years or "未提供"}
最高学历：{resume.highest_education or "未提供"}
技术栈：{self._format_skills(resume.skills)}

工作经历：
{self._format_work_experience(resume.work_experience)}

教育经历：
{self._format_education(resume.education)}

职位信息：
职位名称：{job.title}
部门：{job.department or "未提供"}
职位要求：
{self._format_job_requirements(job.requirements)}

面试官角色：{request.role}

面试关注点：
{request.focusPoints.content}

请根据以上信息，生成一份高度定制化的面试指导文档。特别注意：
1. 面试问题必须基于候选人的具体技术栈和项目经历精确设计
2. 评估要点应直接对应招聘职位的具体要求
3. 所有分析和问题必须与候选人和职位的实际情况紧密结合
4. 根据面试官角色({request.role})定制文档结构和内容深度
5. 确保问题同时具有针对性和深度，不可过于笼统
6. 为每个问题提供针对此候选人情况的参考答案和评分要点"""

            logger.info("提示词构建完成，开始流式生成")

            # 获取LLM配置
            llm_config = await llm_service.get_default_config(db)
            logger.info(f"获取LLM配置成功，使用模型: {llm_config.chat_model}")

            # 5. 调用LLM服务流式生成文档
            async for chunk in llm_service.stream_completion(
                prompt=prompt,
                system_prompt=system_prompt,
                llm_config=llm_config,  # 添加LLM配置参数
                max_tokens=4000  # 确保生成足够长的文档，增加token限制以容纳参考答案
            ):
                yield chunk
            
            logger.info("面试指导文档生成完成")
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"生成面试指导文档失败: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"生成面试指导文档失败: {str(e)}"
            )

# 创建服务实例
interview_ai_service = InterviewAIService()

# 只导出实例
__all__ = ["interview_ai_service"] 