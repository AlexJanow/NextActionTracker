-- Next Action Tracker Database Initialization
-- This script sets up the basic database structure

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create tenants table
CREATE TABLE IF NOT EXISTS tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create opportunities table
CREATE TABLE IF NOT EXISTS opportunities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    name TEXT NOT NULL,
    value INTEGER,
    stage TEXT NOT NULL,
    next_action_at TIMESTAMPTZ,
    next_action_details TEXT,
    last_activity_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create optimized index for NAT dashboard queries
CREATE INDEX IF NOT EXISTS idx_opportunities_tenant_due 
ON opportunities (tenant_id, next_action_at) 
WHERE next_action_at IS NOT NULL;

-- Create index for tenant-based queries
CREATE INDEX IF NOT EXISTS idx_opportunities_tenant_id 
ON opportunities (tenant_id);

-- Insert demo tenant for development
INSERT INTO tenants (id, name) 
VALUES ('550e8400-e29b-41d4-a716-446655440000', 'Demo Company')
ON CONFLICT (id) DO NOTHING;

-- Insert some demo opportunities for testing
INSERT INTO opportunities (tenant_id, name, value, stage, next_action_at, next_action_details) VALUES
    ('550e8400-e29b-41d4-a716-446655440000', 'Acme Corp Deal', 50000, 'Proposal', NOW() - INTERVAL '1 day', 'Follow up on proposal feedback'),
    ('550e8400-e29b-41d4-a716-446655440000', 'TechStart Partnership', 25000, 'Discovery', NOW(), 'Schedule technical demo'),
    ('550e8400-e29b-41d4-a716-446655440000', 'Enterprise Solutions', 100000, 'Negotiation', NOW() + INTERVAL '2 days', 'Review contract terms'),
    ('550e8400-e29b-41d4-a716-446655440000', 'Small Business Package', 5000, 'Qualified', NOW() - INTERVAL '3 days', 'Send pricing proposal')
ON CONFLICT DO NOTHING;