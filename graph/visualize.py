from pyvis.network import Network
import networkx as nx


def create_graph():

    # Create graph
    G = nx.Graph()

    # Add nodes
    G.add_node("OpenAI")
    G.add_node("Microsoft")
    G.add_node("Google")
    G.add_node("DeepMind")
    G.add_node("Geoffrey Hinton")

    # Add relationships
    G.add_edge("Microsoft", "OpenAI")
    G.add_edge("Google", "DeepMind")
    G.add_edge("Geoffrey Hinton", "Google")

    G.add_node("OpenAI", color="green")
    G.add_node("Microsoft", color="blue")
    G.add_node("Google", color="red") 

    G.add_edge(
    "Microsoft",
    "OpenAI",
    title="INVESTED_IN"
)
    # Create pyvis network
    net = Network(
        height="500px",
        width="100%",
        bgcolor="#111111",
        font_color="white"
    )

    # Physics for better movement
    net.barnes_hut()

    # Convert networkx graph
    net.from_nx(G)

    # Save graph
    net.save_graph("graph.html")

    net.add_node(
    "OpenAI",
    title="AI Research Company"
)

