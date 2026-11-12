import { useEffect, useMemo, useState, type ReactNode } from "react";
import {
  Activity, AlertCircle, ArrowUpRight, BookOpen, CheckCircle2, ChevronDown,
  Database, FileSearch, GitBranch, Network, Play, RotateCcw, ShieldCheck,
  Workflow, XCircle, Link2, Target
} from "lucide-react";

type AnyRecord = Record<string, any>;
const API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const stages = [
  { key: "world", title: "Persistent world state", description: "Investigation context and stored knowledge" },
  { key: "retrieval", title: "Adaptive hybrid retrieval", description: "Semantic and graph-based evidence collection" },
  { key: "grading", title: "Retrieval grading", description: "Relevance assessment of retrieved context" },
  { key: "generation", title: "Answer generation", description: "Evidence-grounded findings and claims" },
  { key: "verification", title: "Multi-agent verification", description: "Evidence, graph and consistency checks" },
  { key: "beliefs", title: "Belief and hypothesis reasoning", description: "Belief updates and hypothesis generation" },
  { key: "simulation", title: "Simulation", description: "Scenario execution and hypothesis evaluation" },
  { key: "decision", title: "Decision engine", description: "Risk assessment and recommended disposition" },
];

function obj(value: any): AnyRecord {
  return value && typeof value === "object" && !Array.isArray(value) ? value : {};
}
function firstDefined(...values: any[]) {
  return values.find(v => v !== undefined && v !== null && v !== "");
}
function asArray(...values: any[]): any[] {
  for (const value of values) if (Array.isArray(value)) return value;
  return [];
}
function human(value: any): string {
  if (value === undefined || value === null || value === "") return "Not reported";
  if (typeof value === "boolean") return value ? "Yes" : "No";
  if (typeof value === "number") return Number.isInteger(value) ? value.toLocaleString() : value.toFixed(3);
  return String(value).replaceAll("_", " ").replace(/\b\w/g, (c: string) => c.toUpperCase());
}
function sentence(value: any): string {
  if (value === undefined || value === null || value === "") return "No explanation was returned for this item.";
  if (typeof value === "string") return value;
  if (typeof value === "number" || typeof value === "boolean") return human(value);
  return Object.entries(obj(value)).map(([k, v]) => `${human(k)}: ${human(v)}`).join(" · ") || "Details were not reported.";
}
function titleCase(value: any): string { return human(value); }
function StatusPill({ value }: { value: any }) {
  const text = String(value ?? "Not reported");
  const lower = text.toLowerCase();
  const tone = /error|reject|unsupported|fail|insufficient|offline/.test(lower) ? "rose"
    : /review|weak|partial|proposed|unknown|needs/.test(lower) ? "amber"
    : /success|support|relevant|accept|complete|consistent|online|strong/.test(lower) ? "green" : "neutral";
  return <span className={`pill ${tone}`}>{titleCase(text)}</span>;
}
function Field({ label, value }: { label: string; value: any }) {
  const display = Array.isArray(value) ? value.map(human).join(", ") : human(value);
  return <div className="field"><span>{label}</span><strong>{display}</strong></div>;
}
function RevisionCards({ items, title }: { items: any[]; title: string }) {
  if (!items.length) return <EmptyNote>No {title.toLowerCase()} were recorded.</EmptyNote>;
  return <div className="revision-list">{items.map((raw, i) => {
    const r = obj(raw);
    return <article className="revision-card" key={String(r.belief_id || i)}>
      <div className="record-top"><strong>{title} {i + 1}</strong><StatusPill value={r.revision_type || r.new_status}/></div>
      <p className="record-description">{human(r.belief_id)}</p>
      <div className="detail-grid">
        <Field label="Previous status" value={r.previous_status}/>
        <Field label="New status" value={r.new_status}/>
        <Field label="Revision type" value={r.revision_type}/>
        <Field label="Evidence references" value={r.evidence_ids}/>
      </div>
      <Explanation title="Why this changed (or stayed the same)" children={r.reason}/>
      {r.timestamp && <small className="timestamp">Recorded {new Date(r.timestamp).toLocaleString()}</small>}
    </article>;
  })}</div>;
}
function ClaimCards({ items }: { items: any[] }) {
  if (!items.length) return <EmptyNote>No individual claim assessments were returned.</EmptyNote>;
  return <div className="claim-list">{items.map((raw, i) => {
    const c = obj(raw);
    return <article className="claim-row" key={i}>
      <StatusPill value={c.status}/>
      <p>{human(c.claim || c.statement || `Claim ${i + 1}`)}</p>
      {c.reason && <small>{human(c.reason)}</small>}
    </article>;
  })}</div>;
}
function Section({ title, subtitle, icon, children, defaultOpen = true }: {
  title: string; subtitle?: string; icon: ReactNode; children: ReactNode; defaultOpen?: boolean
}) {
  return <details className="section" open={defaultOpen}>
    <summary className="section-head">
      <span className="section-icon">{icon}</span>
      <span className="section-title"><strong>{title}</strong>{subtitle && <small>{subtitle}</small>}</span>
      <ChevronDown className="section-chevron" size={19}/>
    </summary>
    <div className="section-body">{children}</div>
  </details>;
}
function EmptyNote({ children }: { children: ReactNode }) {
  return <p className="empty-note">{children}</p>;
}
function Explanation({ title, children }: { title: string; children: any }) {
  if (children === undefined || children === null || children === "") return null;
  return <div className="explanation"><strong>{title}</strong><p>{sentence(children)}</p></div>;
}
function RecordCards({ items, kind }: { items: any[]; kind: "evidence" | "belief" | "hypothesis" }) {
  if (!items.length) return <EmptyNote>No individual {kind} records were included in this response.</EmptyNote>;
  return <div className="record-list">{items.map((raw, i) => {
    const item = obj(raw);
    const title = firstDefined(item.claim, item.statement, item.name, item.id, item.evidence_id, item.belief_id, item.hypothesis_id, `${kind} ${i + 1}`);
    const status = firstDefined(item.verification_status, item.status, item.support_status, item.result);
    const description = firstDefined(item.description, item.text, item.content, item.summary, item.reason, item.claim);
    return <article className="record-card" key={String(firstDefined(item.id, item.evidence_id, item.belief_id, item.hypothesis_id, i))}>
      <div className="record-top"><strong>{String(title)}</strong>{status && <StatusPill value={status}/>}</div>
      {description && String(description) !== String(title) && <p className="record-description">{sentence(description)}</p>}
      <div className="record-meta">
        {firstDefined(item.source, item.reference, item.url) && <span><Link2 size={14}/>{human(firstDefined(item.source, item.reference, item.url))}</span>}
        {firstDefined(item.confidence, item.similarity, item.score) !== undefined && <span><Target size={14}/> {human(firstDefined(item.confidence, item.similarity, item.score))}</span>}
        {firstDefined(item.stix_type, item.entity_type, item.type) && <span>{human(firstDefined(item.stix_type, item.entity_type, item.type))}</span>}
      </div>
    </article>;
  })}</div>;
}
function AgentCard({ label, data }: { label: string; data: any }) {
  const item = obj(data);
  const metrics = Object.entries(item).filter(([key, value]) =>
    !["agent", "status", "reason", "summary", "message", "explanation", "status_detail", "claims", "results", "details", "findings", "checks", "entities"].includes(key)
    && (typeof value === "string" || typeof value === "number" || typeof value === "boolean")
  );
  const claims = asArray(item.claims);
  const findings = asArray(item.findings);
  const checks = obj(item.checks);
  const agentResults = obj(item.agent_results);
  const verification = obj(item.verification);
  const conflicts = asArray(item.conflicts);
  return <article className="agent-card">
    <div className="agent-top"><strong>{label}</strong><StatusPill value={item.status}/></div>
    {item.total_claims !== undefined && <div className="agent-metrics">
      <div><span>Total claims</span><strong>{human(item.total_claims)}</strong></div>
      <div><span>Supported</span><strong>{human(item.supported)}</strong></div>
      <div><span>Partially supported</span><strong>{human(item.partially_supported)}</strong></div>
      <div><span>Unsupported</span><strong>{human(item.unsupported)}</strong></div>
    </div>}
    {item.entities_checked !== undefined && <div className="agent-metrics">
      <div><span>Entities checked</span><strong>{human(item.entities_checked)}</strong></div>
      <div><span>Entities found</span><strong>{human(item.entities_found)}</strong></div>
    </div>}
    {metrics.length > 0 && item.total_claims === undefined && item.entities_checked === undefined &&
      <div className="agent-metrics">{metrics.slice(0, 4).map(([key, value]) =>
        <div key={key}><span>{human(key)}</span><strong>{human(value)}</strong></div>
      )}</div>}
    {claims.length > 0 && <div className="agent-sublist"><strong>Claim checks</strong>{claims.map((c: any, i: number) =>
      <div className="agent-subrow" key={i}><span>{human(c.claim)}</span><StatusPill value={c.status}/></div>
    )}</div>}
    {findings.length > 0 && <div className="agent-sublist"><strong>Findings</strong>{findings.map((f: any, i: number) => <p key={i}>{human(f)}</p>)}</div>}
    {Object.keys(checks).length > 0 && <div className="check-list"><strong className="subsection-label">Consistency checks</strong>{Object.entries(checks).map(([k,v]) =>
      <div key={k}><span>{human(k)}</span><StatusPill value={v}/></div>
    )}</div>}
    {asArray(item.entities).length > 0 && <div className="agent-sublist"><strong>Graph entities</strong>{asArray(item.entities).map((e: any, i: number) =>
      <div className="agent-subrow" key={i}><span>{human(e.cve || e.id || e.name)}</span><StatusPill value={e.exists ? "Present in graph" : "Not found"}/></div>
    )}</div>}
    {Object.keys(agentResults).length > 0 && <div className="agent-sublist">
      <strong>Agent assessments contributing to consensus</strong>
      <div className="consensus-results">{Object.entries(agentResults).map(([name, raw]) => {
        const assessment = obj(raw);
        return <div className="consensus-result" key={name}>
          <span>{name}</span><StatusPill value={assessment.status}/>
          {assessment.total_claims !== undefined && <small>{human(assessment.supported)} of {human(assessment.total_claims)} claims supported · {human(assessment.partially_supported)} partially supported · {human(assessment.unsupported)} unsupported</small>}
          {assessment.entities_checked !== undefined && <small>{human(assessment.entities_found)} of {human(assessment.entities_checked)} graph entities found</small>}
        </div>;
      })}</div>
    </div>}
    {Object.keys(verification).length > 0 && <div className="agent-sublist">
      <strong>Consensus verification breakdown</strong>
      <div className="check-list">{Object.entries(verification).map(([k,v]) =>
        <div key={k}><span>{human(k)}</span><StatusPill value={v}/></div>
      )}</div>
    </div>}
    {conflicts.length > 0 && <div className="agent-sublist">
      <strong>Conflicts requiring attention</strong>
      {conflicts.map((conflict: any, i: number) => <p key={i}>{sentence(conflict)}</p>)}
    </div>}
    {Object.keys(agentResults).length === 0 && Object.keys(verification).length === 0 && conflicts.length === 0 && item.status && label.toLowerCase().includes("consensus") &&
      <EmptyNote>The consensus status was returned, but no contributing agent breakdown was included.</EmptyNote>}
  </article>;
}
function formatDecision(value: any) {
  const d = obj(value);
  return {
    risk: firstDefined(d.risk_level, d.risk, d.severity),
    decision: firstDefined(d.decision, d.status, d.action),
    verification: firstDefined(d.verification_status, d.verification),
    action: firstDefined(d.recommended_action, d.action_required, d.recommendation),
    rationale: firstDefined(d.rationale, d.reason, d.explanation, d.summary),
  };
}

export default function App() {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState<AnyRecord | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [apiOnline, setApiOnline] = useState<boolean | null>(null);

  const retrieval = obj(result?.retrieval);
  const adaptive = obj(result?.adaptive_retrieval);
  const grading = obj(retrieval.grading);
  const agents = obj(result?.multi_agent_verification);
  const decision = obj(result?.decision);
  const simulation = obj(result?.simulation);
  const simulationFinal = obj(simulation.final_state);
  const simulationVariables = obj(simulationFinal.variables);
  const graph = obj(retrieval.graph_retrieval);
  const graphContext = obj(graph.context);
  const decisionView = formatDecision(decision);

  const evidenceItems = asArray(
    graphContext.evidence, retrieval.evidence, retrieval.semantic_evidence, retrieval.results,
    retrieval.retrieved_evidence, retrieval.evidence_records,
    result?.evidence, result?.evidence_records
  );
  const beliefs = asArray(result?.beliefs);
  const hypotheses = asArray(result?.hypotheses);
  const evaluations = asArray(result?.hypothesis_evaluations);
  const attempts = asArray(adaptive.attempts, adaptive.retrieval_attempts);
  const graphEntities = asArray(graph.entities, graph.nodes, graph.results,
    agents.graph_agent?.entities);

  const graphRelationships = asArray(graph.relationships, graph.edges);

  const stats = useMemo(() => [
    { label: "Retrieved candidates", value: firstDefined(retrieval.semantic_evidence_count, retrieval.semantic_candidate_count, evidenceItems.length, "—") },
    { label: "Accepted semantic matches", value: firstDefined(retrieval.relevant_semantic_evidence_count, retrieval.semantic_match_count, "—") },
    { label: "Belief records", value: beliefs.length },
    { label: "Hypotheses", value: hypotheses.length },
  ], [result]);

  async function checkHealth() {
    try {
      const response = await fetch(`${API_BASE}/api/health`);
      setApiOnline(response.ok);
    } catch { setApiOnline(false); }
  }
  useEffect(() => { void checkHealth(); }, []);

  async function runInvestigation() {
    if (query.trim().length < 8) { setError("Enter an investigation query of at least 8 characters."); return; }
    setLoading(true); setError(""); setResult(null);
    try {
      const response = await fetch(`${API_BASE}/api/investigate`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: query.trim() }),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail || `Request failed (${response.status})`);
      if (payload.status === "error") throw new Error(payload.message || "The CIF pipeline returned an investigation error.");
      setResult(payload); setApiOnline(true);
    } catch (e: any) {
      setError(e.message || "Could not connect to CIF API."); setApiOnline(false);
    } finally { setLoading(false); }
  }

  const stageStatuses = [
    result?.status === "success" ? "Completed" : result ? human(result.status) : "Awaiting run",
    firstDefined(adaptive.final_decision?.action, adaptive.final_decision?.decision, result ? "Retrieved" : "Awaiting run"),
    firstDefined(grading.status, result ? "Not reported" : "Awaiting run"),
    result?.answer ? "Generated" : result ? "Not reported" : "Awaiting run",
    firstDefined(agents.consensus?.status, result ? "Not reported" : "Awaiting run"),
    `${beliefs.length} beliefs · ${hypotheses.length} hypotheses`,
    firstDefined(simulation.status, simulation.simulation_completed ? "Completed" : result ? "Not reported" : "Awaiting run"),
    firstDefined(decision.decision, decision.status, result ? "Not reported" : "Awaiting run"),
  ];

  return <main className="app-shell">
    <header className="topbar">
      <div className="brand"><div className="brand-mark"><ShieldCheck size={25}/></div>
        <div><div className="brand-name">CIF</div><div className="brand-sub">COGNITIVE INTELLIGENCE FRAMEWORK</div></div>
      </div>
      <div className="top-meta">
        <span className={`connection ${apiOnline === false ? "offline" : apiOnline ? "online" : ""}`}>
          <i/> {apiOnline === false ? "API OFFLINE" : apiOnline ? "API CONNECTED" : "CHECKING API"}
        </span>
        <button className="icon-button" title="Check API connection" onClick={checkHealth}><RotateCcw size={18}/></button>
      </div>
    </header>

    <div className="page">
      <div className="page-heading">
        <div><div className="eyebrow">CYBER THREAT ANALYSIS</div><h1>Investigation workspace</h1>
          <p>Run an evidence-grounded investigation and inspect how CIF reaches its assessment.</p></div>
        <div className="workspace-tag"><Activity size={17}/> SINGLE INVESTIGATION CONSOLE</div>
      </div>

      <section className="query-card">
        <div className="card-label"><FileSearch size={19}/> Investigation query</div>
        <textarea value={query} onChange={e => setQuery(e.target.value)}
          placeholder="Example: Investigate CVE-2026-41473 and identify its vulnerability details, affected component, and security implications."
          rows={3}/>
        <div className="query-footer">
          <span>Be specific about the threat, entity, or indicators you want CIF to investigate.</span>
          <button className="primary-button" onClick={runInvestigation} disabled={loading}>
            {loading ? <><span className="spinner"/> Running CIF…</> : <><Play size={18} fill="currentColor"/> Run investigation</>}
          </button>
        </div>
      </section>

      {error && <div className="error-banner"><AlertCircle size={20}/><span>{error}</span><button onClick={() => setError("")}><XCircle size={18}/></button></div>}
      {!result && !loading && <section className="empty-state">
        <div className="empty-icon"><Workflow size={31}/></div><h2>Ready for investigation</h2>
        <p>Submit a query to view the threat assessment, evidence retrieval, agent verification, belief updates, simulation and final decision.</p>
        <button className="text-button" onClick={() => setQuery("Investigate CVE-2026-41473 and identify its vulnerability details, affected component, and security implications.")}>Use sample investigation <ArrowUpRight size={17}/></button>
      </section>}
      {loading && <section className="loading-card"><div className="spinner large"/><strong>Executing CIF reasoning pipeline</strong><p>Retrieval, verification and decision stages may take a little time. Keep this page open.</p></section>}

      {result && <>
        <div className="result-title"><div><div className="eyebrow">INVESTIGATION OUTPUT</div><h2>Threat assessment report</h2></div><StatusPill value={result.status}/></div>
        <section className="summary-grid">
          <div className="summary-card"><span>Risk level</span><strong className="summary-value">{human(decisionView.risk)}</strong><small>Decision engine assessment</small></div>
          <div className="summary-card"><span>Final decision</span><strong className="summary-value">{human(decisionView.decision)}</strong><small>Recommended disposition</small></div>
          <div className="summary-card"><span>Retrieved candidates</span><strong className="summary-value">{human(stats[0].value)}</strong><small>Semantic retrieval output</small></div>
          <div className="summary-card"><span>Agent consensus</span><strong className="summary-value compact">{human(agents.consensus?.status)}</strong><small>Combined verification assessment</small></div>
        </section>

        <Section title="Executive findings" subtitle="Key findings and the basis for CIF's assessment" icon={<BookOpen size={20}/>}>
          <div className="answer-text">{result.answer || result.message || "The pipeline did not return a generated assessment."}</div>
          <div className="decision-box">
            <div className="decision-heading"><CheckCircle2 size={19}/> Decision rationale</div>
            <p>{sentence(decisionView.rationale)}</p>
            <div className="decision-fields">
              <Field label="Risk level" value={decisionView.risk}/>
              <Field label="Final decision" value={decisionView.decision}/>
              <Field label="Verification status" value={decisionView.verification}/>
              <Field label="Verification status" value={decision.verification_status}/>
              <Field label="Hypothesis status" value={decision.hypothesis_status}/>
              <Field label="Simulation status" value={decision.simulation_status}/>
            </div>
            {asArray(decision.recommended_actions).length > 0 && <div className="decision-list"><strong>Recommended next steps</strong><ul>{decision.recommended_actions.map((a: any, i: number) => <li key={i}>{human(a)}</li>)}</ul></div>}
            {asArray(decision.supporting_evidence).length > 0 && <div className="decision-list"><strong>Decision support</strong><ul>{decision.supporting_evidence.map((a: any, i: number) => <li key={i}>{human(a)}</li>)}</ul></div>}
          </div>
        </Section>

        <Section title="Reasoning pipeline" subtitle="Execution status of each CIF layer" icon={<Workflow size={20}/>}>
          <div className="pipeline-list">{stages.map((stage, i) => <div className="pipeline-row" key={stage.key}>
            <div className="pipeline-number">{String(i + 1).padStart(2, "0")}</div>
            <div className="pipeline-copy"><strong>{stage.title}</strong><small>{stage.description}</small></div>
            <StatusPill value={stageStatuses[i]}/>
          </div>)}</div>
          <p className="note">A stage marked “Not reported” means the current API response did not include a separate result for that layer.</p>
        </Section>

        <Section title="Evidence retrieval" subtitle="Separate retrieved candidates from accepted semantic matches" icon={<Database size={20}/>}>
          <div className="detail-grid">
            <Field label="Retrieval method" value={retrieval.retrieval_mode}/>
            <Field label="Retrieved candidates" value={firstDefined(grading.semantic_candidate_count, retrieval.semantic_evidence_count, evidenceItems.length)}/>
            <Field label="Accepted semantic matches" value={firstDefined(retrieval.semantic_match_count, retrieval.relevant_semantic_evidence_count)}/>
            <Field label="Average similarity" value={firstDefined(grading.average_similarity, retrieval.average_similarity)}/>
            <Field label="Retrieval grading" value={grading.status}/>
            <Field label="Grading score" value={grading.score}/>
            <Field label="Adaptive attempts" value={attempts.length || firstDefined(adaptive.attempt_count, "Not reported")}/>
            <Field label="Final retrieval action" value={firstDefined(adaptive.final_decision?.action, adaptive.final_decision?.decision)}/>
          </div>
          <Explanation title="Retrieval assessment" children={firstDefined(grading.reason, grading.explanation, grading.summary)}/>
          <Explanation title="Retrieved context" children={graphContext.description || retrieval.context}/>
          <h3>Retrieved evidence records</h3>
          <RecordCards items={evidenceItems} kind="evidence"/>
          {graphEntities.length > 0 && <>
            <h3>Knowledge graph entities</h3>
            <div className="chip-list">{graphEntities.map((e, i) => <span className="entity-chip" key={i}>{human(firstDefined(obj(e).name, obj(e).id, obj(e).type, e))}</span>)}</div>
          </>}
          {graphRelationships.length > 0 && <>
            <h3>Knowledge graph relationships</h3>
            <div className="relationship-list">{graphRelationships.map((r, i) => <div key={i}><strong>{human(firstDefined(obj(r).type, obj(r).relationship, "Relationship"))}</strong><span>{human(firstDefined(obj(r).source, obj(r).from, "Source"))} → {human(firstDefined(obj(r).target, obj(r).to, "Target"))}</span></div>)}</div>
          </>}
          {attempts.length > 0 && <div className="attempt-list"><h3>Adaptive retrieval attempts</h3>{attempts.map((a, i) => <div className="attempt-row" key={i}><span>Attempt {i + 1}</span><StatusPill value={firstDefined(obj(a).status, obj(a).action, "Completed")}/><p>{sentence(firstDefined(obj(a).reason, obj(a).query, obj(a).decision))}</p></div>)}</div>}
        </Section>

        <Section title="Multi-agent verification" subtitle="Independent agent findings and their combined consensus" icon={<ShieldCheck size={20}/>}>
          <div className="consensus-banner">
            <div><span>Overall consensus</span><strong>{human(agents.consensus?.status)}</strong></div>
            <StatusPill value={agents.consensus?.status}/>
            {agents.consensus?.conflicts?.length === 0 && <small>No agent conflicts were reported.</small>}
          </div>
          <div className="agent-grid">
            <AgentCard label="Evidence agent" data={agents.evidence_agent}/>
            <AgentCard label="Graph agent" data={agents.graph_agent}/>
            <AgentCard label="Consistency agent" data={agents.consistency_agent}/>
            <AgentCard label="Consensus agent" data={agents.consensus}/>
          </div>
          <h3>Claim-level assessment</h3>
          <ClaimCards items={asArray(result.claim_verification)}/>
        </Section>

        <Section title="Belief state and hypotheses" subtitle="Investigation beliefs and proposed explanations" icon={<GitBranch size={20}/>} defaultOpen={false}>
          <div className="detail-grid">
            <Field label="Belief records" value={beliefs.length}/>
            <Field label="Hypotheses generated" value={hypotheses.length}/>
            <Field label="Belief revisions" value={asArray(result.belief_revisions).length}/>
            <Field label="Simulation-driven revisions" value={asArray(result.simulation_belief_revisions).length}/>
          </div>
          <h3>Belief records</h3><RecordCards items={beliefs} kind="belief"/>
          <h3>Hypotheses</h3><RecordCards items={hypotheses} kind="hypothesis"/>
          <h3>Belief revision history</h3>
          <RevisionCards items={asArray(result.belief_revisions)} title="Belief revision"/>
          <h3>Simulation-driven belief revisions</h3>
          <RevisionCards items={asArray(result.simulation_belief_revisions)} title="Simulation revision"/>
        </Section>

        <Section title="Simulation and hypothesis evaluation" subtitle="Scenario execution and resulting assessment" icon={<Network size={20}/>} defaultOpen={false}>
          <div className="detail-grid">
            <Field label="Simulation completed" value={firstDefined(simulationVariables.simulation_completed, simulation.simulation_completed, simulation.outcomes?.[0]?.status === "completed")}/>
            <Field label="State transitions" value={firstDefined(simulationVariables.state_transition_count, simulation.outcomes?.[0]?.events_generated)}/>
            <Field label="Scenario" value={simulation.scenario_id}/>
            <Field label="Hypothesis evaluations" value={evaluations.length}/>
            <Field label="Initial belief count" value={simulation.outcomes?.[0]?.initial_belief_count}/>
            <Field label="Final belief count" value={simulation.outcomes?.[0]?.final_belief_count}/>
          </div>
          <Explanation title="Simulation summary" children={firstDefined(simulation.summary, simulation.reason, simulation.status_detail)}/>
          {evaluations.length > 0 ? <div className="record-list">{evaluations.map((e, i) => <article className="record-card" key={i}>
            <div className="record-top"><strong>{human(firstDefined(obj(e).hypothesis, obj(e).hypothesis_id, `Evaluation ${i + 1}`))}</strong><StatusPill value={firstDefined(obj(e).evaluation_status, obj(e).outcome, obj(e).status, obj(e).result)}/></div>
            <div className="record-meta"><span>Outcomes: {human(obj(e).outcome_count)}</span><span>Simulation completed: {human(obj(e).simulation_completed)}</span></div>
            <p className="record-description">{sentence(firstDefined(obj(e).reason, obj(e).explanation, obj(e).details))}</p>
          </article>)}</div> : <EmptyNote>No separate hypothesis evaluation records were returned.</EmptyNote>}
        </Section>
      </>}
      <footer><span>CIF · Evidence-grounded threat assessment</span><span>Research prototype · VIT-AP University</span></footer>
    </div>
  </main>;
}
