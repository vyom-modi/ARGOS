import { useState, useCallback, useRef } from 'react';
import { Play, AlertTriangle, CheckCircle, Shield, Activity, Cpu, Clock, DollarSign, XCircle, History } from 'lucide-react';
import GraphView from './components/GraphView';
import TerminalView from './components/TerminalView';
import DiffView from './components/DiffView';
import Modal from './components/Modal';
import MissionDialog from './components/MissionDialog';
import { useWebSocket } from './hooks/useWebSocket';

const BACKEND_WS_URL = 'ws://localhost:8000/ws';

interface Mission {
  id: string;
  name: string;
  status: 'running' | 'success' | 'failed' | 'pending';
  time: string;
  logs: string[];
}

function App() {
  const [activeNode, setActiveNode] = useState<string | null>(null);
  const [logs, setLogs] = useState<string[]>(['ARGOS System Terminal v1.0.0', '[System] ARGOS Initialized. Awaiting mission...']);
  const [showApprovalModal, setShowApprovalModal] = useState(false);
  const [showMissionDialog, setShowMissionDialog] = useState(false);
  const [approvalStatus, setApprovalStatus] = useState<"NONE" | "PENDING" | "APPROVED" | "REJECTED">("NONE");
  const [codeDiff, setCodeDiff] = useState<{ old: string; new: string } | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [telemetry, setTelemetry] = useState({ tokens: 0, latency: 0, cost: 0 });
  const [missions, setMissions] = useState<Mission[]>([]);
  const [selectedMission, setSelectedMission] = useState<Mission | null>(null);
  const [patchUrl, setPatchUrl] = useState<string | null>(null);
  const missionIdRef = useRef(0);

  const handleWebSocketMessage = useCallback((data: any) => {
    console.log('WS Message:', data);

    if (data.type === 'log') {
      setLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] ${data.content}`]);
      if (data.content.includes('✅ Patch saved to:')) {
        const patchPath = data.content.split('saved to: ')[1].trim();
        const filename = patchPath.split('/').pop();
        if (filename) {
          setPatchUrl(`http://localhost:8000/download_patch/${filename}`);
        }
      }
    }
    if (data.type === 'node_update') {
      setActiveNode(data.node);
    }
    if (data.type === 'approval_required') {
      setApprovalStatus('PENDING');
      setCodeDiff({ old: data.old_code || '', new: data.new_code || '' });
      setShowApprovalModal(true);
    }
    if (data.type === 'telemetry') {
      setTelemetry(data.telemetry);
    }
    if (data.type === 'mission_complete') {
      setIsRunning(false);
      setActiveNode(null);
      // Update current mission status
      setMissions(prev => prev.map(m =>
        m.status === 'running' ? { ...m, status: 'success' as const } : m
      ));
    }
  }, []);

  const { isConnected, send } = useWebSocket(BACKEND_WS_URL, {
    onMessage: handleWebSocketMessage,
    onOpen: () => setLogs(prev => [...prev, '[System] Connected to ARGOS Backend.']),
    onClose: () => setLogs(prev => [...prev, '[System] Disconnected from Backend. Reconnecting...']),
  });

  const handleStartMission = (mission: { type: string; missionType: string; target: string; description: string }) => {
    if (!isConnected) {
      setLogs(prev => [...prev, '[Error] Backend not connected.']);
      return;
    }

    missionIdRef.current += 1;
    const missionLabels: Record<string, string> = {
      'security': 'Security Scan',
      'audit': 'Dependency Audit',
      'fix': 'Bug Analysis',
      'custom': 'Custom Task',
    };
    const newMission: Mission = {
      id: String(missionIdRef.current),
      name: missionLabels[mission.missionType] || 'Scan',
      status: 'running',
      time: new Date().toLocaleTimeString(),
      logs: [],
    };

    setMissions(prev => [newMission, ...prev]);
    setIsRunning(true);
    setApprovalStatus('NONE');
    setPatchUrl(null);
    setLogs(prev => [...prev, `[System] Starting ${missionLabels[mission.missionType]}: ${mission.target}`]);
    send({
      type: 'start_mission',
      payload: {
        message: mission.description,
        target_type: mission.type,
        target: mission.target,
        mission_type: mission.missionType
      }
    });
  };


  const handleApprove = () => {
    setApprovalStatus('APPROVED');
    send({ type: 'approval', payload: { approved: true } });
    setShowApprovalModal(false);
    setLogs(prev => [...prev, `[Human] Fix APPROVED.`]);
  };

  const handleReject = () => {
    setApprovalStatus('REJECTED');
    send({ type: 'approval', payload: { approved: false } });
    setShowApprovalModal(false);
    setLogs(prev => [...prev, `[Human] Fix REJECTED. Requesting retry...`]);
  };

  const handleSelectMission = (mission: Mission) => {
    setSelectedMission(mission);
    // In a real app, this would load the mission's logs and state
    setLogs(prev => [...prev, `[System] Viewing mission: ${mission.name}`]);
  };

  return (
    <div className="h-screen w-screen bg-background flex text-foreground overflow-hidden font-sans">
      {/* Sidebar - History */}
      <aside className="w-64 border-r border-border flex flex-col bg-card/50 shrink-0">
        <div className="p-4 border-b border-border">
          <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-400">ARGOS</h1>
          <p className="text-xs text-secondary mt-1">Autonomous Repository Guardian & Operational Swarm</p>
        </div>

        <div className="flex-1 p-4 overflow-y-auto">
          <h3 className="text-xs font-bold text-secondary uppercase mb-3 px-1 flex items-center gap-1">
            <History size={12} /> Mission History
          </h3>
          <div className="space-y-2">
            {missions.length === 0 ? (
              <p className="text-xs text-secondary/60 text-center py-4">No missions yet.<br />Click "New Mission" to start.</p>
            ) : (
              missions.map(m => (
                <button
                  key={m.id}
                  onClick={() => handleSelectMission(m)}
                  className={`w-full p-3 rounded-lg border text-left transition-colors ${selectedMission?.id === m.id
                    ? 'bg-primary/10 border-primary/30'
                    : 'border-border hover:bg-secondary/10'
                    }`}
                >
                  <div className="flex justify-between items-start mb-1">
                    <span className="font-semibold text-sm">{m.name}</span>
                    <span className={`text-[10px] px-1.5 rounded ${m.status === 'success' ? 'bg-green-500/20 text-green-400' :
                      m.status === 'running' ? 'bg-blue-500/20 text-blue-400 animate-pulse' :
                        m.status === 'failed' ? 'bg-red-500/20 text-red-400' :
                          'bg-yellow-500/20 text-yellow-400'
                      }`}>
                      {m.status}
                    </span>
                  </div>
                  <p className="text-[10px] text-secondary/60 mt-1">{m.time}</p>
                </button>
              ))
            )}
          </div>
        </div>

        <div className="p-4 border-t border-border">
          <button
            onClick={() => setShowMissionDialog(true)}
            disabled={isRunning || !isConnected}
            className="w-full py-2 bg-primary hover:bg-blue-600 disabled:bg-secondary/30 disabled:cursor-not-allowed text-white rounded-lg flex items-center justify-center gap-2 text-sm font-medium shadow-lg shadow-blue-500/20 transition-all"
          >
            <Play size={16} /> {isRunning ? 'Running...' : 'New Mission'}
          </button>
          <div className={`mt-2 text-xs text-center ${isConnected ? 'text-green-400' : 'text-red-400'}`}>
            {isConnected ? '● Connected' : '○ Disconnected'}
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top Bar / Header */}
        <header className="h-12 border-b border-border flex items-center px-4 justify-between bg-card/30 backdrop-blur shrink-0">
          <div className="flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></span>
            <span className="text-sm font-medium">{isConnected ? 'System Online' : 'Offline'}</span>
          </div>
          <div className="flex items-center gap-4 text-xs">
            <div className="flex items-center gap-1"><Cpu size={14} className="text-purple-400" /><span>{telemetry.tokens} tokens</span></div>
            <div className="flex items-center gap-1"><Clock size={14} className="text-yellow-400" /><span>{telemetry.latency}ms</span></div>
            <div className="flex items-center gap-1"><DollarSign size={14} className="text-green-400" /><span>${telemetry.cost.toFixed(4)}</span></div>
          </div>
        </header>

        <div className="flex-1 flex overflow-hidden p-4 gap-4">
          {/* Center Panel: Graph + Terminal */}
          <div className="flex-1 flex flex-col gap-4 min-w-0">
            <div className="flex-[3] min-h-0">
              <GraphView activeNode={activeNode} />
            </div>
            <div className="flex-[2] min-h-0">
              <TerminalView logs={logs} />
            </div>
          </div>

          {/* Right Panel */}
          <div className="w-80 flex flex-col gap-4 shrink-0 overflow-y-auto">
            <div className="bg-card rounded-xl border border-border p-4">
              <h3 className="text-sm font-bold mb-3 flex items-center gap-2">
                <Shield size={16} className="text-purple-500" /> Agent Swarm Status
              </h3>
              <div className="space-y-2">
                <StatusRow label="Supervisor" status={activeNode === 'Supervisor' ? 'Planning' : 'Idle'} active={activeNode === 'Supervisor'} />
                <StatusRow label="Explorer" status={activeNode === 'Explorer' ? 'Scanning...' : 'Idle'} active={activeNode === 'Explorer'} />
                <StatusRow label="Auditor" status={activeNode === 'Auditor' ? 'Auditing...' : 'Idle'} active={activeNode === 'Auditor'} />
                <StatusRow label="Execution" status={activeNode === 'Execution' ? 'Testing...' : 'Idle'} active={activeNode === 'Execution'} />
                <StatusRow label="Human" status={approvalStatus === 'PENDING' ? 'Awaiting...' : 'Idle'} active={approvalStatus === 'PENDING'} />
              </div>
            </div>

            <div className="bg-card rounded-xl border border-border p-4">
              <h3 className="text-sm font-bold mb-3 flex items-center gap-2">
                <Activity size={16} className="text-blue-500" /> Run Telemetry
              </h3>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div className="bg-secondary/10 rounded-lg p-3">
                  <p className="text-xs text-secondary">Tokens</p>
                  <p className="font-bold">{telemetry.tokens}</p>
                </div>
                <div className="bg-secondary/10 rounded-lg p-3">
                  <p className="text-xs text-secondary">Latency</p>
                  <p className="font-bold">{telemetry.latency}ms</p>
                </div>
                <div className="bg-secondary/10 rounded-lg p-3">
                  <p className="text-xs text-secondary">Cost</p>
                  <p className="font-bold">${telemetry.cost.toFixed(4)}</p>
                </div>
                <div className="bg-secondary/10 rounded-lg p-3">
                  <p className="text-xs text-secondary">Status</p>
                  <p className="font-bold">{isRunning ? 'Active' : 'Idle'}</p>
                </div>
              </div>
            </div>

            {approvalStatus === 'PENDING' && (
              <button
                onClick={() => setShowApprovalModal(true)}
                className="bg-yellow-500/10 border border-yellow-500/30 rounded-xl p-4 flex items-center gap-3 hover:bg-yellow-500/20 transition-colors"
              >
                <AlertTriangle className="text-yellow-500" />
                <div className="text-left">
                  <p className="font-bold text-yellow-400">Approval Pending</p>
                  <p className="text-xs text-secondary">Click to review proposed fix</p>
                </div>
              </button>
            )}

            {patchUrl && (
              <a
                href={patchUrl}
                download
                className="bg-green-500/10 border border-green-500/30 rounded-xl p-4 flex items-center gap-3 hover:bg-green-500/20 transition-colors cursor-pointer"
              >
                <CheckCircle className="text-green-500" />
                <div className="text-left">
                  <p className="font-bold text-green-400">Patch Available</p>
                  <p className="text-xs text-secondary">Click to download fix</p>
                </div>
              </a>
            )}
          </div>
        </div>
      </main>

      {/* Mission Dialog */}
      <MissionDialog
        isOpen={showMissionDialog}
        onClose={() => setShowMissionDialog(false)}
        onSubmit={handleStartMission}
      />

      {/* Approval Modal */}
      <Modal
        isOpen={showApprovalModal}
        onClose={() => setShowApprovalModal(false)}
        title="🔒 Human-in-the-Loop Approval"
      >
        <div className="p-4">
          <p className="text-sm text-secondary mb-4">
            The Auditor has identified a vulnerability and the Fixer has generated a patch.
            Please review the changes below before approving deployment.
          </p>
          {codeDiff && (
            <div className="border border-border rounded-lg overflow-hidden max-h-96">
              <DiffView oldCode={codeDiff.old} newCode={codeDiff.new} />
            </div>
          )}
        </div>
        <div className="p-4 border-t border-border flex gap-3">
          <button
            onClick={handleReject}
            className="flex-1 py-2.5 bg-secondary/10 hover:bg-red-500/20 text-foreground rounded-lg border border-border text-sm font-medium transition-colors flex items-center justify-center gap-2"
          >
            <XCircle size={16} /> Reject & Retry
          </button>
          <button
            onClick={handleApprove}
            className="flex-1 py-2.5 bg-success hover:bg-green-600 text-white rounded-lg shadow-lg shadow-green-500/20 text-sm font-bold transition-all flex items-center justify-center gap-2"
          >
            <CheckCircle size={16} /> Approve Fix
          </button>
        </div>
      </Modal>
    </div>
  );
}

function StatusRow({ label, status, active }: { label: string; status: string; active: boolean }) {
  return (
    <div className={`flex justify-between items-center p-2 rounded ${active ? 'bg-primary/10 border-primary/20 border' : 'bg-secondary/5'}`}>
      <span className={`text-sm ${active ? 'font-bold text-foreground' : 'text-secondary'}`}>{label}</span>
      <span className={`text-xs px-2 py-0.5 rounded-full ${active ? 'bg-primary/20 text-blue-400 animate-pulse' : 'text-secondary/60'}`}>
        {status}
      </span>
    </div>
  );
}

export default App;
