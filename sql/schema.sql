-- Schema for ПК «Руководитель проектов»
-- MySQL 8.x

CREATE DATABASE IF NOT EXISTS project_manager
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE project_manager;

-- ===== Clients =====
CREATE TABLE IF NOT EXISTS clients (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  phone VARCHAR(50) NULL,
  email VARCHAR(255) NULL,
  note TEXT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ===== Employees =====
CREATE TABLE IF NOT EXISTS employees (
  id INT AUTO_INCREMENT PRIMARY KEY,
  last_name VARCHAR(120) NOT NULL,
  first_name VARCHAR(120) NOT NULL,
  middle_name VARCHAR(120) NULL,
  position VARCHAR(120) NOT NULL,
  phone VARCHAR(50) NULL,
  email VARCHAR(255) NULL,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_employees_active (is_active),
  INDEX idx_employees_name (last_name, first_name)
);

-- ===== Projects =====
CREATE TABLE IF NOT EXISTS projects (
  id INT AUTO_INCREMENT PRIMARY KEY,
  client_id INT NOT NULL,
  name VARCHAR(255) NOT NULL,
  description TEXT NULL,
  start_date DATE NOT NULL,
  end_date DATE NULL,
  status ENUM('Planned','Active','Completed','OnHold','Canceled') NOT NULL DEFAULT 'Active',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_projects_client
    FOREIGN KEY (client_id) REFERENCES clients(id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,
  INDEX idx_projects_client (client_id),
  INDEX idx_projects_status (status),
  INDEX idx_projects_dates (start_date, end_date)
);

-- ===== Project members (employees involved in a project) =====
CREATE TABLE IF NOT EXISTS project_members (
  project_id INT NOT NULL,
  employee_id INT NOT NULL,
  role VARCHAR(120) NOT NULL DEFAULT 'Member',
  since_date DATE NOT NULL,
  PRIMARY KEY (project_id, employee_id),
  CONSTRAINT fk_members_project
    FOREIGN KEY (project_id) REFERENCES projects(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT fk_members_employee
    FOREIGN KEY (employee_id) REFERENCES employees(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  INDEX idx_members_employee (employee_id)
);

-- ===== Tasks =====
CREATE TABLE IF NOT EXISTS tasks (
  id INT AUTO_INCREMENT PRIMARY KEY,
  project_id INT NOT NULL,
  employee_id INT NULL,
  title VARCHAR(255) NOT NULL,
  description TEXT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  due_date DATE NOT NULL,
  completed_at DATETIME NULL,
  status ENUM('New','InProgress','Done','Canceled') NOT NULL DEFAULT 'New',
  CONSTRAINT fk_tasks_project
    FOREIGN KEY (project_id) REFERENCES projects(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT fk_tasks_employee
    FOREIGN KEY (employee_id) REFERENCES employees(id)
    ON DELETE SET NULL
    ON UPDATE CASCADE,
  INDEX idx_tasks_project (project_id),
  INDEX idx_tasks_employee (employee_id),
  INDEX idx_tasks_due (due_date),
  INDEX idx_tasks_status (status)
);


