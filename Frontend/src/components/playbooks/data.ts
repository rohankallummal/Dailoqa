import type { Playbook } from "./types";

const GREEN = "#16a34a";
const AMBER = "#d97706";
const BLUE = "#2563eb";

export const playbooksSeed: Playbook[] = [
  {
    id: "approval",
    name: "Approval",
    description:
      "A conversational workflow for AU Bank Gold Loan checker which is derived from the business rule agent.",
    framework: "LangGraph",
    status: "active",
    locked: true,
    tag: { label: "AUGOLDLOANA", color: GREEN },
    agents: 2,
    steps: 0,
    updatedAgo: "4 days ago",
    author: "Dev Admin",
    action: "chat",
  },
  {
    id: "valuator",
    name: "valuator",
    description:
      "You are a Manager Agent responsible for processing customer gold valuation cases.",
    framework: "LangGraph",
    status: "active",
    locked: true,
    tag: { label: "AUGOLDLOANV", color: AMBER },
    agents: 1,
    steps: 0,
    updatedAgo: "4 days ago",
    author: "Dev Admin",
    action: "chat",
  },
  {
    id: "securitization_and_disbursement",
    name: "securitization_and_disbursement",
    description:
      "A conversational workflow that completes the post-evaluation Gold Loan journey, including Gold Packet…",
    framework: "LangGraph",
    status: "active",
    locked: true,
    tag: { label: "AUGOLDLOANSD", color: GREEN },
    agents: 3,
    steps: 0,
    updatedAgo: "4 days ago",
    author: "Dev Admin",
    action: "chat",
  },
  {
    id: "pre_approval",
    name: "Pre_approval",
    description:
      "A conversational agent that helps loan officers structure and validate gold loan applications by guiding product…",
    framework: "LangGraph",
    status: "active",
    locked: true,
    tag: { label: "AUGOLDLOANPA", color: GREEN },
    agents: 5,
    steps: 0,
    updatedAgo: "4 days ago",
    author: "Dev Admin",
    action: "chat",
  },
  {
    id: "initiation_and_KYC",
    name: "initiation_and_KYC",
    description:
      "A conversational workflow for AU Bank Gold Loan onboarding that collects customer details, verifies…",
    framework: "LangGraph",
    status: "active",
    locked: true,
    tag: { label: "AUGOLDLOANIK", color: GREEN },
    agents: 4,
    steps: 0,
    updatedAgo: "4 days ago",
    author: "Dev Admin",
    action: "chat",
  },
  {
    id: "complaint_playbook",
    name: "complaint_playbook",
    description:
      "Performs evidence-based gap analysis on complaints case data, identifies missing/partial evidence against a…",
    framework: "LangGraph",
    status: "active",
    locked: true,
    tag: { label: "complaint_usecase", color: BLUE },
    agents: 1,
    steps: 0,
    updatedAgo: "5 days ago",
    author: "Satvik Bhardwaj",
    action: "run",
  },
];
