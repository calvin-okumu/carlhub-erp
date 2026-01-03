// Service URL mapping for microservices via Traefik Gateway
// All requests now go through Traefik API Gateway on port 8000

export const TRAEFIK_GATEWAY = process.env.NEXT_PUBLIC_TRAEFIK_URL || 'http://localhost:8000';

export const IDENTITY_API_URL = process.env.NEXT_PUBLIC_IDENTITY_URL || `${TRAEFIK_GATEWAY}/api/v1/identity`;
export const AUDIT_API_URL = process.env.NEXT_PUBLIC_AUDIT_URL || `${TRAEFIK_GATEWAY}/api/v1/audit`;
export const NOTIFICATION_API_URL = process.env.NEXT_PUBLIC_NOTIFICATION_URL || `${TRAEFIK_GATEWAY}/api/v1/notification`;
export const ACCOUNTING_API_URL = process.env.NEXT_PUBLIC_ACCOUNTING_URL || `${TRAEFIK_GATEWAY}/api/v1/accounting`;
export const HR_API_URL = process.env.NEXT_PUBLIC_HR_URL || `${TRAEFIK_GATEWAY}/api/v1/hr`;
export const PROJECT_API_URL = process.env.NEXT_PUBLIC_PROJECT_URL || `${TRAEFIK_GATEWAY}/api/v1/project`;
export const SALES_API_URL = process.env.NEXT_PUBLIC_SALES_URL || `${TRAEFIK_GATEWAY}/api/v1/sales`;

// Fallback to identity service
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || IDENTITY_API_URL;
