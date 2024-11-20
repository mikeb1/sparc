# Interface Definitions for Solar Power Plant Project Management System

@interface ProjectManagement {
    @description Core project management operations

    createProject(
        name: String,
        type: ProjectType,
        location: String,
        startDate: DateTime
    ): Project

    updateProject(
        projectId: String,
        updates: ProjectUpdates
    ): UpdateResult

    archiveProject(
        projectId: String,
        reason: String
    ): ArchiveResult

    getProjectStatus(
        projectId: String
    ): ProjectStatus

    listProjects(
        filters: ProjectFilters
    ): [Project]
}

@interface DocumentManagement {
    @description Document management and version control

    uploadDocument(
        projectId: String,
        document: Document,
        metadata: DocumentMetadata
    ): UploadResult

    updateDocument(
        documentId: String,
        updates: DocumentUpdates
    ): UpdateResult

    getDocumentVersion(
        documentId: String,
        version: String
    ): Document

    listDocuments(
        projectId: String,
        filters: DocumentFilters
    ): [Document]

    archiveDocument(
        documentId: String,
        reason: String
    ): ArchiveResult
}

@interface MaterialApproval {
    @description Material approval workflow management

    submitMaterialApproval(
        projectId: String,
        material: Material,
        specifications: MaterialSpecifications
    ): SubmissionResult

    reviewMaterialApproval(
        approvalId: String,
        reviewDetails: ReviewDetails
    ): ReviewResult

    updateMaterialStatus(
        materialId: String,
        status: MaterialStatus,
        notes: String
    ): UpdateResult

    trackMaterial(
        materialId: String
    ): MaterialTrackingInfo

    generateMaterialReport(
        projectId: String,
        filters: MaterialFilters
    ): MaterialReport
}

@interface ProgressPayment {
    @description Progress payment processing

    createProgressPayment(
        projectId: String,
        payment: ProgressPayment
    ): PaymentResult

    reviewProgressPayment(
        paymentId: String,
        reviewDetails: ReviewDetails
    ): ReviewResult

    approvePayment(
        paymentId: String,
        approvalDetails: ApprovalDetails
    ): ApprovalResult

    generateInvoice(
        paymentId: String
    ): Invoice

    trackPaymentStatus(
        paymentId: String
    ): PaymentStatus
}

@interface FieldControl {
    @description Field control and monitoring

    submitFieldReport(
        projectId: String,
        report: FieldReport,
        attachments: [Attachment]
    ): SubmissionResult

    reviewFieldReport(
        reportId: String,
        reviewDetails: ReviewDetails
    ): ReviewResult

    trackIssues(
        projectId: String,
        status: IssueStatus
    ): [Issue]

    updateIssueStatus(
        issueId: String,
        status: IssueStatus,
        resolution: Optional<String>
    ): UpdateResult

    generateFieldReport(
        projectId: String,
        dateRange: DateRange
    ): FieldReport
}

@interface StakeholderManagement {
    @description Stakeholder management and access control

    addStakeholder(
        projectId: String,
        stakeholder: Stakeholder,
        role: StakeholderRole
    ): AddResult

    updateStakeholderRole(
        stakeholderId: String,
        newRole: StakeholderRole
    ): UpdateResult

    removeStakeholder(
        stakeholderId: String,
        reason: String
    ): RemoveResult

    listStakeholders(
        projectId: String,
        role: Optional<StakeholderRole>
    ): [Stakeholder]

    getStakeholderPermissions(
        stakeholderId: String
    ): [Permission]
}

@interface ConnectionViewManagement {
    @description Connection view version control and tracking

    createConnectionView(
        projectId: String,
        view: ConnectionView
    ): CreateResult

    updateConnectionView(
        viewId: String,
        updates: ViewUpdates
    ): UpdateResult

    archiveConnectionView(
        viewId: String,
        reason: String
    ): ArchiveResult

    getConnectionViewHistory(
        projectId: String
    ): [ConnectionView]
}

@interface ReportGeneration {
    @description Report generation and analytics

    generateProjectReport(
        projectId: String,
        reportType: ReportType,
        dateRange: DateRange
    ): Report

    generateProgressReport(
        projectId: String,
        dateRange: DateRange
    ): ProgressReport

    generateMaterialReport(
        projectId: String,
        materialType: Optional<MaterialType>
    ): MaterialReport

    generateFinancialReport(
        projectId: String,
        dateRange: DateRange
    ): FinancialReport
}
