import { useEffect, useRef } from 'react';
import { Terminal } from '@xterm/xterm';
import { FitAddon } from '@xterm/addon-fit';
import '@xterm/xterm/css/xterm.css';

interface TerminalViewProps {
    logs: string[];
}

export default function TerminalView({ logs }: TerminalViewProps) {
    const containerRef = useRef<HTMLDivElement>(null);
    const terminalRef = useRef<Terminal | null>(null);
    const fitAddonRef = useRef<FitAddon | null>(null);

    useEffect(() => {
        if (!containerRef.current) return;

        const term = new Terminal({
            theme: {
                background: '#18181b', // card color
                foreground: '#e4e4e7', // zinc-200
                cursor: '#a1a1aa',
                selectionBackground: '#3f3f46',
            },
            fontFamily: '"Fira Code", monospace',
            fontSize: 13,
            cursorBlink: true,
            convertEol: true, // Important for \n
        });

        const fitAddon = new FitAddon();
        term.loadAddon(fitAddon);

        term.open(containerRef.current);
        fitAddon.fit();

        terminalRef.current = term;
        fitAddonRef.current = fitAddon;

        term.writeln('\x1b[34mARGOS System Terminal v1.0.0\x1b[0m');
        term.writeln('Waiting for connection...');

        const handleResize = () => fitAddon.fit();
        window.addEventListener('resize', handleResize);

        return () => {
            term.dispose();
            window.removeEventListener('resize', handleResize);
        };
    }, []);

    useEffect(() => {
        if (terminalRef.current && logs.length > 0) {
            // Write only new logs? Simpler to just clear and rewrite or stream.
            // For now, assuming logs prop appends.
            terminalRef.current.clear(); // inefficient but simple for React state sync
            terminalRef.current.writeln('\x1b[34mARGOS System Terminal v1.0.0\x1b[0m');
            logs.forEach(log => terminalRef.current?.writeln(log));
        }
    }, [logs]);

    return (
        <div className="h-full w-full bg-card rounded-xl border border-border p-1 overflow-hidden flex flex-col">
            <div className="px-3 py-1 border-b border-border bg-card/50 flex justify-between items-center">
                <span className="text-xs text-secondary font-mono">Terminal (E2B Sandbox)</span>
                <div className="flex gap-1.5">
                    <div className="w-2.5 h-2.5 rounded-full bg-red-500/20 border border-red-500/50"></div>
                    <div className="w-2.5 h-2.5 rounded-full bg-yellow-500/20 border border-yellow-500/50"></div>
                    <div className="w-2.5 h-2.5 rounded-full bg-green-500/20 border border-green-500/50"></div>
                </div>
            </div>
            <div className="flex-1 p-2" ref={containerRef} />
        </div>
    );
}
