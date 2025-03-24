import json
import asyncio
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import BackgroundTasks
import logging

from app import crud, models, schemas
from app.services.llm_service import llm_service
from app.services.job_application_service import job_application_service

# 设置日志
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# 添加控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# 设置日志格式
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
console_handler.setFormatter(formatter)

# 添加处理器到logger
if not logger.handlers:  # 避免重复添加处理器
    logger.addHandler(console_handler)


class ResumeJobMatchingService:
    """简历与职位匹配服务"""
    
    async def analyze_and_update_match(
        self,
        db: Session,
        application_id: int
    ) -> Dict[str, Any]:
        """分析简历与职位的匹配度并更新结果"""
        logger.debug("开始分析简历与职位匹配: 申请ID=%s", application_id)
        try:
            # 获取申请信息
            application = crud.job_application.get(db=db, id=application_id)
            if not application:
                logger.error("找不到职位申请: ID=%s", application_id)
                return {"success": False, "error": "找不到职位申请"}
            
            # 获取职位和简历信息
            job = crud.job.get(db=db, id=application.job_id)
            resume = crud.resume.get(db=db, id=application.resume_id)
            
            # 构建提示词
            prompt = self._build_match_prompt(job, resume)
            
            # 调用LLM服务
            response = await llm_service.generate_completion(
                prompt=prompt,
                system_prompt="你是一个专业的人才匹配专家",
                db=db  # 传入数据库会话，让服务内部获取配置
            )
            
            # 解析结果并更新申请
            match_result = self._parse_llm_response(response["content"])
            application_update = schemas.JobApplicationUpdate(
                match_score=match_result["score"],
                match_reason=match_result["reason"]
            )
            
            # 更新申请
            job_application_service.update_application(
                db=db,
                application_id=application_id,
                application_in=application_update
            )
            
            logger.info(
                "完成简历与职位匹配分析: 申请ID=%s, 分数=%s",
                application_id,
                match_result["score"]
            )
            return match_result
            
        except Exception as e:
            logger.error(
                "匹配分析失败: 申请ID=%s, 错误=%s",
                application_id,
                str(e),
                exc_info=True
            )
            return {"success": False, "error": str(e)}
    
    def _build_match_prompt(self, job: models.Job, resume: models.Resume) -> str:
        """构建匹配分析提示词"""
        # 提取职位信息
        job_info = {
            "title": job.title,
            "job_type": job.job_type,
            "headcount": job.headcount,
            "salary_range": (
                f"{job.salary_min}-{job.salary_max} "
                f"({job.salary_type})"
            ),
            "location": job.location,
            "experience_required": job.experience_required,
            "education_required": job.education_required,
            "description": job.description,
            "requirements": job.requirements,
            "benefits": job.benefits
        }
        
        # 提取简历信息
        resume_info = {
            "name": resume.name,
            "gender": resume.gender,
            "age": resume.birthdate,  # 年龄需要计算
            "education": {
                "highest_education": resume.highest_education,
                "highest_degree": resume.highest_degree,
                "major": resume.major,
                "graduate_school": resume.graduate_school,
                "graduation_date": resume.graduation_date
            },
            "experience": {
                "years": resume.experience_years,
                "current_company": resume.current_company,
                "current_position": resume.current_position,
                "current_salary": resume.current_salary,
                "work_history": resume.work_history
            },
            "job_intention": {
                "expected_position": resume.expected_position,
                "expected_salary": resume.expected_salary,
                "expected_location": resume.expected_location
            },
            "skills": resume.skills,
            "certificates": resume.certificates,
            "english_level": resume.english_level
        }
        
        # 构建提示词
        prompt = f"""
请分析以下职位需求与候选人简历的匹配程度，并给出匹配分数（0-100分）和详细的匹配理由。

## 职位信息
- 职位名称: {job_info['title']}
- 工种类型: {job_info['job_type']}
- 招聘人数: {job_info['headcount']}
- 薪资范围: {job_info['salary_range']}
- 工作地点: {job_info['location']}
- 经验要求: {job_info['experience_required']}
- 学历要求: {job_info['education_required']}
- 职位描述: {job_info['description']}
- 岗位要求: {job_info['requirements']}
- 福利待遇: {job_info['benefits']}

## 候选人信息
### 基本信息
- 姓名: {resume_info['name']}
- 性别: {resume_info['gender']}
- 年龄: {resume_info['age']}
- 英语水平: {resume_info['english_level']}

### 教育背景
- 最高学历: {resume_info['education']['highest_education']}
- 最高学位: {resume_info['education']['highest_degree']}
- 专业: {resume_info['education']['major']}
- 毕业院校: {resume_info['education']['graduate_school']}
- 毕业时间: {resume_info['education']['graduation_date']}

### 工作经验
- 工作年限: {resume_info['experience']['years']}年
- 目前公司: {resume_info['experience']['current_company']}
- 目前职位: {resume_info['experience']['current_position']}
- 目前薪资: {resume_info['experience']['current_salary']}
- 工作经历: {resume_info['experience']['work_history']}

### 求职意向
- 期望职位: {resume_info['job_intention']['expected_position']}
- 期望薪资: {resume_info['job_intention']['expected_salary']}
- 期望地点: {resume_info['job_intention']['expected_location']}

### 技能与证书
- 技能: {resume_info['skills']}
- 证书: {resume_info['certificates']}

请根据以上信息，全面分析该候选人与职位的匹配程度。重点考虑以下方面：
1. 教育背景与要求的匹配度
2. 工作经验与要求的匹配度
3. 技能与岗位要求的匹配度
4. 求职意向与职位条件的匹配度
5. 薪资期望的匹配度

请按照以下JSON格式返回结果：
{{
    "score": 85,  // 0-100的整数
    "reason": "详细的匹配分析理由..."
}}
"""
        return prompt
    
    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """解析LLM响应"""
        logger.debug("开始解析LLM响应，原始响应文本: %s", response_text)
        try:
            def clean_json_text(text: str) -> str:
                """清理JSON文本，移除控制字符并规范化换行符"""
                # 将Windows换行符转换为Unix换行符
                text = text.replace('\r\n', '\n')
                # 移除不可见的控制字符，但保留换行符
                return ''.join(char for char in text if char >= ' ' or char == '\n')

            # 尝试直接解析JSON
            try:
                logger.debug("尝试直接解析JSON")
                cleaned_text = clean_json_text(response_text)
                result = json.loads(cleaned_text)
                if "score" in result and "reason" in result:
                    logger.debug("成功直接解析JSON: %s", result)
                    score = float(result["score"])
                    score = max(0, min(100, score))
                    return {
                        "score": score,
                        "reason": result["reason"]
                    }
                else:
                    logger.debug("JSON缺少必要字段 score 或 reason: %s", result)
            except json.JSONDecodeError as e:
                logger.debug("直接JSON解析失败: %s", str(e))
            
            # 如果直接解析失败，尝试从文本中提取JSON部分
            import re
            logger.debug("尝试从文本中提取JSON")
            # 使用非贪婪模式匹配，避免匹配到多个JSON对象
            json_pattern = r'({[^{]*?})'
            matches = re.finditer(json_pattern, response_text)
            
            for match in matches:
                try:
                    json_str = clean_json_text(match.group(1))
                    logger.debug("尝试解析JSON字符串: %s", json_str)
                    result = json.loads(json_str)
                    if "score" in result and "reason" in result:
                        logger.debug("成功解析提取的JSON: %s", result)
                        score = float(result["score"])
                        score = max(0, min(100, score))
                        return {
                            "score": score,
                            "reason": result["reason"]
                        }
                except json.JSONDecodeError as e:
                    logger.debug("当前JSON解析失败，尝试下一个: %s", str(e))
                    continue
            
            logger.debug("未能从文本中提取有效的JSON")
            
            # 如果仍然无法解析，尝试提取分数和理由
            logger.debug("尝试使用正则表达式提取分数和理由")
            # 扩展分数匹配模式
            score_patterns = [
                r'匹配分数[：:]\s*(\d+)',
                r'"score"\s*:\s*(\d+)',
                r'分数[：:]\s*(\d+)',
            ]
            
            score = 0
            for pattern in score_patterns:
                score_match = re.search(pattern, response_text)
                if score_match:
                    logger.debug("找到分数匹配: %s", score_match.group(1))
                    score = float(score_match.group(1))
                    score = max(0, min(100, score))
                    break
            
            # 提取理由
            reason_patterns = [
                r'"reason"\s*:\s*"([^"]+)"',
                r'理由[：:]([\s\S]+?)(?=\n\n|$)',
            ]
            
            reason = None
            for pattern in reason_patterns:
                reason_match = re.search(pattern, response_text)
                if reason_match:
                    reason = reason_match.group(1).strip()
                    logger.debug("找到理由匹配: %s", reason)
                    break
            
            if not reason:
                # 如果没有找到明确的理由，使用整个响应文本
                reason = response_text.strip()
            
            result = {
                "score": score,
                "reason": reason if reason else "无法提取匹配理由"
            }
            logger.debug("最终解析结果: %s", result)
            return result
            
        except Exception as e:
            logger.error("解析LLM响应时发生异常: %s", str(e), exc_info=True)
            return {
                "score": 0,
                "reason": f"解析匹配结果失败: {str(e)}"
            }
    
    async def background_analyze_match(
        self,
        db: Session,
        application_id: int
    ) -> None:
        """后台分析简历与职位的匹配度"""
        logger.debug("开始执行后台匹配分析: 申请ID=%s", application_id)
        try:
            # 确保数据库会话可用
            if not db.is_active:
                logger.warning("数据库会话已关闭，创建新会话")
                from app.db.session import SessionLocal
                db = SessionLocal()
            
            # 获取申请信息
            application = crud.job_application.get(db=db, id=application_id)
            if not application:
                logger.error("找不到职位申请: ID=%s", application_id)
                return
                
            logger.debug(
                "获取到职位申请信息: ID=%s, 职位ID=%s, 简历ID=%s",
                application_id,
                application.job_id,
                application.resume_id
            )
            
            # 执行匹配分析
            result = await self.analyze_and_update_match(db, application_id)
            logger.debug("匹配分析结果: %s", result)
            
            logger.info("完成简历与职位匹配分析: 申请ID=%s", application_id)
            
        except Exception as e:
            logger.error(
                "简历与职位匹配分析失败: 申请ID=%s, 错误=%s",
                application_id,
                str(e),
                exc_info=True
            )
            raise
        finally:
            # 确保关闭数据库会话
            db.close()
    
    def schedule_match_analysis(
        self,
        background_tasks: BackgroundTasks,
        db: Session,
        application_id: int
    ) -> None:
        """调度匹配分析任务"""
        logger.debug("准备调度匹配分析任务: 申请ID=%s", application_id)
        try:
            # 获取应用ID，避免在后台任务中使用已关闭的会话
            application = crud.job_application.get(db=db, id=application_id)
            if not application:
                raise ValueError(f"找不到职位申请: ID={application_id}")
            
            # 在后台任务中创建新的数据库会话
            from app.api import deps  # 导入数据库依赖
            
            async def _run_background_task():
                try:
                    logger.info("开始执行后台任务: 申请ID=%s", application_id)
                    # 使用依赖注入获取数据库会话
                    async_db = next(deps.get_db())
                    try:
                        await self.background_analyze_match(async_db, application_id)
                        logger.info("后台任务执行完成: 申请ID=%s", application_id)
                    except Exception as e:
                        logger.error(
                            "后台任务执行失败: 申请ID=%s, 错误=%s",
                            application_id,
                            str(e),
                            exc_info=True
                        )
                        # 更新申请状态为失败
                        try:
                            job_application_service.update_application(
                                db=async_db,
                                application_id=application_id,
                                application_in=schemas.JobApplicationUpdate(
                                    status="failed",
                                    error_message=str(e)
                                )
                            )
                        except Exception as update_error:
                            logger.error(
                                "更新申请状态失败: 申请ID=%s, 错误=%s",
                                application_id,
                                str(update_error)
                            )
                    finally:
                        async_db.close()
                        logger.debug("数据库会话已关闭: 申请ID=%s", application_id)
                except Exception as e:
                    logger.error(
                        "后台任务完全失败: 申请ID=%s, 错误=%s",
                        application_id,
                        str(e),
                        exc_info=True
                    )
            
            # 添加后台任务
            background_tasks.add_task(_run_background_task)
            logger.info("已成功调度简历与职位匹配分析任务: 申请ID=%s", application_id)
            
        except Exception as e:
            logger.error(
                "调度匹配分析任务失败: 申请ID=%s, 错误=%s",
                application_id,
                str(e)
            )
            raise


# 创建服务实例
resume_job_matching_service = ResumeJobMatchingService()

# 只导出实例
__all__ = ["resume_job_matching_service"] 