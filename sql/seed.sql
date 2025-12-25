USE project_manager;

-- Clients
INSERT INTO clients (name, phone, email, note)
VALUES
  ('ООО Альфа', '+7 900 000-00-01', 'alpha@example.com', 'Ключевой клиент'),
  ('АО Бета', '+7 900 000-00-02', 'beta@example.com', NULL);

-- Employees
INSERT INTO employees (last_name, first_name, middle_name, position, phone, email, is_active)
VALUES
  ('Иванов', 'Иван', 'Иванович', 'Разработчик', '+7 911 111-11-11', 'ivanov@example.com', 1),
  ('Петров', 'Пётр', 'Петрович', 'Тестировщик', '+7 922 222-22-22', 'petrov@example.com', 1),
  ('Сидорова', 'Анна', 'Сергеевна', 'Аналитик', '+7 933 333-33-33', 'sidorova@example.com', 1);

-- Projects
INSERT INTO projects (client_id, name, description, start_date, end_date, status)
VALUES
  (1, 'CRM для Альфа', 'Разработка CRM системы', '2025-10-01', NULL, 'Active'),
  (2, 'Сайт для Бета', 'Лендинг + админка', '2025-09-15', '2025-12-30', 'Active');

-- Members
INSERT INTO project_members (project_id, employee_id, role, since_date)
VALUES
  (1, 1, 'Backend', '2025-10-01'),
  (1, 3, 'Analyst', '2025-10-01'),
  (2, 2, 'QA', '2025-09-15'),
  (2, 1, 'Dev', '2025-09-15');

-- Tasks
-- В проекте 1 есть просроченная задача (для проверки отчёта)
INSERT INTO tasks (project_id, employee_id, title, description, due_date, status, completed_at)
VALUES
  (1, 1, 'Сделать модели данных', 'Проектирование таблиц и связей', '2025-10-10', 'Done', '2025-10-09 18:00:00'),
  (1, 1, 'Реализовать API', 'CRUD для основных сущностей', '2025-10-20', 'InProgress', NULL),
  (1, 3, 'Собрать требования', 'Интервью с заказчиком', '2025-10-05', 'InProgress', NULL),
  (2, 2, 'Тест-план', 'Подготовить план тестирования', '2025-12-10', 'New', NULL);


