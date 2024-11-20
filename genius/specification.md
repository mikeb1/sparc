# Solar Power Plant Project Management System

@description A comprehensive project management and control processes tracking software for Solar Power Plant (SPP) projects that enables monitoring of project stakeholders, including investor representatives and consultancy service providers.

@module ProjectStructure {
    @description Manages the hierarchical organization of project folders and documents
    
    @type FolderStructure {
        id: String
        name: String
        path: String
        subfolders: [FolderStructure]
        documents: [Document]
        index: Optional<String>
    }

    @type Document {
        id: String
        name: String
        type: DocumentType
        version: String
        status: DocumentStatus
        lastModified: DateTime
        content: String
    }
}

@module ConnectionView {
    @description Manages connection views and their revisions
    
    @type ConnectionView {
        id: String
        version: String
        date: DateTime
        status: ViewStatus
        revisionReason: Optional<String>
    }
}

@module ProjectTypes {
    @description Defines different types of projects and their specific requirements
    
    @type ImplementationProject extends Project {
        implementationDetails: String
        constructionPhase: ConstructionPhase
    }

    @type TransmissionProject extends Project {
        lineSpecifications: String
        substationDetails: String
    }

    @type ApprovalProject extends Project {
        approvalType: ApprovalType
        approvalStatus: ApprovalStatus
    }

    @type AsBuiltProject extends Project {
        completionDate: DateTime
        asBuiltDocuments: [Document]
    }
}

@module DocumentControl {
    @description Manages project documentation and approval workflows
    
    @type EIADocument {
        flowChart: FlowChart
        institutionOpinions: [Opinion]
        trackingStatus: TrackingStatus
    }

    @type ZoningDocument {
        currentMap: Document
        groundStudyReport: Document
        zoningPlan: Document
        institutionOpinions: [Opinion]
    }
}

@module MaterialManagement {
    @description Handles material approvals and tracking
    
    @type MaterialApproval {
        id: String
        material: Material
        status: ApprovalStatus
        submissionDate: DateTime
        approvalDate: Optional<DateTime>
        catalogs: [Document]
    }

    @type Material {
        id: String
        name: String
        specifications: String
        quantity: Number
        location: Location
        dispatchStatus: DispatchStatus
    }
}

@module ProgressTracking {
    @description Manages progress payments and financial tracking
    
    @type ProgressPayment {
        id: String
        amount: Number
        period: String
        status: PaymentStatus
        attachments: [Document]
        reviewStatus: ReviewStatus
    }

    @type Contract {
        id: String
        type: ContractType
        startDate: DateTime
        endDate: DateTime
        value: Number
        terms: String
    }
}

@interface ProjectManagement {
    @description Interface for project management operations

    createProject(name: String, type: ProjectType): Project
    updateProjectStatus(projectId: String, status: ProjectStatus): Boolean
    addDocument(projectId: String, document: Document): Boolean
    assignStakeholder(projectId: String, stakeholderId: String, role: StakeholderRole): Boolean
}

@interface DocumentWorkflow {
    @description Interface for document workflow management

    submitDocument(document: Document): SubmissionResult
    approveDocument(documentId: String, approverId: String): ApprovalResult
    rejectDocument(documentId: String, approverId: String, reason: String): RejectionResult
    trackDocumentStatus(documentId: String): DocumentStatus
}

@interface MaterialApprovalWorkflow {
    @description Interface for material approval process

    submitMaterialApproval(material: Material, documents: [Document]): SubmissionResult
    reviewMaterialApproval(approvalId: String, decision: ApprovalDecision): ReviewResult
    updateDispatchStatus(materialId: String, status: DispatchStatus): Boolean
}

@interface ProgressPaymentWorkflow {
    @description Interface for progress payment processing

    submitProgressPayment(payment: ProgressPayment): SubmissionResult
    reviewPayment(paymentId: String): ReviewResult
    approvePayment(paymentId: String, approverId: String): ApprovalResult
    generateInvoice(paymentId: String): Invoice
}
