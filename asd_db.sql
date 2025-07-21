CREATE DATABASE asd_db;
USE asd_db;

-- Users Table
CREATE TABLE Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255),
    role ENUM('parent', 'therapist', 'researcher') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Facial Images Table
CREATE TABLE FacialImages (
    image_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    image_path TEXT NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

-- Predictions Table
CREATE TABLE Predictions (
    prediction_id INT AUTO_INCREMENT PRIMARY KEY,
    image_id INT,
    prediction_result ENUM('ASD', 'Non-ASD'),
    confidence FLOAT,
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (image_id) REFERENCES FacialImages(image_id)
);

-- Analysis Table
CREATE TABLE Analysis (
    analysis_id INT AUTO_INCREMENT PRIMARY KEY,
    total_images INT,
    asd_count INT,
    non_asd_count INT,
    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


