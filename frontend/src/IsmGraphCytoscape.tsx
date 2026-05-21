import { useEffect, useRef } from "react";
import cytoscape, { type Core, type ElementDefinition } from "cytoscape";
import dagre from "cytoscape-dagre";

cytoscape.use(dagre);

export type IsmGraphData = {
  nodes: { id: string; node_type: string; label: string; meta: Record<string, unknown> }[];
  edges: {
    id: string;
    source: string;
    target: string;
    link_type: string;
    label: string;
    confidence: number;
  }[];
};

const LINK_COLORS: Record<string, string> = {
  controls: "#64748b",
  references: "#2563eb",
  duplicates: "#d97706",
  conflicts: "#dc2626",
  discipline_ref: "#7c3aed",
  requires_input_from: "#0891b2",
  produces_output_for: "#059669"
};

function nodeStyle(nodeType: string) {
  if (nodeType === "process") {
    return { shape: "round-rectangle" as const, backgroundColor: "#e0e7ff", borderColor: "#4f46e5" };
  }
  if (nodeType === "reference") {
    return { shape: "diamond" as const, backgroundColor: "#fef3c7", borderColor: "#d97706" };
  }
  return { shape: "ellipse" as const, backgroundColor: "#ecfdf5", borderColor: "#059669" };
}

export function IsmGraphCytoscape({ graph }: { graph: IsmGraphData }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);

  useEffect(() => {
    if (!containerRef.current || graph.nodes.length === 0) {
      return;
    }

    const elements: ElementDefinition[] = [
      ...graph.nodes.map((n) => {
        const style = nodeStyle(n.node_type);
        return {
          data: { id: n.id, label: n.label, nodeType: n.node_type },
          style: {
            "background-color": style.backgroundColor,
            "border-color": style.borderColor,
            "border-width": 2,
            shape: style.shape,
            label: n.label,
            "font-size": 10,
            "text-wrap": "wrap",
            "text-max-width": 120,
            "text-valign": "center",
            "text-halign": "center",
            width: n.node_type === "process" ? 140 : 90,
            height: 44
          }
        };
      }),
      ...graph.edges.map((e) => ({
        data: {
          id: e.id,
          source: e.source,
          target: e.target,
          linkType: e.link_type,
          label: e.link_type
        },
        style: {
          width: 1 + e.confidence,
          "line-color": LINK_COLORS[e.link_type] ?? "#94a3b8",
          "target-arrow-color": LINK_COLORS[e.link_type] ?? "#94a3b8",
          "target-arrow-shape": "triangle",
          "curve-style": "bezier",
          label: e.link_type,
          "font-size": 8,
          color: "#64748b"
        }
      }))
    ];

    cyRef.current?.destroy();
    const cy = cytoscape({
      container: containerRef.current,
      elements,
      layout: {
        name: "dagre",
        rankDir: "LR",
        nodeSep: 40,
        edgeSep: 20,
        rankSep: 80
      } as cytoscape.LayoutOptions,
      style: [
        {
          selector: "node",
          style: { color: "#0f172a" }
        },
        {
          selector: "edge",
          style: { "arrow-scale": 0.8 }
        }
      ],
      minZoom: 0.2,
      maxZoom: 3,
      wheelSensitivity: 0.2
    });
    cyRef.current = cy;

    return () => {
      cy.destroy();
      cyRef.current = null;
    };
  }, [graph]);

  return <div ref={containerRef} className="ism-cytoscape" role="img" aria-label="Граф связей ИСМ" />;
}
