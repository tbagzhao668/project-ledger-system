-- 添加项目经理姓名字段到项目表
-- 执行时间: 2025-08-20

-- 1. 添加manager_name字段
ALTER TABLE projects ADD COLUMN manager_name VARCHAR(100);

-- 2. 添加字段注释
COMMENT ON COLUMN projects.manager_name IS '项目经理姓名';

-- 3. 更新现有项目，将创建者姓名设置为项目经理（可选）
-- UPDATE projects 
-- SET manager_name = (
--   SELECT COALESCE(u.username, u.email) 
--   FROM users u 
--   WHERE u.id = projects.created_by
-- )
-- WHERE manager_name IS NULL;

-- 4. 验证字段添加成功
SELECT column_name, data_type, is_nullable, column_default, character_maximum_length
FROM information_schema.columns 
WHERE table_name = 'projects' AND column_name = 'manager_name';

-- 5. 显示更新后的表结构
\d projects;
