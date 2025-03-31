-- 创建数据库
CREATE DATABASE IF NOT EXISTS waf;
USE waf;

-- IP记录表
CREATE TABLE IF NOT EXISTS ip_records (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    ip VARCHAR(50) NOT NULL,
    ja3 VARCHAR(100),
    country VARCHAR(50),
    rule_id VARCHAR(100),
    location VARCHAR(255),
    count INT,
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_ip (ip),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);

-- JA3指纹记录表
CREATE TABLE IF NOT EXISTS ja3_records (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    ja3 VARCHAR(100) NOT NULL,
    ip_count INT,
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_ja3 (ja3),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);

-- IP分析记录表
CREATE TABLE IF NOT EXISTS ip_analysis (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    ip VARCHAR(50) NOT NULL,
    ja3 VARCHAR(100),
    country VARCHAR(50),
    count INT,
    analysis TEXT,
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_ip (ip),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);