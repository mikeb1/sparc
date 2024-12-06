# Project Structure and Workflow Diagrams

@diagram ProjectFolderStructure {
    @title "Solar Power Plant Project Folder Structure"
    @type "tree"

    Root {
        ConnectionView {
            Index
            CurrentView
            PreviousViews
        }
        Projects {
            Implementation
            TransmissionLine
            SubstationProjects
            TEDASApproval
            AsBuilt
        }
        ProjectComplementary {
            EIA {
                FlowChart
                Tracking
                Opinions
                Documents
            }
            Zoning {
                CurrentMap
                GroundStudy
                DraftPlan
                FlowChart
                Tracking
                Opinions
            }
            Licensing {
                BuildingLicense
                Permits
            }
        }
        Materials {
            Index
            Submissions
            Approved
            Rejected
            DispatchStatus {
                OnSite
                Schedule
                Rejected
            }
        }
        FieldControl {
            DailyReports
            Warnings
            OngoingIssues
        }
        GeneralControl {
            Index
            Reports
            OngoingIssues
        }
        ProgressPayments {
            Index
            Submitted
            Reviewed
            ReadyForSignature
            Invoices
            Contracts
            ComparativeDiscovery
        }
    }
}

@diagram WorkflowDiagrams {
    @title "Core Workflow Processes"
    @type "sequence"

    MaterialApprovalWorkflow {
        Contractor -> System: "Submit Material Approval"
        System -> Consultant: "Review Request"
        Consultant -> System: "Review Feedback"
        alt "Approved" {
            System -> Contractor: "Approval Notification"
            Contractor -> System: "Schedule Dispatch"
            System -> Consultant: "Track Dispatch"
        }
        alt "Rejected" {
            System -> Contractor: "Rejection with Feedback"
            Contractor -> System: "Submit Revision"
        }
    }

    ProgressPaymentWorkflow {
        Contractor -> System: "Submit Progress Payment"
        System -> Consultant: "Review Request"
        Consultant -> System: "Review Report"
        System -> Investor: "Payment Approval Request"
        alt "Approved" {
            Investor -> System: "Approve Payment"
            System -> Contractor: "Generate Invoice"
        }
        alt "Rejected" {
            Investor -> System: "Reject with Reason"
            System -> Contractor: "Revision Request"
        }
    }

    FieldControlWorkflow {
        Consultant -> System: "Submit Field Report"
        System -> Contractor: "Issue Notifications"
        Contractor -> System: "Response/Resolution"
        System -> Investor: "Status Update"
        alt "Issues Resolved" {
            System -> All: "Close Report"
        }
        alt "Outstanding Issues" {
            System -> All: "Track in Ongoing Issues"
        }
    }
}

@diagram StakeholderInteractions {
    @title "Stakeholder Interaction Model"
    @type "component"

    Stakeholders {
        Investor {
            Responsibilities [
                "Project Oversight"
                "Payment Approval"
                "Strategic Decisions"
            ]
            Access [
                "All Reports"
                "Financial Data"
                "Project Status"
            ]
        }
        Contractor {
            Responsibilities [
                "Implementation"
                "Material Management"
                "Progress Reports"
            ]
            Access [
                "Field Reports"
                "Material Status"
                "Payment Status"
            ]
        }
        Consultant {
            Responsibilities [
                "Technical Review"
                "Quality Control"
                "Compliance Check"
            ]
            Access [
                "Technical Documents"
                "Field Data"
                "Approval Workflows"
            ]
        }
    }
}
