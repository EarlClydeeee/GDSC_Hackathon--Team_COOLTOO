CREATE TABLE IF NOT EXISTS incidents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    incident_type VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    location VARCHAR(255) NOT NULL,
    status ENUM('active', 'resolved', 'pending') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    reported_by VARCHAR(255) NOT NULL,
    contact_email VARCHAR(255),
    contact_phone VARCHAR(20),
    priority ENUM('low', 'medium', 'high', 'urgent') DEFAULT 'medium',
    resolution_notes TEXT,
    assigned_to VARCHAR(255),
    evidence_files JSON
);

-- Add indexes for common queries
CREATE INDEX idx_incident_type ON incidents(incident_type);
CREATE INDEX idx_status ON incidents(status);
CREATE INDEX idx_created_at ON incidents(created_at);
