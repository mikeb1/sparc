# Technical Architecture and Implementation Diagrams

@diagram SystemArchitecture {
    @title "System Architecture Overview"
    @type "component"

    Frontend {
        WebInterface {
            Components [
                "Dashboard"
                "Project Explorer"
                "Document Manager"
                "Workflow Controls"
            ]
        }
        MobileInterface {
            Components [
                "Field Reports"
                "Status Updates"
                "Notifications"
            ]
        }
    }

    Backend {
        APIGateway {
            Services [
                "Authentication"
                "Request Routing"
                "Rate Limiting"
                "Caching"
            ]
        }
        CoreServices {
            ProjectManagement [
                "Project CRUD"
                "Status Tracking"
                "Workflow Engine"
            ]
            DocumentManagement [
                "Version Control"
                "Storage Management"
                "Search Index"
            ]
            WorkflowEngine [
                "State Machine"
                "Process Orchestration"
                "Event Processing"
            ]
        }
        Infrastructure {
            Database [
                "Project Data"
                "User Data"
                "Audit Logs"
            ]
            Storage [
                "Document Store"
                "File System"
                "Backup System"
            ]
            MessageQueue [
                "Event Bus"
                "Task Queue"
                "Notifications"
            ]
        }
    }
}

@diagram DataModel {
    @title "Core Data Model"
    @type "entity"

    Project {
        Attributes [
            "id: UUID"
            "name: String"
            "type: ProjectType"
            "status: ProjectStatus"
            "location: String"
            "startDate: DateTime"
            "endDate: DateTime"
        ]
        Relations [
            "documents: [Document]"
            "stakeholders: [Stakeholder]"
            "materials: [Material]"
            "payments: [Payment]"
        ]
    }

    Document {
        Attributes [
            "id: UUID"
            "name: String"
            "type: DocumentType"
            "version: String"
            "status: DocumentStatus"
            "path: String"
            "metadata: JSON"
        ]
        Relations [
            "project: Project"
            "approvals: [Approval]"
            "revisions: [Revision]"
        ]
    }

    Material {
        Attributes [
            "id: UUID"
            "name: String"
            "specifications: JSON"
            "quantity: Number"
            "status: MaterialStatus"
            "location: String"
        ]
        Relations [
            "project: Project"
            "approvals: [Approval]"
            "dispatches: [Dispatch]"
        ]
    }

    Payment {
        Attributes [
            "id: UUID"
            "amount: Decimal"
            "type: PaymentType"
            "status: PaymentStatus"
            "date: DateTime"
            "details: JSON"
        ]
        Relations [
            "project: Project"
            "approvals: [Approval]"
            "invoices: [Invoice]"
        ]
    }
}

@diagram SecurityModel {
    @title "Security Architecture"
    @type "component"

    Authentication {
        Components [
            "OAuth2 Provider"
            "JWT Service"
            "2FA System"
        ]
        Flows [
            "User Login"
            "Token Generation"
            "Session Management"
        ]
    }

    Authorization {
        RBAC {
            Roles [
                "System Admin"
                "Project Manager"
                "Contractor"
                "Consultant"
                "Viewer"
            ]
            Permissions [
                "Create/Edit Projects"
                "Approve Documents"
                "View Reports"
                "Manage Users"
            ]
        }
        ResourceAccess {
            Policies [
                "Document Access"
                "Payment Approval"
                "Report Generation"
            ]
            Enforcement [
                "API Gateway"
                "Service Layer"
                "Database Layer"
            ]
        }
    }
}

@diagram DeploymentArchitecture {
    @title "System Deployment Architecture"
    @type "deployment"

    Cloud {
        WebServers {
            Components [
                "Load Balancer"
                "Web Applications"
                "Static Content"
            ]
            Config [
                "Auto Scaling"
                "Health Checks"
                "SSL/TLS"
            ]
        }
        ApplicationServers {
            Components [
                "API Services"
                "Background Workers"
                "Cache Servers"
            ]
            Config [
                "Container Orchestration"
                "Service Discovery"
                "Log Aggregation"
            ]
        }
        Storage {
            Components [
                "Database Cluster"
                "Object Storage"
                "Backup Systems"
            ]
            Config [
                "Replication"
                "Backup Schedule"
                "Data Retention"
            ]
        }
    }

    Monitoring {
        Systems [
            "Performance Metrics"
            "Error Tracking"
            "Audit Logs"
        ]
        Alerts [
            "System Health"
            "Security Events"
            "Resource Usage"
        ]
    }
}

@diagram WorkflowImplementation {
    @title "Workflow Implementation Details"
    @type "sequence"

    MaterialApproval {
        States [
            "DRAFT"
            "SUBMITTED"
            "UNDER_REVIEW"
            "APPROVED"
            "REJECTED"
        ]
        Events [
            "submit"
            "review"
            "approve"
            "reject"
            "revise"
        ]
        Actions [
            "Validate Input"
            "Update Status"
            "Notify Stakeholders"
            "Generate Documents"
        ]
    }

    DocumentControl {
        States [
            "CREATED"
            "IN_REVIEW"
            "APPROVED"
            "ARCHIVED"
        ]
        Events [
            "submit"
            "review"
            "approve"
            "archive"
        ]
        Actions [
            "Version Control"
            "Access Control"
            "Audit Logging"
            "Notification"
        ]
    }

    PaymentProcessing {
        States [
            "INITIATED"
            "REVIEWED"
            "APPROVED"
            "PROCESSED"
        ]
        Events [
            "submit"
            "review"
            "approve"
            "process"
        ]
        Actions [
            "Amount Validation"
            "Document Check"
            "Payment Processing"
            "Record Keeping"
        ]
    }
}
