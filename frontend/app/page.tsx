"use client";

import { useEffect, useMemo, useState } from "react";
import { Download, Edit3, Play, Plus, RefreshCw, Save, Search } from "lucide-react";
import { createProject, exportUrl, getProject, listProjects, queueResearch, runResearchNow, updateCompany } from "./api";
import type { Company, Project, ProjectDetail } from "./types";

const statuses = ["new", "reviewing", "qualified", "contacted", "not_fit", "blocked_source"];

export default function Home() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [activeId, setActiveId] = useState<number | null>(null);
  const [detail, setDetail] = useState<ProjectDetail | null>(null);
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState("");
  const [sourceType, setSourceType] = useState("");
  const [busy, setBusy] = useState(false);
  const [editing, setEditing] = useState<Company | null>(null);
  const [form, setForm] = useState({
    name: "LED Display Prospecting",
    description: "Research target customers, exhibitor lists, magazines and buyer guides.",
    seed_keywords: "LED display, retail signage, commercial integrator"
  });

  async function refreshProjects(nextActiveId?: number) {
    const data = await listProjects();
    setProjects(data);
    const id = nextActiveId || activeId || data[0]?.id || null;
    setActiveId(id);
    if (id) {
      setDetail(await getProject(id));
    }
  }

  useEffect(() => {
    refreshProjects().catch(console.error);
  }, []);

  async function openProject(id: number) {
    setActiveId(id);
    setDetail(await getProject(id));
  }

  async function submitProject(event: React.FormEvent) {
    event.preventDefault();
    setBusy(true);
    try {
      const project = await createProject({
        name: form.name,
        description: form.description,
        seed_keywords: form.seed_keywords.split(",").map((item) => item.trim()).filter(Boolean)
      });
      await refreshProjects(project.id);
    } finally {
      setBusy(false);
    }
  }

  async function startResearch(mode: "queue" | "now") {
    if (!activeId) return;
    setBusy(true);
    try {
      if (mode === "queue") {
        await queueResearch(activeId);
      } else {
        await runResearchNow(activeId);
      }
      setDetail(await getProject(activeId));
    } finally {
      setBusy(false);
    }
  }

  async function saveCompany() {
    if (!editing || !activeId) return;
    setBusy(true);
    try {
      await updateCompany(editing.id, editing);
      setEditing(null);
      setDetail(await getProject(activeId));
    } finally {
      setBusy(false);
    }
  }

  const filteredCompanies = useMemo(() => {
    const companies = detail?.companies || [];
    return companies.filter((company) => {
      const haystack = [company.name, company.website, company.country, company.email, company.source_title].join(" ").toLowerCase();
      return (
        (!query || haystack.includes(query.toLowerCase())) &&
        (!status || company.status === status) &&
        (!sourceType || company.source_type === sourceType)
      );
    });
  }, [detail, query, status, sourceType]);

  const sourceTypes = Array.from(new Set((detail?.companies || []).map((company) => company.source_type).filter(Boolean))) as string[];

  return (
    <main className="shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="mark">CD</span>
          <div>
            <strong>Customer Dev</strong>
            <small>Research workspace</small>
          </div>
        </div>

        <form className="projectForm" onSubmit={submitProject}>
          <label>
            Project
            <input value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} />
          </label>
          <label>
            Seed keywords
            <textarea value={form.seed_keywords} onChange={(event) => setForm({ ...form, seed_keywords: event.target.value })} />
          </label>
          <button disabled={busy} type="submit">
            <Plus size={16} /> Create
          </button>
        </form>

        <nav className="projectList">
          {projects.map((project) => (
            <button key={project.id} className={project.id === activeId ? "active" : ""} onClick={() => openProject(project.id)}>
              <span>{project.name}</span>
              <small>{project.seed_keywords}</small>
            </button>
          ))}
        </nav>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <div>
            <h1>{detail?.name || "Customer Development System"}</h1>
            <p>{detail?.seed_keywords || "Create a project to begin keyword expansion and source discovery."}</p>
          </div>
          {detail && (
            <div className="actions">
              <button disabled={busy} onClick={() => startResearch("queue")} title="Run with background worker">
                <Play size={16} /> Queue
              </button>
              <button disabled={busy} onClick={() => startResearch("now")} title="Run immediately for local testing">
                <RefreshCw size={16} /> Run now
              </button>
              <a href={exportUrl(detail.id, "csv")}>
                <Download size={16} /> CSV
              </a>
              <a href={exportUrl(detail.id, "xlsx")}>
                <Download size={16} /> XLSX
              </a>
            </div>
          )}
        </header>

        {detail && (
          <>
            <section className="metrics">
              <div><strong>{detail.keywords.length}</strong><span>Keywords</span></div>
              <div><strong>{detail.sources.length}</strong><span>Sources</span></div>
              <div><strong>{detail.companies.length}</strong><span>Companies</span></div>
              <div><strong>{detail.tasks[0]?.status || "idle"}</strong><span>Latest task</span></div>
            </section>

            <section className="panel">
              <div className="panelHeader">
                <h2>Companies</h2>
                <div className="filters">
                  <div className="searchBox"><Search size={15} /><input placeholder="Search companies" value={query} onChange={(event) => setQuery(event.target.value)} /></div>
                  <select value={status} onChange={(event) => setStatus(event.target.value)}>
                    <option value="">All status</option>
                    {statuses.map((item) => <option key={item}>{item}</option>)}
                  </select>
                  <select value={sourceType} onChange={(event) => setSourceType(event.target.value)}>
                    <option value="">All sources</option>
                    {sourceTypes.map((item) => <option key={item}>{item}</option>)}
                  </select>
                </div>
              </div>
              <div className="tableWrap">
                <table>
                  <thead>
                    <tr>
                      <th>Company</th>
                      <th>Website</th>
                      <th>Country</th>
                      <th>Contact</th>
                      <th>Status</th>
                      <th>Source</th>
                      <th></th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredCompanies.map((company) => (
                      <tr key={company.id}>
                        <td>{company.name}</td>
                        <td>{company.website ? <a href={company.website} target="_blank">{company.website}</a> : ""}</td>
                        <td>{company.country}</td>
                        <td>{company.email || company.phone}</td>
                        <td><span className="status">{company.status}</span></td>
                        <td>{company.source_url ? <a href={company.source_url} target="_blank">{company.source_type}</a> : company.source_type}</td>
                        <td><button className="iconButton" onClick={() => setEditing(company)} title="Edit company"><Edit3 size={15} /></button></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>

            <section className="split">
              <div className="panel">
                <div className="panelHeader"><h2>Expanded Keywords</h2></div>
                <div className="chips">
                  {detail.keywords.slice(0, 80).map((keyword) => (
                    <span key={keyword.id} title={keyword.category}>{keyword.text}</span>
                  ))}
                </div>
              </div>
              <div className="panel">
                <div className="panelHeader"><h2>Sources</h2></div>
                <ul className="sourceList">
                  {detail.sources.slice(0, 30).map((source) => (
                    <li key={source.id}>
                      <a href={source.url} target="_blank">{source.title}</a>
                      <small>{source.source_type} · {source.access_status}</small>
                    </li>
                  ))}
                </ul>
              </div>
            </section>
          </>
        )}
      </section>

      {editing && (
        <div className="modalBackdrop">
          <div className="modal">
            <h2>Edit company</h2>
            <label>Name<input value={editing.name} onChange={(event) => setEditing({ ...editing, name: event.target.value })} /></label>
            <label>Website<input value={editing.website || ""} onChange={(event) => setEditing({ ...editing, website: event.target.value })} /></label>
            <label>Country<input value={editing.country || ""} onChange={(event) => setEditing({ ...editing, country: event.target.value })} /></label>
            <label>Email<input value={editing.email || ""} onChange={(event) => setEditing({ ...editing, email: event.target.value })} /></label>
            <label>Status<select value={editing.status} onChange={(event) => setEditing({ ...editing, status: event.target.value })}>{statuses.map((item) => <option key={item}>{item}</option>)}</select></label>
            <label>Notes<textarea value={editing.notes || ""} onChange={(event) => setEditing({ ...editing, notes: event.target.value })} /></label>
            <div className="modalActions">
              <button onClick={() => setEditing(null)}>Cancel</button>
              <button disabled={busy} onClick={saveCompany}><Save size={16} /> Save</button>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
