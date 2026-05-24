-- DDL DB Schema Script for PostgreSQL with JSONB dynamic logs configurations
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(150) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'candidate' NOT NULL,
    aws_credential_secret_b64 VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE interview_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    candidate_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    domain VARCHAR(100) NOT NULL,
    mode VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'In-Progress' NOT NULL,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE,
    history_logs JSONB DEFAULT '[]'::jsonb NOT NULL,
    skills JSONB DEFAULT '[]'::jsonb NOT NULL
);

CREATE TABLE sandbox_resources (
    resource_id VARCHAR(150) PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    interview_id UUID NOT NULL REFERENCES interview_sessions(id) ON DELETE CASCADE,
    provider VARCHAR(50) DEFAULT 'AWS' NOT NULL,
    instance_tier VARCHAR(100) DEFAULT 't3.large' NOT NULL,
    region VARCHAR(100) DEFAULT 'us-east-1' NOT NULL,
    status VARCHAR(50) DEFAULT 'running' NOT NULL,
    hourly_rate NUMERIC(10, 4) DEFAULT 0.0832 NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE sandbox_metrics (
    id SERIAL PRIMARY KEY,
    resource_id VARCHAR(150) NOT NULL REFERENCES sandbox_resources(resource_id) ON DELETE CASCADE,
    cpu_utilization NUMERIC(5, 2) NOT NULL,
    ram_utilization NUMERIC(5, 2) NOT NULL,
    network_egress_bytes BIGINT DEFAULT 0 NOT NULL,
    daily_cost NUMERIC(10, 2) DEFAULT 0.00 NOT NULL,
    is_anomaly BOOLEAN DEFAULT FALSE NOT NULL,
    anomaly_score NUMERIC(5, 4) DEFAULT 0.0000 NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Optimize queries for dynamic candidate history audits and timeseries plots
CREATE INDEX idx_interview_sessions_logs ON interview_sessions USING gin (history_logs);
CREATE INDEX idx_sandbox_metrics_ts ON sandbox_metrics(resource_id, timestamp DESC);
