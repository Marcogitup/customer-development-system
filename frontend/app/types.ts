export type Project = {
  id: number;
  name: string;
  description: string | null;
  seed_keywords: string;
  status: string;
  created_at: string;
  updated_at: string;
};

export type Keyword = {
  id: number;
  text: string;
  category: string;
  confidence: number;
  source_type: string;
  source_url: string | null;
};

export type Source = {
  id: number;
  source_type: string;
  title: string;
  url: string;
  event_name: string | null;
  publication_year: number | null;
  access_status: string;
  notes: string | null;
};

export type Company = {
  id: number;
  name: string;
  website: string | null;
  country: string | null;
  address: string | null;
  phone: string | null;
  email: string | null;
  status: string;
  confidence: number;
  source_type: string | null;
  source_title: string | null;
  source_url: string | null;
  event_name: string | null;
  notes: string | null;
};

export type ResearchTask = {
  id: number;
  status: string;
  log: string | null;
  keywords_created: number;
  sources_created: number;
  companies_created: number;
  error: string | null;
  created_at: string;
  started_at: string | null;
  finished_at: string | null;
};

export type ProjectDetail = Project & {
  keywords: Keyword[];
  sources: Source[];
  companies: Company[];
  tasks: ResearchTask[];
};
