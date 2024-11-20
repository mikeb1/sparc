# Type Definitions for Solar Power Plant Project Management System

@type ProjectType {
    IMPLEMENTATION
    TRANSMISSION_LINE
    SUBSTATION
    TEDAS_APPROVAL
    AS_BUILT
}

@type ProjectStatus {
    PLANNING
    IN_PROGRESS
    UNDER_REVIEW
    APPROVED
    COMPLETED
    ON_HOLD
}

@type DocumentType {
    CONNECTION_VIEW
    EIA_DOCUMENT
    ZONING_PLAN
    LICENSE
    MATERIAL_APPROVAL
    FIELD_CONTROL
    PROGRESS_PAYMENT
    CONTRACT
    INVOICE
}

@type DocumentStatus {
    DRAFT
    SUBMITTED
    UNDER_REVIEW
    APPROVED
    REJECTED
    ARCHIVED
}

@type ViewStatus {
    CURRENT
    SUPERSEDED
    ARCHIVED
}

@type ConstructionPhase {
    PLANNING
    FOUNDATION
    STRUCTURAL
    ELECTRICAL
    TESTING
    COMMISSIONING
}

@type ApprovalType {
    TEDAS
    ENVIRONMENTAL
    ZONING
    CONSTRUCTION
    OPERATIONAL
}

@type ApprovalStatus {
    PENDING
    IN_REVIEW
    APPROVED
    REJECTED
    REVISION_REQUIRED
}

@type TrackingStatus {
    NOT_STARTED
    IN_PROGRESS
    COMPLETED
    DELAYED
    ON_HOLD
}

@type DispatchStatus {
    PENDING
    IN_TRANSIT
    DELIVERED
    REJECTED
    RETURNED
}

@type PaymentStatus {
    DRAFT
    SUBMITTED
    UNDER_REVIEW
    APPROVED
    REJECTED
    PAID
}

@type ReviewStatus {
    PENDING
    IN_PROGRESS
    COMPLETED
    REVISION_REQUIRED
}

@type ContractType {
    CONSTRUCTION
    CONSULTANCY
    MAINTENANCE
    SUPPLY
}

@type StakeholderRole {
    INVESTOR
    CONTRACTOR
    CONSULTANT
    APPROVER
    PROJECT_MANAGER
}

@type Location {
    ON_SITE
    IN_TRANSIT
    WAREHOUSE
    SUPPLIER
}

@type Result {
    success: Boolean
    message: String
    timestamp: DateTime
}

@type SubmissionResult extends Result {
    documentId: Optional<String>
}

@type ApprovalResult extends Result {
    approvalId: String
    approvalDate: DateTime
}

@type RejectionResult extends Result {
    rejectionReason: String
    rejectionDate: DateTime
}

@type ReviewResult extends Result {
    reviewId: String
    reviewDate: DateTime
    comments: [String]
}

@type MaterialSpecifications {
    name: String
    description: String
    quantity: Number
    specifications: String
    supplier: String
    estimatedDeliveryDate: DateTime
}

@type DocumentMetadata {
    author: String
    version: String
    category: String
    tags: [String]
    createdAt: DateTime
    lastModified: DateTime
}

@type ProjectFilters {
    type: Optional<ProjectType>
    status: Optional<ProjectStatus>
    dateRange: Optional<DateRange>
    stakeholder: Optional<String>
}

@type DateRange {
    startDate: DateTime
    endDate: DateTime
}

@type Issue {
    id: String
    title: String
    description: String
    priority: Priority
    status: IssueStatus
    assignee: Optional<String>
    createdAt: DateTime
    updatedAt: DateTime
}

@type Priority {
    LOW
    MEDIUM
    HIGH
    CRITICAL
}

@type IssueStatus {
    OPEN
    IN_PROGRESS
    RESOLVED
    CLOSED
}
