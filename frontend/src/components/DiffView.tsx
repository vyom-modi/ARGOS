import ReactDiffViewer from 'react-diff-viewer-continued';

interface DiffViewProps {
    oldCode: string;
    newCode: string;
}

export default function DiffView({ oldCode, newCode }: DiffViewProps) {
    return (
        <div className="h-full w-full bg-card rounded-xl border border-border overflow-hidden flex flex-col">
            <div className="px-3 py-1 border-b border-border bg-card/50 flex justify-between items-center">
                <span className="text-xs text-secondary font-mono">Proposed Fix (Diff)</span>
                <span className="text-[10px] uppercase font-bold text-success bg-success/10 px-1.5 py-0.5 rounded">Patch Ready</span>
            </div>
            <div className="flex-1 overflow-auto text-xs font-mono">
                <ReactDiffViewer
                    oldValue={oldCode}
                    newValue={newCode}
                    splitView={true}
                    useDarkTheme={true}
                    styles={{
                        variables: {
                            dark: {
                                diffViewerBackground: '#18181b',
                                diffViewerColor: '#fafafa',
                                addedBackground: '#042f2e', // darker green
                                addedColor: '#22c55e',
                                removedBackground: '#450a0a', // darker red
                                removedColor: '#ef4444',
                                wordAddedBackground: '#14532d',
                                wordRemovedBackground: '#7f1d1d',
                                diffViewerTitleBackground: '#27272a',
                                gutterBackground: '#18181b',
                                gutterBackgroundDark: '#18181b',
                                highlightBackground: '#2a2b32',
                                gutterColor: '#52525b',
                            }
                        },
                        line: {
                            padding: '2px 0',
                        }
                    }}
                />
            </div>
        </div>
    );
}
