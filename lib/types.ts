export type Template = {
  id: number;
  name: string;
  subject: string;
  body: string;
  createdAt: string;
};

export type CampaignHistory = {
  id: number;
  sentAt: string;
  subject: string;
  recipientsCount: number;
  successCount: number;
  failureCount: number;
  copyHtml: string;
  failedEmails: string;
};

export type SendStatus = {
  id: string;
  total: number;
  sent: number;
  failed: number;
  current: string;
  finished: boolean;
  stopped: boolean;
  failures: Array<{ email: string; error: string }>;
};
