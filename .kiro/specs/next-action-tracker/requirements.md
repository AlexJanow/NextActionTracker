# Requirements Document

## Introduction

The Next Action Tracker (NAT) is a focused dashboard feature for Sales CRM/ERP systems that addresses pipeline leakage - the critical problem where sales deals are lost not because customers say "no", but because sales representatives forget to proactively plan and execute the next steps. The system ensures every deal has a defined next action with a due date, and forces sales reps to immediately plan the subsequent action when completing the current one.

## Glossary

- **NAT**: Next Action Tracker - the core dashboard feature
- **Sales Rep (AE)**: Account Executive - the sales person managing deals
- **Opportunity**: A sales deal or potential sale in the pipeline
- **Pipeline Leakage**: Lost sales due to inaction rather than customer rejection
- **Tenant**: A customer organization using the multi-tenant CRM system
- **Due Action**: An action that is scheduled for today or overdue

## Requirements

### Requirement 1

**User Story:** As a Sales Rep, I want to see all my deals that have actions due today or overdue, so that I can prioritize my daily work and prevent pipeline leakage.

#### Acceptance Criteria

1. WHEN a Sales Rep accesses the NAT dashboard, THE NAT SHALL display all opportunities where next_action_at is today or in the past
2. THE NAT SHALL order due actions by next_action_at in ascending order (oldest first)
3. THE NAT SHALL display opportunity name, value, stage, and next action details for each due item
4. WHERE no actions are due, THE NAT SHALL display a "All done! 🎉" message
5. THE NAT SHALL filter all data by the Sales Rep's tenant_id to ensure data isolation

### Requirement 2

**User Story:** As a Sales Rep, I want to mark an action as complete and immediately define the next action, so that deals never stagnate without a planned next step.

#### Acceptance Criteria

1. WHEN a Sales Rep clicks "Complete Action" on a due item, THE NAT SHALL open a modal form
2. THE NAT SHALL require both a new action date and action description before allowing submission
3. WHEN the Sales Rep submits the form, THE NAT SHALL update the opportunity with the new next action details
4. THE NAT SHALL update the last_activity_at timestamp to track deal activity
5. WHEN the update is successful, THE NAT SHALL remove the item from the due actions list and close the modal

### Requirement 3

**User Story:** As a Sales Rep, I want the system to track when I last interacted with each deal, so that stagnant opportunities can be identified and addressed.

#### Acceptance Criteria

1. WHEN any action is completed on an opportunity, THE NAT SHALL update the last_activity_at field to the current timestamp
2. THE NAT SHALL store last_activity_at with timezone information for accurate tracking
3. WHEN an opportunity is created, THE NAT SHALL set last_activity_at to the creation time
4. THE NAT SHALL maintain last_activity_at as a non-nullable field for all opportunities

### Requirement 4

**User Story:** As a system administrator, I want tenant data to be properly isolated, so that each organization's sales data remains secure and separate.

#### Acceptance Criteria

1. THE NAT SHALL require a tenant_id for all API operations
2. THE NAT SHALL filter all database queries by tenant_id to ensure data isolation
3. WHEN accessing opportunities, THE NAT SHALL only return data belonging to the specified tenant
4. THE NAT SHALL validate tenant_id on every API request before processing
5. THE NAT SHALL return appropriate error responses for invalid or missing tenant_id values

### Requirement 5

**User Story:** As a Sales Rep, I want the interface to provide clear feedback during actions, so that I know when operations are in progress or have failed.

#### Acceptance Criteria

1. WHEN loading due actions, THE NAT SHALL display a loading indicator
2. WHEN an API error occurs, THE NAT SHALL display a clear error message
3. WHEN completing an action, THE NAT SHALL disable the submit button and show a loading spinner
4. WHEN an action completion fails, THE NAT SHALL display the error and keep the modal open for retry
5. WHEN an action is successfully completed, THE NAT SHALL refresh the dashboard data automatically

### Requirement 6

**User Story:** As a developer, I want regular Git commits to be made during development, so that progress is tracked and code changes can be reviewed incrementally.

#### Acceptance Criteria

1. THE development process SHALL include Git commits after each significant code change
2. THE development process SHALL include descriptive commit messages that explain the changes made
3. THE development process SHALL commit code at logical breakpoints during implementation
4. THE development process SHALL maintain a clean Git history for code review and debugging purposes

### Requirement 7

**User Story:** As a Sales Rep, I want to visually distinguish between different urgency levels of due actions, so that I can quickly identify which deals need immediate attention.

#### Acceptance Criteria

1. WHEN a due action is more than 3 days overdue, THE NAT SHALL display a red visual indicator (#ef4444)
2. WHEN a due action is 1-3 days overdue, THE NAT SHALL display a yellow visual indicator (#eab308)
3. WHEN a due action is due today, THE NAT SHALL display a blue or gray visual indicator (#3b82f6)
4. THE NAT SHALL calculate urgency by comparing next_action_at to the current date
5. THE NAT SHALL apply the visual indicator consistently to all due action cards

### Requirement 8

**User Story:** As a Sales Rep, I want to quickly schedule follow-up actions using preset time intervals, so that I can complete actions faster without manual date calculation.

#### Acceptance Criteria

1. WHEN completing an action, THE NAT SHALL display quick-select buttons for "+1 Week", "+2 Weeks", and "+1 Month"
2. WHEN a quick-select button is clicked, THE NAT SHALL automatically set the date picker to the corresponding future date from today
3. THE NAT SHALL prevent selection of past dates in the date picker
4. THE NAT SHALL validate that new_next_action_at is not in the past before allowing form submission
5. THE NAT SHALL calculate future dates accurately accounting for month boundaries and leap years

### Requirement 9

**User Story:** As a product manager, I want the demo to showcase realistic pipeline scenarios with varied urgency levels, so that potential customers can understand the value proposition immediately.

#### Acceptance Criteria

1. THE seed script SHALL create 5-6 opportunities for a single demo tenant
2. THE seed script SHALL create 1 opportunity with next_action_at 5-7 days in the past (high urgency)
3. THE seed script SHALL create 1 opportunity with next_action_at 2 days in the past (medium urgency)
4. THE seed script SHALL create 1 opportunity with next_action_at set to today (low urgency)
5. THE seed script SHALL create 1 opportunity with next_action_at 1 day in the past (for demo completion flow)
6. THE seed script SHALL create 1 opportunity with next_action_at 3 days in the future (should not appear on dashboard)
7. WHEN the dashboard loads, THE NAT SHALL display only the 4 overdue/due items, excluding future actions