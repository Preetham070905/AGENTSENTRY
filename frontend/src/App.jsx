



import { useEffect, useState } from 'react';
import {
  ShieldCheck, LayoutDashboard, Activity, Cpu, FileSearch,
  Bell, Settings, Search, RefreshCw, AlertTriangle,
  CheckCircle2, CircleDot, Server, Clock, ChevronRight,
  ShieldAlert, Zap, HardDrive, Terminal, Eye
} from 'lucide-react';
import {
  ResponsiveContainer, AreaChart, Area, XAxis, YAxis,
  Tooltip, CartesianGrid, BarChart, Bar
} from 'recharts';
import './App.css';

const API = 'http://127.0.0.1:8000';

function StatCard({ title, value, detail, icon: Icon, color }) {
  return (
    <div className="stat-card">
      <div className={`stat-icon ${color}`}><Icon size={21} /></div>
      <div className="stat-title">{title}</div>
      <div className="stat-value">{value}</div>
      <div className="stat-detail">{detail}</div>
    </div>
  );
}

function App() {
  const [dashboard, setDashboard] = useState(null);
  const [processes, setProcesses] = useState([]);
  const [agents, setAgents] = useState([]);
  const [enforcement, setEnforcement] = useState({ events: [], confirmed_denials: 0 });
  const [xaiExplanations, setXaiExplanations] = useState([]);
  const [activeTab, setActiveTab] = useState('Overview');
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState(new Date());

  async function loadData() {
    try {
      const [dashResponse, processResponse, agentsResponse, enforcementResponse, xaiResponse] = await Promise.all([
        fetch(`${API}/api/dashboard`),
        fetch(`${API}/api/processes`),
        fetch(`${API}/api/agents`),
        fetch(`${API}/api/enforcement-events`),
        fetch(`${API}/api/xai-explanations`)
      ]);

      if (![dashResponse, processResponse, agentsResponse, enforcementResponse, xaiResponse].every(response => response.ok)) {
        throw new Error('API request failed');
      }

      const [dash, proc, agentData, enforcementData, xaiData] = await Promise.all([
        dashResponse.json(),
        processResponse.json(),
        agentsResponse.json(),
        enforcementResponse.json(),
        xaiResponse.json()
      ]);

      setDashboard(dash);
      setProcesses(proc.processes || []);
      setAgents(agentData.agents || []);
      setEnforcement({
        events: enforcementData.events || [],
        confirmed_denials: enforcementData.confirmed_denials || 0
      });
      setXaiExplanations(xaiData.explanations || []);
      setLastUpdated(new Date());
    } catch (error) {
      console.error('Could not load AGENTSENTRY data:', error);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData();
    const timer = setInterval(loadData, 5000);
    return () => clearInterval(timer);
  }, []);

  const navItems = [
    { name: 'Overview', icon: LayoutDashboard },
    { name: 'Processes', icon: Cpu },
    { name: 'File Events', icon: FileSearch },
    { name: 'Security Alerts', icon: ShieldAlert },
  ];

  const eventChart = [
    { time: '00:00', events: 2 },
    { time: '04:00', events: 5 },
    { time: '08:00', events: 3 },
    { time: '12:00', events: 8 },
    { time: '16:00', events: 4 },
    { time: '20:00', events: dashboard?.file_event_count || 0 },
  ];

  const visibleProcesses = [...processes]
    .sort((a, b) => (b.memory_rss_bytes || 0) - (a.memory_rss_bytes || 0))
    .slice(0, 8);

  const events = dashboard?.recent_events || [];
  const timelineEvents = events.slice(0, 5).reverse().map((event, index) => ({
    time: event.timestamp
      ? new Date(event.timestamp).toLocaleTimeString([], {
          hour: '2-digit',
          minute: '2-digit',
          hour12: false
        })
      : '--:--',
    title: `${event.event || 'File event'} observed`,
    detail: event.path
      ? event.path.split('/').pop()
      : 'Local monitoring event',
    event
  }));
  const alerts = dashboard?.recent_alerts || [];

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark"><ShieldCheck size={25} /></div>
          <div>
            <div className="brand-name">AGENT<span>SENTRY</span></div>
            <div className="brand-subtitle">AI SECURITY PLATFORM</div>
          </div>
        </div>

        <div className="workspace-label">WORKSPACE</div>
        <div className="workspace">
          <div className="workspace-avatar">A</div>
          <div><strong>Local Environment</strong><small>Ubuntu • VirtualBox</small></div>
          <CircleDot size={14} className="online-dot" />
        </div>

        <div className="nav-label">MONITORING</div>
        <nav>
          {navItems.map(({ name, icon: Icon }) => (
            <button
              key={name}
              className={`nav-item ${activeTab === name ? 'active' : ''}`}
              onClick={() => setActiveTab(name)}
            >
              <Icon size={18} />
              <span>{name}</span>
              {name === 'Security Alerts' && alerts.length > 0 && (
                <span className="nav-count">{alerts.length}</span>
              )}
            </button>
          ))}
        </nav>

        <div className="nav-label system-label">SYSTEM</div>
        <button className="nav-item" onClick={loadData}>
          <RefreshCw size={18} /><span>Refresh Data</span>
        </button>
        <button className="nav-item" onClick={() => setActiveTab('Settings')}>
          <Settings size={18} /><span>Settings</span>
        </button>

        <div className="sidebar-bottom">
          <div className="protection-card">
            <div className="protection-icon"><ShieldCheck size={20} /></div>
            <strong>Monitoring Active</strong>
            <p>Local process and file-event monitoring is enabled.</p>
            <div className="protection-status"><span /> SYSTEM ONLINE</div>
          </div>
          <div className="profile">
            <div className="profile-avatar">AS</div>
            <div><strong>Security Analyst</strong><small>Local Administrator</small></div>
            <Settings size={16} />
          </div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div className="breadcrumbs">Workspace <ChevronRight size={14} /> <strong>{activeTab}</strong></div>
          <div className="topbar-right">
            <div className="live-status"><span /> LIVE MONITORING</div>
            <button className="icon-button" title="Refresh" onClick={loadData}>
              <RefreshCw size={17} />
            </button>
            <button className="icon-button" title="Notifications" onClick={() => setActiveTab('Security Alerts')}>
              <Bell size={18} />
            </button>
          </div>
        </header>

        <section className="page-heading">
          <div>
            <div className="eyebrow"><span /> SECURITY OPERATIONS CENTER</div>
            <h1>{activeTab === 'Overview' ? 'Security Overview' : activeTab}</h1>
            <p>Monitor system activity, inspect processes, and review file-system events.</p>
          </div>
          <div className="heading-actions">
            <div className="updated-label"><Clock size={14} /> Updated {lastUpdated.toLocaleTimeString()}</div>
            <button className="primary-button" onClick={loadData}><RefreshCw size={16} /> Refresh</button>
          </div>
        </section>

        {loading && !dashboard && <div className="loading-banner">Connecting to AGENTSENTRY API…</div>}

        {!loading && !dashboard && (
          <div className="error-banner">
            <AlertTriangle size={19} />
            <div><strong>Backend connection unavailable</strong><p>Start the FastAPI server on port 8000, then click Refresh.</p></div>
          </div>
        )}

        {activeTab === 'Settings' ? (
          <div className="panel settings-panel">
            <h2>Environment Settings</h2>
            <p><strong>API endpoint:</strong> {API}</p>
            <p><strong>Refresh interval:</strong> 5 seconds</p>
            <p><strong>Environment:</strong> Ubuntu VirtualBox</p>
            <p>Process information is read from the local operating system. File events are limited to the configured AGENTSENTRY test directory.</p>
          </div>
        ) : activeTab === 'Processes' ? (
          <section className="panel">
            <div className="panel-heading"><div><h2>Running Processes</h2><p>Live process information from the local system</p></div><span className="pill">{processes.length} processes</span></div>
            <ProcessTable processes={visibleProcesses} />
          </section>
        ) : activeTab === 'File Events' ? (
          <section className="panel">
            <div className="panel-heading"><div><h2>Recent File Events</h2><p>Observed activity in the monitored test directory</p></div><span className="pill">{dashboard?.file_event_count || 0} events</span></div>
            <EventList events={events} />
          </section>
        ) : activeTab === 'Security Alerts' ? (
          <section className="panel">
            <div className="panel-heading"><div><h2>Security Alerts</h2><p>Rule-based findings from the local event analyzer</p></div><span className="pill">{dashboard?.alert_count || 0} alerts</span></div>
            <AlertList alerts={alerts} />
          </section>
        ) : (
          <>
            <section className="stats-grid">
              <StatCard title="Running Processes" value={(dashboard?.process_count ?? 0).toLocaleString()} detail="Processes visible to this user" icon={Cpu} color="blue" />
              <StatCard title="File Events" value={(dashboard?.file_event_count ?? 0).toLocaleString()} detail="Recorded file-system events" icon={Activity} color="purple" />
              <StatCard title="Security Alerts" value={(dashboard?.alert_count ?? 0).toLocaleString()} detail="Rule matches recorded" icon={ShieldAlert} color="orange" />
              <StatCard title="High Severity" value={(dashboard?.high_alert_count ?? 0).toLocaleString()} detail="High-severity rule matches" icon={AlertTriangle} color="red" />
            </section>
	    <section className="panel incident-timeline">
  <div className="panel-heading">
    <div>
      <h2>Incident Timeline</h2>
      <p>Latest observed file-system activity</p>
    </div>
    <span className="pill">
      <span className="pill-dot" /> LIVE EVENTS
    </span>
  </div>

  {timelineEvents.length > 0 ? (
    <div className="timeline-track">
      {timelineEvents.map((item, index) => (
        <div className="timeline-event" key={`${item.time}-${index}`}>
          <div className="timeline-time">{item.time}</div>

          <div
            className={`timeline-marker ${
              item.event?.event === 'deleted'
                ? 'timeline-marker-alert'
                : ''
            }`}
          />

          <div className="timeline-card">
            <strong>{item.title}</strong>
            <span>{item.detail}</span>
          </div>
        </div>
      ))}
    </div>
  ) : (
    <div className="empty-state">
      <Eye size={22} />
      <p>
        No events yet. Create or edit a file in ~/AGENTSENTRY/test_files.
      </p>
    </div>
  )}
</section>
            <section className="bottom-grid">
              <div className="panel">
                <div className="panel-heading">
                  <div>
                    <h2>Agent Executions</h2>
                    <p>Sandbox executions reconstructed from enforcement evidence</p>
                  </div>
                  <span className="pill">{agents.length} executions</span>
                </div>
                {agents.length === 0 ? (
                  <div className="empty-state">
                    <ShieldCheck size={22} />
                    <p>No sandbox executions recorded yet. Run the agent sandbox test to generate evidence.</p>
                  </div>
                ) : (
                  <div className="activity-list">
                    {agents.slice(0, 5).map((agent) => (
                      <div className="activity-item" key={agent.execution_id}>
                        <div className="activity-icon">
                          <ShieldCheck size={16} />
                        </div>
                        <div className="activity-content">
                          <strong>Execution {agent.execution_id.slice(0, 8)}</strong>
                          <p>PID: {agent.pid ?? '—'} · Landlock ABI: {agent.landlock_abi ?? '—'}</p>
                          <small>{agent.workspace || 'Workspace unavailable'}</small>
                        </div>
                        <span className="event-type">{agent.status || 'unknown'}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="panel">
                <div className="panel-heading">
                  <div>
                    <h2>Kernel Enforcement Events</h2>
                    <p>Recorded filesystem operations in the sandbox test</p>
                  </div>
                  <span className="pill">{enforcement.events.length} events</span>
                </div>
                <div className="posture-row">
                  <span><ShieldAlert size={16} /> Confirmed kernel denials</span>
                  <b>{enforcement.confirmed_denials}</b>
                </div>
                {enforcement.events.length === 0 ? (
                  <div className="empty-state">
                    <Eye size={22} />
                    <p>No enforcement events recorded yet.</p>
                  </div>
                ) : (
                  <div className="activity-list">
                    {enforcement.events.slice(0, 5).map((event, index) => (
                      <div className="activity-item" key={`${event.execution_id}-${event.timestamp}-${index}`}>
                        <div className={`activity-icon ${event.outcome === 'denied' ? 'activity-danger' : ''}`}>
                          {event.outcome === 'denied' ? <ShieldAlert size={16} /> : <ShieldCheck size={16} />}
                        </div>
                        <div className="activity-content">
                          <strong>{(event.outcome || event.kind || 'event').toUpperCase()}</strong>
                          <p>{event.operation || event.kind || 'Sandbox event'} · {event.path || 'No path recorded'}</p>
                          <small>{event.enforcement || 'Evidence recorded'}{event.error?.errno ? ` · errno ${event.error.errno}` : ''}</small>
                        </div>
                        <span className="event-type">{event.outcome || event.kind || 'EVENT'}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </section>

            <section className="panel">
              <div className="panel-heading">
                <div>
                  <h2>Explainable AI (XAI)</h2>
                  <p>Evidence-based explanations of recorded sandbox activity</p>
                </div>
                <span className="pill">{xaiExplanations.length} explanations</span>
              </div>

              {xaiExplanations.length === 0 ? (
                <div className="empty-state">
                  <Eye size={22} />
                  <p>No explanations available. Generate them with the XAI explainer first.</p>
                </div>
              ) : (
                <div className="activity-list">
                  {xaiExplanations.slice(0, 5).map((item, index) => (
                    <div className="activity-item" key={`${item.execution_id}-${item.timestamp}-${index}`}>
                      <div className={`activity-icon ${item.title?.includes('denied') ? 'activity-danger' : ''}`}>
                        {item.title?.includes('denied') ? <ShieldAlert size={16} /> : <Eye size={16} />}
                      </div>
                      <div className="activity-content">
                        <strong>{item.title || 'Event explanation'}</strong>
                        <p>{item.explanation || 'No explanation recorded.'}</p>
                        <small>
                          {item.evidence?.enforcement || item.evidence?.workspace || item.evidence?.status || 'Evidence recorded'}
                          {item.evidence?.errno ? ` · errno ${item.evidence.errno}` : ''}
                        </small>
                      </div>
                    </div>
                  ))}
                </div>
              )}
              <div className="disclaimer">
                Explanations summarize recorded evidence. Security enforcement is performed by the operating system and deterministic policy, not by an AI model.
              </div>
            </section>

            <section className="charts-grid">
              <div className="panel chart-panel">
                <div className="panel-heading"><div><h2>Activity Overview</h2><p>Recorded file events and sample activity timeline</p></div><span className="pill"><span className="pill-dot" /> LIVE DATA</span></div>
                <div className="chart-legend"><span className="legend-dot blue-dot" /> File event count <span className="chart-note">Sample
 timeline</span></div>
                <div className="chart-area">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={eventChart}>
                      <defs><linearGradient id="eventFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%"stopColor="#DFFF45" stopOpacity={0.3} /><stop offset="100%" stopColor="#6687ff" stopOpacity={0.01} /></linearGradient></defs>
                      <CartesianGrid stroke="#242d40" strokeDasharray="3 5" vertical={false} />
                      <XAxis dataKey="time" stroke="#78849b" tickLine={false} axisLine={false} />
                      <YAxis stroke="#78849b" tickLine={false} axisLine={false} width={28} />
                      <Tooltip contentStyle={{ background: '#151d2d', border: '1px solid #303c52', borderRadius: 8 }} />
                      <Area type="monotone" dataKey="events" stroke="#DFFF45" strokeWidth={2.5} fill="url(#eventFill)" />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div className="panel summary-panel">
                <div className="panel-heading"><div><h2>Security Posture</h2><p>Current local monitoring status</p></div><ShieldCheck size={21} className="green-text" /></div>
                <div className="posture-score"><div className="score-ring"><div><strong>{dashboard?.high_alert_count ? 'Review' : 'OK'}</strong><small>Rule status</small></div></div><div><strong>{dashboard?.high_alert_count ? 'Attention required' : 'No high-severity alerts recorded'}</strong><p>{dashboard?.high_alert_count ? 'Review the high-severity findings.' : 'No high-severity rule matches currently recorded.'}</p></div></div>
                <div className="posture-row"><span><CheckCircle2 size={16} /> Process inventory</span><b>Available</b></div>
                <div className="posture-row"><span><CheckCircle2 size={16} /> File event log</span><b>Available</b></div>
                <div className="posture-row"><span><CircleDot size={16} /> Rule-based analysis</span><b>Basic</b></div>
                <div className="disclaimer">Demonstration status only. This is not a guarantee that the system is secure.</div>
              </div>
            </section>

            <section className="bottom-grid">
              <div className="panel">
                <div className="panel-heading"><div><h2>Process Monitor</h2><p>Processes using the most resident memory</p></div><button className="text-button" onClick={() => setActiveTab('Processes')}>View all <ChevronRight size={15} /></button></div>
                <ProcessTable processes={visibleProcesses.slice(0, 5)} />
              </div>
              <div className="panel">
                <div className="panel-heading"><div><h2>Recent Security Activity</h2><p>Latest observed file events</p></div><button className="text-button" onClick={() => setActiveTab('File Events')}>View all <ChevronRight size={15} /></button></div>
                <EventList events={events.slice(0, 5)} />
              </div>
            </section>

            <section className="panel alert-panel">
              <div className="panel-heading"><div><h2>Security Alerts</h2><p>Findings emitted by the rule-based analyzer</p></div><button className="text-button" onClick={() => setActiveTab('Security Alerts')}>View alerts <ChevronRight size={15} /></button></div>
              <AlertList alerts={alerts.slice(0, 3)} />
            </section>
          </>
        )}

        <footer><span><ShieldCheck size={15} /> AGENTSENTRY</span><span>Local security monitoring • Demo build</span></footer>
      </main>
    </div>
  );
}

function ProcessTable({ processes }) {
  if (!processes.length) return <div className="empty-state"><Cpu size={24} /><p>No process data available.</p></div>;

  return (
    <div className="table-wrap">
      <table><thead><tr><th>PROCESS</th><th>PID</th><th>USER</th><th>STATUS</th><th>MEMORY</th></tr></thead>
        <tbody>{processes.map((p, index) => (
          <tr key={`${p.pid}-${index}`}>
            <td><div className="process-name"><span className="process-icon"><Terminal size={15} /></span><strong>{p.name || 'Unknown'}</strong></div></td>
            <td className="muted-cell">{p.pid}</td>
            <td className="muted-cell">{p.username || '—'}</td>
            <td><span className={`status-tag ${(p.status || '').toLowerCase() === 'running' ? 'status-running' : ''}`}><span />{p.status || 'unknown'}</span></td>
            <td>{((p.memory_rss_bytes || 0) / 1024 / 1024).toFixed(1)} MB</td>
          </tr>
        ))}</tbody>
      </table>
    </div>
  );
}

function EventList({ events }) {
  if (!events.length) return <div className="empty-state"><Eye size={24} /><p>No file events recorded yet. Create or edit a file in ~/AGENTSENTRY/test_files.</p></div>;

  return <div className="activity-list">{events.map((event, index) => (
    <div className="activity-item" key={`${event.timestamp}-${index}`}>
      <div className={`activity-icon ${event.event === 'deleted' ? 'activity-warning' : ''}`}><FileSearch size={16} /></div>
      <div className="activity-content"><strong>{event.event || 'event'} <span>file</span></strong><p>{event.path || 'Unknown path'}</p><small>{event.timestamp ? new Date(event.timestamp).toLocaleTimeString() : 'Time unavailable'}</small></div>
      <span className="event-type">{event.event || 'EVENT'}</span>
    </div>
  ))}</div>;
}

function AlertList({ alerts }) {
  if (!alerts.length) return <div className="empty-state"><CheckCircle2 size={24} /><p>No rule-based alerts recorded. This does not prove the system is threat-free.</p></div>;

  return <div className="activity-list">{alerts.map((alert, index) => (
    <div className="activity-item" key={`${alert.timestamp}-${index}`}>
      <div className={`activity-icon ${alert.severity === 'HIGH' ? 'activity-danger' : 'activity-warning'}`}><AlertTriangle size={16} /></div>
      <div className="activity-content"><strong>{alert.rule || 'Rule match'} <span>• {alert.severity || 'UNKNOWN'}</span></strong><p>{alert.message || 'No details available'}</p><small>{alert.timestamp ? new Date(alert.timestamp).toLocaleString() : ''}</small></div>
      <span className={`severity-tag ${(alert.severity || '').toLowerCase()}`}>{alert.severity || 'UNKNOWN'}</span>
    </div>
  ))}</div>;
}

export default App;
