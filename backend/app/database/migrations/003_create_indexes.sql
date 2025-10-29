-- Create optimized indexes for Next Action Tracker queries

-- Critical index for NAT dashboard performance
-- Filters by tenant and orders by due date, excludes NULL next_action_at
CREATE INDEX idx_opportunities_tenant_due 
ON opportunities (tenant_id, next_action_at) 
WHERE next_action_at IS NOT NULL;

-- General tenant-based queries index
CREATE INDEX idx_opportunities_tenant_id 
ON opportunities (tenant_id);

-- Index for activity tracking queries
CREATE INDEX idx_opportunities_last_activity 
ON opportunities (tenant_id, last_activity_at);