import pytest

import graphinate
import graphinate.typing
from graphinate.modeling import GraphModel, elements


def test_graph_model(map_graph_model):
    # Arrange
    expected_country_count, expected_city_count, graph_model = map_graph_model
    country_type_id = (graphinate.typing.UniverseNode, 'country')
    city_type_id = ('country', 'city')

    # Act
    actual_model_count = len(graph_model._node_models)
    actual_country_count = len(list(graph_model._node_models[country_type_id][0].generator()))
    actual_city_count = len(list(graph_model._node_models[city_type_id][0].generator()))

    # Assert
    assert actual_model_count == 3
    assert actual_country_count == expected_country_count  # len(country_ids)
    assert actual_city_count == expected_city_count  # len(city_ids)


def test_graph_model__add__():
    # Arrange
    first_model = graphinate.model(name='First Model')
    second_model = graphinate.model(name='Second Model')

    # Act
    actual_model = first_model + second_model

    # Assert
    assert actual_model.name == 'First Model + Second Model'


def test_graph_model_validate_node_parameters():
    # Arrange
    graph_model = graphinate.model(name='Graph with invalid node supplier')

    # Act & Assert
    with pytest.raises(graphinate.modeling.GraphModelError):
        @graph_model.node()
        def invalid_node_supplier(wrong_parameter=None):
            yield 1


def test_validate_type_identifier_and_callable():
    # Arrange
    class CallableStr(str):
        def __call__(self):
            return "called"

    node_type = CallableStr("valididentifier")

    # Act & Assert
    # Should not raise
    GraphModel._validate_type(node_type)


def test_validate_type_non_callable_valid_identifier():
    # Arrange
    node_type = "valid_identifier"

    # Act & Assert
    # Should not raise
    GraphModel._validate_type(node_type)


def test_validate_type_non_string_callable():
    # Arrange
    class DummyCallable:
        def __call__(self):
            return "called"

    node_type = DummyCallable()

    # Act & Assert
    # Should not raise
    GraphModel._validate_type(node_type)


def test_validate_type_neither_callable_nor_identifier():
    # Arrange
    node_type = "123 invalid!"

    # Act & Assert
    with pytest.raises(ValueError, match="Invalid Type:"):
        GraphModel._validate_type(node_type)


def test_validate_type_empty_string():
    # Arrange
    node_type = ""

    # Act & Assert
    with pytest.raises(ValueError, match="Invalid Type:"):
        GraphModel._validate_type(node_type)


def test_validate_type_special_characters():
    # Arrange
    node_type = "invalid-type!"

    # Act & Assert
    with pytest.raises(ValueError, match="Invalid Type:"):
        GraphModel._validate_type(node_type)


def test_validate_type_accepts_valid_identifier():
    # Arrange
    node_type = "node_type"

    # Act & Assert
    # Should not raise
    GraphModel._validate_type(node_type)


def test_validate_type_accepts_callable():
    # Arrange
    def some_callable():
        pass

    # Act & Assert
    # Should not raise
    GraphModel._validate_type(some_callable)


def test_validate_type_accepts_identifier_and_callable():
    # Arrange
    class CallableStr(str):
        def __call__(self):
            return "called"

    node_type = CallableStr("anotheridentifier")

    # Act & Assert
    # Should not raise
    GraphModel._validate_type(node_type)


def test_validate_type_raises_on_invalid_identifier():
    # Arrange
    node_type = "not valid!"

    # Act & Assert
    with pytest.raises(ValueError, match="Invalid Type:"):
        GraphModel._validate_type(node_type)


def test_validate_type_raises_on_empty_string():
    # Arrange
    node_type = ""

    # Act & Assert
    with pytest.raises(ValueError, match="Invalid Type:"):
        GraphModel._validate_type(node_type)


def test_validate_type_callable_string():
    # Arrange
    # In Python, a string is never callable, but for the sake of the test, let's simulate
    # a string subclass that is callable
    class CallableStr(str):
        def __call__(self):
            return "called"

    node_type = CallableStr("not_an_identifier_but_callable")

    # Act & Assert
    # Should not raise
    GraphModel._validate_type(node_type)


def test_elements_yields_correct_count():
    # Arrange
    data = [
        {"id": 1, "name": "A"},
        {"id": 2, "name": "B"},
        {"id": 3, "name": "C"},
    ]

    # Act
    result = list(elements(data, element_type="Node", id="id", name="name"))

    # Assert
    assert len(result) == len(data)
    for i, el in enumerate(result):
        assert el.id == data[i]["id"]
        assert el.name == data[i]["name"]


def test_elements_multiple_getters():
    # Arrange
    data = [
        {"id": 1, "name": "A", "value": 10},
        {"id": 2, "name": "B", "value": 20},
    ]

    # Act
    result = list(elements(data, element_type="Node", id="id", name="name", value="value"))

    # Assert
    assert len(result) == 2
    for i, el in enumerate(result):
        assert el.id == data[i]["id"]
        assert el.name == data[i]["name"]
        assert el.value == data[i]["value"]


def test_elements_empty_iterable():
    # Arrange
    data = []

    # Act
    result = list(elements(data, element_type="Node", id="id"))

    # Assert
    assert result == []


def test_elements_element_type_not_callable_invalid():
    # Arrange
    data = [{"id": 1}]

    # Act & Assert
    # element_type is not callable and not a valid identifier
    with pytest.raises(ValueError, match="Invalid Type:"):
        list(elements(data, element_type="123 invalid!", id="id"))


def test_elements_callable_element_type():
    # Arrange
    data = [
        {"type": "Alpha", "id": 1},
        {"type": "Beta", "id": 2},
    ]

    def type_extractor(item):
        return item["type"]

    # Act
    result = list(elements(data, element_type=type_extractor, id="id"))

    # Assert
    assert result[0].__class__.__name__ == "Alpha"
    assert result[1].__class__.__name__ == "Beta"
    assert result[0].id == 1
    assert result[1].id == 2


def test_elements_invalid_identifier_type():
    # Arrange
    data = [{"id": 1}]

    def bad_type(item):
        return "not valid!"

    # Act & Assert
    with pytest.raises(ValueError, match="Invalid Type:"):
        list(elements(data, element_type=bad_type, id="id"))
