import { useMemo } from 'react';
import ReactFlow, { Background, Controls } from 'reactflow';
import type { Node, Edge } from 'reactflow';
import 'reactflow/dist/style.css';

// All nodes need to be 'default' type to have both source and target handles
const initialNodes: Node[] = [
    { id: 'Supervisor', position: { x: 300, y: 0 }, data: { label: 'Supervisor' } },
    { id: 'Explorer', position: { x: 50, y: 150 }, data: { label: 'Explorer' } },
    { id: 'Auditor', position: { x: 300, y: 150 }, data: { label: 'Auditor' } },
    { id: 'Execution', position: { x: 550, y: 150 }, data: { label: 'Execution' } },
    { id: 'Human', position: { x: 300, y: 300 }, data: { label: 'Human' } },
];

const initialEdges: Edge[] = [
    { id: 'e1-2', source: 'Supervisor', target: 'Explorer' },
    { id: 'e1-3', source: 'Supervisor', target: 'Auditor' },
    { id: 'e1-4', source: 'Supervisor', target: 'Execution' },
    { id: 'e1-5', source: 'Supervisor', target: 'Human' },
    // Returns
    { id: 'e2-1', source: 'Explorer', target: 'Supervisor', style: { strokeDasharray: '5,5' } },
    { id: 'e3-1', source: 'Auditor', target: 'Supervisor', style: { strokeDasharray: '5,5' } },
    { id: 'e4-1', source: 'Execution', target: 'Supervisor', style: { strokeDasharray: '5,5' } },
    { id: 'e5-1', source: 'Human', target: 'Supervisor', style: { strokeDasharray: '5,5' } },
];

interface GraphViewProps {
    activeNode: string | null;
}

export default function GraphView({ activeNode }: GraphViewProps) {
    const nodes = useMemo(() => {
        return initialNodes.map((node) => ({
            ...node,
            style: {
                background: node.id === activeNode ? '#3b82f6' : '#18181b',
                color: node.id === activeNode ? '#fff' : '#a1a1aa',
                border: node.id === activeNode ? '2px solid #60a5fa' : '1px solid #27272a',
                borderRadius: 8,
                padding: 10,
                width: 140,
            },
            data: {
                label: (
                    <div className="font-mono font-bold text-center">
                        {node.data.label}
                        {node.id === activeNode && <span className="block text-xs font-normal mt-1 animate-pulse">Running...</span>}
                    </div>
                )
            }
        }));
    }, [activeNode]);

    const edges = useMemo(() => {
        return initialEdges.map(edge => ({
            ...edge,
            animated: edge.source === activeNode || edge.target === activeNode,
            style: {
                ...edge.style,
                stroke: (edge.source === activeNode || edge.target === activeNode) ? '#3b82f6' : '#52525b',
                strokeWidth: (edge.source === activeNode || edge.target === activeNode) ? 2 : 1
            }
        }))
    }, [activeNode]);

    return (
        <div className="h-full w-full bg-background rounded-xl border border-border overflow-hidden relative">
            <div className="absolute top-4 left-4 z-10 bg-card/80 backdrop-blur px-3 py-1 rounded border border-border">
                <span className="text-xs text-secondary font-mono">Live Graph View</span>
            </div>
            <ReactFlow
                nodes={nodes}
                edges={edges}
                fitView
                minZoom={0.5}
                maxZoom={1.5}
                proOptions={{ hideAttribution: true }}
                nodesDraggable={false}
                nodesConnectable={false}
                elementsSelectable={false}
            >
                <Background color="#27272a" gap={20} size={1} />
                <Controls className="!bg-card !border-border [&>button]:!border-border [&>button]:!bg-card [&>button]:text-foreground [&>button:hover]:!bg-secondary/80 [&>button>svg]:fill-foreground [&>button>svg]:stroke-foreground" />
            </ReactFlow>
        </div>
    );
}
