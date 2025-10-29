-- Create opportunities table
-- This table stores sales opportunities with next action tracking

CREATE TABLE opportunities (
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