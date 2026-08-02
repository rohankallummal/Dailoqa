export type ClientEnvironment = {
  device: string;
  browser: string;
  operating_system: string;
};

const UNKNOWN = "Unknown";

type UserAgentData = {
  mobile?: boolean;
  platform?: string;
};

const BROWSER_PATTERNS: [RegExp, string][] = [
  [/Edg\/([\d.]+)/, "Edge"],
  [/OPR\/([\d.]+)/, "Opera"],
  [/Firefox\/([\d.]+)/, "Firefox"],
  [/Chrome\/([\d.]+)/, "Chrome"],
  [/Version\/([\d.]+).*Safari/, "Safari"],
];

const OS_PATTERNS: [RegExp, string][] = [
  [/Windows NT 10\.0/, "Windows 10/11"],
  [/Windows NT ([\d.]+)/, "Windows"],
  [/Mac OS X ([\d_.]+)/, "macOS"],
  [/Android ([\d.]+)/, "Android"],
  [/(?:iPhone|iPad) OS ([\d_]+)/, "iOS"],
  [/CrOS/, "ChromeOS"],
  [/Linux/, "Linux"],
];

function match(userAgent: string, patterns: [RegExp, string][]): string {
  for (const [pattern, label] of patterns) {
    const found = userAgent.match(pattern);
    if (found) return found[1] ? `${label} ${found[1].replace(/_/g, ".")}` : label;
  }
  return UNKNOWN;
}

function detectDevice(userAgent: string, data?: UserAgentData): string {
  if (data?.mobile === true) return "Mobile";
  if (/iPad|Tablet/i.test(userAgent)) return "Tablet";
  if (/Mobi|Android|iPhone/i.test(userAgent)) return "Mobile";
  return "Desktop";
}

export function readClientEnvironment(): ClientEnvironment {
  if (typeof navigator === "undefined") {
    return { device: UNKNOWN, browser: UNKNOWN, operating_system: UNKNOWN };
  }
  const data = (navigator as Navigator & { userAgentData?: UserAgentData }).userAgentData;
  const userAgent = navigator.userAgent ?? "";
  const parsedOs = match(userAgent, OS_PATTERNS);
  return {
    device: detectDevice(userAgent, data),
    browser: match(userAgent, BROWSER_PATTERNS),
    operating_system: parsedOs === UNKNOWN && data?.platform ? data.platform : parsedOs,
  };
}
