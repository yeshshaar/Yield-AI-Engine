export type BirthDetails = {
  fullName: string;
  dob: string;
  time: string;
  place: string;
};

export type AstrologySection = {
  title: string;
  body: string;
};

export type AstrologyReport = {
  basicDetails: AstrologySection;
  personality: AstrologySection;
  career: AstrologySection;
  love: AstrologySection;
  wealth: AstrologySection;
  dasha: AstrologySection;
  futurePredictions: AstrologySection;
  remedies: AstrologySection;
};

export type StoredReport = {
  id: string;
  user: BirthDetails;
  report: AstrologyReport;
  personalityPreview: string;
  unlocked: boolean;
  paymentId?: string;
  createdAt: string;
};

export type PreviewResponse = {
  reportId: string;
  basicDetails: AstrologySection;
  personalityPreview: string;
  lockedSections: string[];
};
