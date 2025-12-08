#  [MermaidChart: 31f25fab-3a92-4cc4-bb11-71e8012c8ece]
#  [MermaidChart: 31f25fab-3a92-4cc4-bb11-71e8012c8ece]
#  [MermaidChart: 31f25fab-3a92-4cc4-bb11-71e8012c8ece]
# tests/test_modeling.py

from collections import defaultdict

from src.graphinate.modeling import GraphModel


def test_add_graph_models_names():
    model_a = GraphModel(name="ModelA")
    model_b = GraphModel(name="ModelB")
    combined_model = model_a + model_b

    assert combined_model.name == "ModelA + ModelB"


def test_add_graph_models_node_models():
    model_a = GraphModel(name="ModelA")
    model_b = GraphModel(name="ModelB")

    model_a._node_models = defaultdict(list, {"type1": ["node1"]})
    model_b._node_models = defaultdict(list, {"type1": ["node2"]})

    combined_model = model_a + model_b

    assert combined_model._node_models["type1"] == ["node1", "node2"]


def test_add_graph_models_edge_generators():
    model_a = GraphModel(name="ModelA")
    model_b = GraphModel(name="ModelB")

    model_a._edge_generators = defaultdict(list, {"edge1": ["gen1"]})
    model_b._edge_generators = defaultdict(list, {"edge1": ["gen2"]})

    combined_model = model_a + model_b

    assert combined_model._edge_generators["edge1"] == ["gen1", "gen2"]


def test_add_graph_models_node_children():
    model_a = GraphModel(name="ModelA")
    model_b = GraphModel(name="ModelB")

    model_a._node_children = defaultdict(list, {"child1": ["child_a"]})
    model_b._node_children = defaultdict(list, {"child1": ["child_b"]})

    combined_model = model_a + model_b

    assert combined_model._node_children["child1"] == ["child_a", "child_b"]
