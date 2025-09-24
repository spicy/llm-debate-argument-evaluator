"""
TODO: This module...
"""

import asyncio
import os
import tempfile
import webbrowser
from typing import Any, Dict, List, Tuple, Optional

try:
    import networkx as nx  # type: ignore

    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    nx = None

try:
    import plotly.graph_objects as go  # type: ignore
    import plotly.express as px  # type: ignore
    from plotly.subplots import make_subplots  # type: ignore

    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    go = None
    px = None

from visualization.base_renderer import BaseRenderer
from utils.logger import logger, ensure_logger_in_thread


class PlotlyRenderer(BaseRenderer):
    """Renders tree using Plotly for interactive web-based visualization"""

    def __init__(
        self,
        tree_subject,
        auto_open: bool = True,
        output_dir: Optional[str] = None,
    ):
        super().__init__(tree_subject)
        if not PLOTLY_AVAILABLE:
            raise ImportError(
                "Plotly is not installed. Install with: pip install plotly"
            )
        if not NETWORKX_AVAILABLE:
            raise ImportError(
                "NetworkX is not installed. Install with: pip install networkx"
            )

        logger.debug(
            f"Plotly available: {PLOTLY_AVAILABLE}, NetworkX available: {NETWORKX_AVAILABLE}"
        )

        self.auto_open = auto_open
        self.output_dir = output_dir or tempfile.gettempdir()
        self.fig = None
        self.temp_files = []  # Track temp files for cleanup

        logger.info("PlotlyRenderer initialized successfully")

    def render_tree(self, tree: Dict[str, Any], optimal_path: Optional[List] = None):
        """Create Plotly visualization from tree"""
        if not tree:
            logger.warning("Cannot render empty tree")
            return

        try:
            logger.debug(f"Rendering tree with {len(tree)} nodes")

            # Build NetworkX graph for layout
            graph = self._build_networkx_graph(tree)
            if not graph.nodes():
                logger.warning("No nodes in graph after building")
                return
            logger.debug(f"Built graph with {graph.number_of_nodes()} nodes")

            # Calculate hierarchical layout
            pos = self._calculate_hierarchical_layout(graph)
            if not pos:
                logger.warning("Failed to calculate node positions")
                return
            logger.debug(f"Calculated positions for {len(pos)} nodes")

            # Create Plotly figure
            logger.debug("Creating Plotly figure...")
            self.fig = self._create_plotly_figure(tree, graph, pos, optimal_path)
            if self.fig:
                logger.debug("Successfully created Plotly figure")
            else:
                logger.warning("Failed to create Plotly figure")
                return None

            # Always save the file, optionally open in browser
            output_path = self._save_and_open()
            logger.debug("Successfully rendered tree with Plotly")
            return output_path

        except Exception as e:
            logger.error(f"Error rendering tree: {e}", exc_info=True)
            raise

    def _build_networkx_graph(self, tree: Dict[str, Any]):
        """Build NetworkX graph from tree"""
        G = nx.DiGraph()

        try:
            for node_id, node_data in tree.items():
                if not isinstance(node_data, dict):
                    logger.warning(
                        f"Skipping invalid node data for {node_id}: {type(node_data)}"
                    )
                    continue

                # Add node with sanitized data
                sanitized_data = {}
                for key, value in node_data.items():
                    # Only include serializable data for NetworkX
                    if isinstance(value, (str, int, float, bool, type(None))):
                        sanitized_data[key] = value

                G.add_node(str(node_id), **sanitized_data)

                # Add edges based on parent relationships
                parent = node_data.get("parent_id")
                if parent is not None and parent != -1:
                    parent_str = str(parent)
                    node_str = str(node_id)

                    # Only add edge if parent exists in tree
                    if parent_str in tree:
                        G.add_edge(parent_str, node_str)
                    else:
                        logger.debug(
                            f"Parent {parent_str} not found for node {node_str}"
                        )

            logger.debug(
                f"Built graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges"
            )
            return G

        except Exception as e:
            logger.error(f"Error building NetworkX graph: {e}", exc_info=True)
            # Return empty graph as fallback
            return nx.DiGraph()

    def _calculate_hierarchical_layout(self, graph) -> Dict[str, Tuple[float, float]]:
        """Calculate hierarchical layout positions"""
        if not graph.nodes():
            logger.warning("Cannot calculate layout for empty graph")
            return {}

        # Find root nodes (nodes with no incoming edges)
        root_nodes = [n for n, d in graph.in_degree() if d == 0]

        if not root_nodes:
            logger.warning("No root nodes found, using arbitrary node as root")
            # If no clear root, use the first node
            root_nodes = [list(graph.nodes())[0]]

        root = root_nodes[0]
        if len(root_nodes) > 1:
            logger.debug(f"Multiple root nodes found, using {root}")

        # Try hierarchical layout first
        try:
            pos = self._hierarchy_pos(graph, root)
            if pos:
                logger.debug(
                    f"Successfully calculated hierarchical layout for {len(pos)} nodes"
                )
                return pos
        except Exception as e:
            logger.warning(f"Hierarchical layout failed: {e}", exc_info=True)

        # Fallback to spring layout
        try:
            logger.debug("Using spring layout as fallback")
            pos = nx.spring_layout(graph, k=3, iterations=50, seed=42)
            return pos
        except Exception as e:
            logger.error(f"Spring layout also failed: {e}", exc_info=True)
            # Last resort: simple grid layout
            return self._create_simple_layout(graph)

    def _create_simple_layout(self, graph) -> Dict[str, Tuple[float, float]]:
        """Create a simple grid layout as last resort"""
        nodes = list(graph.nodes())
        pos = {}

        # Arrange in a simple grid
        cols = int(len(nodes) ** 0.5) + 1
        for i, node in enumerate(nodes):
            x = (i % cols) / max(1, cols - 1) if cols > 1 else 0.5
            y = (
                (i // cols) / max(1, (len(nodes) - 1) // cols)
                if len(nodes) > cols
                else 0.5
            )
            pos[node] = (x, y)

        logger.debug(f"Created simple grid layout for {len(nodes)} nodes")
        return pos

    def _hierarchy_pos(
        self,
        G,
        root: str,
        width: float = 1.0,
        vert_gap: float = 0.2,
        vert_loc: float = 0,
        xcenter: float = 0.5,
    ) -> Dict[str, Tuple[float, float]]:
        """Create a hierarchical layout for trees"""
        pos = {}

        def _hierarchy_pos_recursive(
            G, root, width, vert_gap, vert_loc, xcenter, pos, parent=None, parsed=None
        ):
            if parsed is None:
                parsed = []

            if root not in parsed:
                parsed.append(root)
                if parent is not None:
                    vert_loc -= vert_gap

                children = list(G.neighbors(root))

                if len(children) == 0:
                    pos[root] = (xcenter, vert_loc)
                else:
                    dx = width / len(children) if len(children) > 0 else width
                    nextx = xcenter - width / 2 - dx / 2
                    for child in children:
                        nextx += dx
                        pos = _hierarchy_pos_recursive(
                            G,
                            child,
                            width=dx,
                            vert_gap=vert_gap,
                            vert_loc=vert_loc,
                            xcenter=nextx,
                            pos=pos,
                            parent=root,
                            parsed=parsed,
                        )
                    pos[root] = (xcenter, vert_loc)
            return pos

        try:
            return _hierarchy_pos_recursive(
                G, root, width, vert_gap, vert_loc, xcenter, pos
            )
        except Exception as e:
            logger.error(f"Error in hierarchical positioning: {e}", exc_info=True)
            return {}

    def _create_plotly_figure(
        self,
        tree: Dict[str, Any],
        graph,
        pos: Dict[str, Tuple[float, float]],
        optimal_path: Optional[List] = None,
    ):
        """Create Plotly figure with nodes and edges"""

        try:
            # Prepare data for visualization
            node_trace, edge_traces = self._prepare_traces(
                tree, graph, pos, optimal_path
            )

            # Combine all traces (edge traces + node trace)
            all_traces = []
            if isinstance(edge_traces, list):
                all_traces.extend(edge_traces)
            else:
                all_traces.append(edge_traces)
            all_traces.append(node_trace)

            # Create figure with proper layout
            fig = go.Figure(
                data=all_traces,
                layout=go.Layout(
                    title=dict(
                        text="🌳 tree Visualization",
                        x=0.5,
                        font=dict(size=20, color="#2c3e50"),
                    ),
                    showlegend=False,
                    hovermode="closest",
                    margin=dict(b=40, l=20, r=20, t=60),
                    annotations=[
                        dict(
                            text="💡 Hover over nodes to see arguments • Zoom and pan to explore",
                            showarrow=False,
                            xref="paper",
                            yref="paper",
                            x=0.5,
                            y=-0.05,
                            xanchor="center",
                            yanchor="top",
                            font=dict(color="#7f8c8d", size=12),
                        )
                    ],
                    xaxis=dict(
                        showgrid=False,
                        zeroline=False,
                        showticklabels=False,
                        showspikes=False,
                    ),
                    yaxis=dict(
                        showgrid=False,
                        zeroline=False,
                        showticklabels=False,
                        showspikes=False,
                    ),
                    plot_bgcolor="white",
                    paper_bgcolor="#f8f9fa",
                    dragmode="pan",
                ),
            )

            return fig

        except Exception as e:
            logger.error(f"Error creating Plotly figure: {e}", exc_info=True)
            # Return a minimal figure as fallback
            return go.Figure(
                layout=go.Layout(
                    title="Error rendering tree",
                    xaxis=dict(visible=False),
                    yaxis=dict(visible=False),
                )
            )

    def _prepare_traces(
        self,
        tree: Dict[str, Any],
        graph,
        pos: Dict[str, Tuple[float, float]],
        optimal_path: Optional[List] = None,
    ):
        """Prepare node and edge traces for Plotly"""

        try:
            optimal_ids = set()
            if optimal_path:
                for node in optimal_path:
                    if isinstance(node, dict) and "id" in node:
                        optimal_ids.add(str(node["id"]))
                    elif isinstance(node, (str, int)):
                        optimal_ids.add(str(node))

            # Prepare edge traces
            edge_traces = []

            # Regular edges
            edge_x, edge_y = [], []
            optimal_edge_x, optimal_edge_y = [], []

            for edge in graph.edges():
                if edge[0] in pos and edge[1] in pos:
                    x0, y0 = pos[edge[0]]
                    x1, y1 = pos[edge[1]]

                    # Check if edge is part of optimal path
                    if edge[1] in optimal_ids:
                        optimal_edge_x.extend([x0, x1, None])
                        optimal_edge_y.extend([y0, y1, None])
                    else:
                        edge_x.extend([x0, x1, None])
                        edge_y.extend([y0, y1, None])

            # Add regular edges trace
            if edge_x:  # Only add if there are edges
                edge_trace = go.Scatter(
                    x=edge_x,
                    y=edge_y,
                    line=dict(width=2, color="#bdc3c7"),
                    hoverinfo="none",
                    mode="lines",
                    name="edges",
                )
                edge_traces.append(edge_trace)

            # Add optimal path edges trace
            if optimal_edge_x:
                optimal_edge_trace = go.Scatter(
                    x=optimal_edge_x,
                    y=optimal_edge_y,
                    line=dict(width=4, color="#9b59b6"),
                    hoverinfo="none",
                    mode="lines",
                    name="optimal_path",
                )
                edge_traces.append(optimal_edge_trace)

            # Prepare node traces
            node_x, node_y = [], []
            node_colors, node_sizes = [], []
            node_text, hover_text = [], []

            for node_id, node_data in tree.items():
                if str(node_id) in pos:
                    x, y = pos[str(node_id)]
                    node_x.append(x)
                    node_y.append(y)

                    # Node properties with safe defaults
                    evaluation = float(node_data.get("evaluation", 0))
                    argument = str(node_data.get("argument", ""))
                    arg_type = str(node_data.get("argument_type", "root"))

                    # Color and size based on properties
                    if arg_type == "root":
                        color = "#3498db"  # Blue for root
                        size = 30
                    else:
                        color = self._score_to_gradient_color(evaluation)
                        size = 20

                    node_colors.append(color)
                    node_sizes.append(size)

                    # Labels and hover text - enhanced score display
                    if arg_type == "root":
                        node_text.append(f"[{node_id}]<br>ROOT")
                    else:
                        # Show score with color-coded indicator
                        score_indicator = (
                            "🟢"
                            if evaluation >= 0.7
                            else "🟡" if evaluation >= 0.5 else "🔴"
                        )
                        node_text.append(
                            f"[{node_id}]<br>{score_indicator} {evaluation:.2f}"
                        )

                    # Enhanced hover text with more score details
                    display_arg = (
                        argument[:200] + "..." if len(argument) > 200 else argument
                    )

                    # Add visits and win rate if available
                    visits = node_data.get("visits", 0)
                    wins = node_data.get("wins", 0.0)
                    win_rate = (wins / visits) if visits > 0 else 0.0

                    hover_info = f"""<b>Node:</b> {node_id}<br><b>Type:</b> {arg_type}<br><b>Score:</b> {evaluation:.3f}<br><b>Visits:</b> {visits}<br><b>Win Rate:</b> {win_rate:.2f}<br><b>Argument:</b><br>{display_arg}"""
                    hover_text.append(hover_info)

            # Create node trace
            node_trace = go.Scatter(
                x=node_x,
                y=node_y,
                mode="markers+text",
                text=node_text,
                textposition="middle center",
                textfont=dict(size=10, color="white", family="Arial Black"),
                hovertemplate="%{hovertext}<extra></extra>",
                hovertext=hover_text,
                marker=dict(
                    size=node_sizes,
                    color=node_colors,
                    line=dict(width=2, color="white"),
                    opacity=0.9,
                ),
                name="nodes",
            )

            # Always return consistent structure: (node_trace, list_of_edge_traces)
            return node_trace, edge_traces

        except Exception as e:
            logger.error(f"Error preparing traces: {e}", exc_info=True)
            # Return minimal fallback traces
            empty_trace = go.Scatter(x=[], y=[], mode="markers", name="empty")
            return empty_trace, []

    def _save_and_open(self, filename: Optional[str] = None) -> Optional[str]:
        """Save figure and open in browser"""
        if not self.fig:
            logger.warning("No figure to save - figure is None")
            return None

        logger.debug(f"Attempting to save figure to {self.output_dir}")

        try:
            # Generate output path
            if filename:
                output_path = os.path.join(self.output_dir, filename)
                if not output_path.endswith(".html"):
                    output_path += ".html"
            else:
                # Create temporary file
                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".html", delete=False, dir=self.output_dir
                ) as f:
                    output_path = f.name

            # Track temp files for cleanup
            self.temp_files.append(output_path)

            # Save figure
            self.fig.write_html(
                output_path,
                config={
                    "displayModeBar": True,
                    "displaylogo": False,
                    "modeBarButtonsToRemove": ["pan2d", "lasso2d", "select2d"],
                    "toImageButtonOptions": {
                        "format": "png",
                        "filename": "tree",
                        "height": 800,
                        "width": 1200,
                        "scale": 2,
                    },
                    "responsive": True,
                },
                include_plotlyjs="cdn",  # Use CDN to reduce file size
            )

            # Open in browser if enabled
            if self.auto_open:
                try:
                    webbrowser.open(f"file://{os.path.abspath(output_path)}")
                    logger.info(f"Plotly visualization saved and opened: {output_path}")
                except Exception as e:
                    logger.warning(f"Could not open browser: {e}")
                    logger.info(f"Plotly visualization saved to: {output_path}")
            else:
                logger.info(f"Plotly visualization saved to: {output_path}")

            return output_path

        except Exception as e:
            logger.error(f"Failed to save Plotly figure: {e}", exc_info=True)
            return None

    def _score_to_gradient_color(self, score: float) -> str:
        """Convert score to gradient color from red (0.5) to green (1.0)."""
        # Clamp score to valid range
        score = max(0.0, min(1.0, score))

        # If score is below 0.5, use red
        if score < 0.5:
            return "#f44336"  # Red

        # Calculate gradient position (0.0 to 1.0) for scores 0.5 to 1.0
        gradient_pos = (score - 0.5) / 0.5

        # Interpolate between red and green
        # Red: RGB(244, 67, 54) -> Green: RGB(76, 175, 80)
        r = int(244 - (244 - 76) * gradient_pos)
        g = int(67 + (175 - 67) * gradient_pos)
        b = int(54 + (80 - 54) * gradient_pos)

        return f"#{r:02x}{g:02x}{b:02x}"

    def cleanup(self):
        """Clean up temporary files"""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    logger.debug(f"Cleaned up temp file: {temp_file}")
            except Exception as e:
                logger.warning(f"Could not remove temp file {temp_file}: {e}")
        self.temp_files.clear()

    async def start(self, quit_event):
        """Start the renderer"""
        # Ensure logger is available in this async context
        thread_logger = ensure_logger_in_thread()
        thread_logger.info("Plotly renderer started")

        try:
            # Initial render if data is available
            if hasattr(self.tree_subject, "tree"):
                tree = getattr(self.tree_subject, "tree", {})
                optimal_path = getattr(self.tree_subject, "optimal_path", [])

                if tree:
                    self.render_tree(tree, optimal_path)

            # Keep running and listening for updates
            while not quit_event.is_set():
                await asyncio.sleep(1)

        except Exception as e:
            thread_logger.error(f"Error in Plotly renderer: {e}", exc_info=True)
        finally:
            # Cleanup on exit
            self.cleanup()
            thread_logger.info("Plotly renderer stopped")
