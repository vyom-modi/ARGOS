import { useState } from 'react';
import { X, Rocket, FolderOpen, Github, AlertCircle, Shield, FileSearch, Bug, Wrench } from 'lucide-react';

interface MissionDialogProps {
    isOpen: boolean;
    onClose: () => void;
    onSubmit: (mission: { type: string; missionType: string; target: string; description: string }) => void;
}

const missionTypes = [
    { id: 'security', icon: Shield, label: 'Security Scan', description: 'Scan for vulnerabilities with Bandit' },
    { id: 'audit', icon: FileSearch, label: 'Dependency Audit', description: 'Check for outdated/vulnerable packages' },
    { id: 'fix', icon: Bug, label: 'Bug Analysis', description: 'Analyze code for potential bugs' },
    { id: 'custom', icon: Wrench, label: 'Custom Task', description: 'Describe a custom analysis task' },
];

export default function MissionDialog({ isOpen, onClose, onSubmit }: MissionDialogProps) {
    const [step, setStep] = useState<1 | 2>(1);
    const [selectedMissionType, setSelectedMissionType] = useState('security');
    const [targetType, setTargetType] = useState<'local' | 'github'>('local');
    const [targetPath, setTargetPath] = useState('');
    const [githubUrl, setGithubUrl] = useState('');
    const [customTask, setCustomTask] = useState('');
    const [error, setError] = useState('');

    if (!isOpen) return null;

    const validateStep2 = () => {
        if (targetType === 'local') {
            if (!targetPath.trim()) {
                setError('Please enter a local path');
                return false;
            }
            if (!targetPath.startsWith('/')) {
                setError('Please enter an absolute path (starting with /)');
                return false;
            }
        } else {
            if (!githubUrl.trim()) {
                setError('Please enter a GitHub URL');
                return false;
            }
            if (!githubUrl.includes('github.com')) {
                setError('Please enter a valid GitHub URL');
                return false;
            }
        }
        return true;
    };

    const handleNext = () => {
        if (step === 1) {
            setStep(2);
        }
    };

    const handleBack = () => {
        setStep(1);
        setError('');
    };

    const handleSubmit = () => {
        setError('');
        if (!validateStep2()) return;

        const target = targetType === 'local' ? targetPath : githubUrl;
        const missionLabel = missionTypes.find(m => m.id === selectedMissionType)?.label || 'Security Scan';
        const description = selectedMissionType === 'custom' && customTask
            ? customTask
            : `${missionLabel} on ${targetType === 'local' ? targetPath : githubUrl}`;

        onSubmit({
            type: targetType,
            missionType: selectedMissionType,
            target,
            description
        });
        onClose();
        // Reset state
        setStep(1);
        setTargetPath('');
        setGithubUrl('');
        setCustomTask('');
        setSelectedMissionType('security');
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
            <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />
            <div className="relative bg-card border border-border rounded-2xl shadow-2xl w-full max-w-lg overflow-hidden animate-in zoom-in-95 duration-200">
                {/* Header */}
                <div className="flex items-center justify-between p-4 border-b border-border">
                    <div className="flex items-center gap-2">
                        <Rocket className="text-primary" size={20} />
                        <h2 className="text-lg font-bold text-foreground">
                            New Mission {step === 2 ? '- Select Target' : ''}
                        </h2>
                    </div>
                    <button onClick={onClose} className="p-1.5 rounded-lg hover:bg-secondary/20 transition-colors">
                        <X size={18} />
                    </button>
                </div>

                {/* Step Indicator */}
                <div className="px-4 pt-3 flex gap-2">
                    <div className={`flex-1 h-1 rounded ${step >= 1 ? 'bg-primary' : 'bg-secondary/30'}`} />
                    <div className={`flex-1 h-1 rounded ${step >= 2 ? 'bg-primary' : 'bg-secondary/30'}`} />
                </div>

                {/* Body */}
                <div className="p-4">
                    {step === 1 ? (
                        <>
                            <p className="text-sm text-secondary mb-4">Select mission type:</p>
                            <div className="grid grid-cols-2 gap-3 mb-4">
                                {missionTypes.map(type => (
                                    <button
                                        key={type.id}
                                        onClick={() => setSelectedMissionType(type.id)}
                                        className={`p-4 rounded-xl border text-left transition-all ${selectedMissionType === type.id
                                                ? 'bg-primary/10 border-primary/50'
                                                : 'bg-secondary/5 border-border hover:bg-secondary/10'
                                            }`}
                                    >
                                        <type.icon size={24} className={selectedMissionType === type.id ? 'text-primary' : 'text-secondary'} />
                                        <p className="font-semibold mt-2 text-sm">{type.label}</p>
                                        <p className="text-xs text-secondary mt-1">{type.description}</p>
                                    </button>
                                ))}
                            </div>

                            {selectedMissionType === 'custom' && (
                                <textarea
                                    value={customTask}
                                    onChange={(e) => setCustomTask(e.target.value)}
                                    placeholder="Describe your custom task..."
                                    className="w-full p-3 bg-secondary/10 border border-border rounded-xl text-sm resize-none h-20 focus:outline-none focus:ring-2 focus:ring-primary/50"
                                />
                            )}
                        </>
                    ) : (
                        <>
                            <p className="text-sm text-secondary mb-4">Select target codebase:</p>

                            {/* Target Type Tabs */}
                            <div className="flex gap-2 mb-4">
                                <button
                                    onClick={() => { setTargetType('local'); setError(''); }}
                                    className={`flex-1 py-3 px-4 rounded-xl border flex items-center justify-center gap-2 transition-all ${targetType === 'local'
                                            ? 'bg-primary/10 border-primary/50 text-primary'
                                            : 'bg-secondary/5 border-border hover:bg-secondary/10 text-secondary'
                                        }`}
                                >
                                    <FolderOpen size={18} />
                                    <span className="font-medium">Local Path</span>
                                </button>
                                <button
                                    onClick={() => { setTargetType('github'); setError(''); }}
                                    className={`flex-1 py-3 px-4 rounded-xl border flex items-center justify-center gap-2 transition-all ${targetType === 'github'
                                            ? 'bg-primary/10 border-primary/50 text-primary'
                                            : 'bg-secondary/5 border-border hover:bg-secondary/10 text-secondary'
                                        }`}
                                >
                                    <Github size={18} />
                                    <span className="font-medium">GitHub Repo</span>
                                </button>
                            </div>

                            {/* Input Fields */}
                            {targetType === 'local' ? (
                                <div>
                                    <input
                                        type="text"
                                        value={targetPath}
                                        onChange={(e) => { setTargetPath(e.target.value); setError(''); }}
                                        placeholder="/Users/you/projects/my-app"
                                        className="w-full p-3 bg-secondary/10 border border-border rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 font-mono"
                                    />
                                </div>
                            ) : (
                                <div>
                                    <input
                                        type="text"
                                        value={githubUrl}
                                        onChange={(e) => { setGithubUrl(e.target.value); setError(''); }}
                                        placeholder="https://github.com/username/repo"
                                        className="w-full p-3 bg-secondary/10 border border-border rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
                                    />
                                </div>
                            )}

                            {error && (
                                <div className="mt-3 p-3 bg-red-500/10 border border-red-500/30 rounded-lg flex items-center gap-2 text-red-400 text-sm">
                                    <AlertCircle size={16} />
                                    {error}
                                </div>
                            )}
                        </>
                    )}
                </div>

                {/* Footer */}
                <div className="p-4 border-t border-border flex gap-3">
                    {step === 1 ? (
                        <>
                            <button onClick={onClose} className="flex-1 py-2.5 bg-secondary/10 hover:bg-secondary/20 text-foreground rounded-lg border border-border text-sm font-medium transition-colors">
                                Cancel
                            </button>
                            <button onClick={handleNext} className="flex-1 py-2.5 bg-primary hover:bg-blue-600 text-white rounded-lg shadow-lg shadow-blue-500/20 text-sm font-bold transition-all">
                                Next →
                            </button>
                        </>
                    ) : (
                        <>
                            <button onClick={handleBack} className="flex-1 py-2.5 bg-secondary/10 hover:bg-secondary/20 text-foreground rounded-lg border border-border text-sm font-medium transition-colors">
                                ← Back
                            </button>
                            <button onClick={handleSubmit} className="flex-1 py-2.5 bg-primary hover:bg-blue-600 text-white rounded-lg shadow-lg shadow-blue-500/20 text-sm font-bold transition-all flex items-center justify-center gap-2">
                                <Rocket size={16} />
                                Launch
                            </button>
                        </>
                    )}
                </div>
            </div>
        </div>
    );
}
