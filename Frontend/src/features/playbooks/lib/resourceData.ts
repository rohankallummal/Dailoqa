export type ResourceOption = {
  id: string;
  name: string;
  description?: string;
};

export const availableAgents: ResourceOption[] = [
  { id: "kyc-agent", name: "KYC Agent", description: "Aadhaar + PAN validation" },
  { id: "compliance-agent", name: "Compliance Agent", description: "CIBIL, AML, delinquency checks" },
  { id: "valuation-agent", name: "Valuation Agent", description: "Gold valuation & loan summary" },
  { id: "manager-agent", name: "Manager Agent", description: "Orchestrates gold valuation cases" },
  { id: "business-rule-agent", name: "Business Rule Agent", description: "Loan checker business rules" },
];

export const availableTools: ResourceOption[] = [
  { id: "send-otp", name: "Send OTP" },
  { id: "fetch-cif", name: "Fetch CIF" },
  { id: "cibil-lookup", name: "CIBIL Lookup" },
  { id: "aml-screen", name: "AML Screen" },
  { id: "gold-rate-fetch", name: "Gold Rate Fetch" },
];

export const availableSkills: ResourceOption[] = [
  { id: "summarization", name: "Summarization" },
  { id: "sql-generation", name: "SQL Generation" },
  { id: "document-parsing", name: "Document Parsing" },
  { id: "risk-scoring", name: "Risk Scoring" },
];

export const availableKnowledgeBases: ResourceOption[] = [
  { id: "gold-loan-policy", name: "Gold Loan Policy" },
  { id: "kyc-guidelines", name: "KYC Guidelines" },
  { id: "compliance-handbook", name: "Compliance Handbook" },
];
