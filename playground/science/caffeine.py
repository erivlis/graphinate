import graphinate


def caffeine_graph_model():
    """
    Create a graph model for the caffeine molecule (C8H10N4O2).

    Returns:
        GraphModel: A graph model representing the caffeine molecule.
    """
    graph_model = graphinate.model(name="Caffeine Molecule")

    # Define atoms
    atoms = [
        ('C1', 'C'), ('C2', 'C'), ('C3', 'C'), ('C4', 'C'), ('C5', 'C'), ('C6', 'C'),
        ('C7', 'C'), ('C8', 'C'), ('H1', 'H'), ('H2', 'H'), ('H3', 'H'), ('H4', 'H'),
        ('H5', 'H'), ('H6', 'H'), ('H7', 'H'), ('H8', 'H'), ('H9', 'H'), ('H10', 'H'),
        ('N1', 'N'), ('N2', 'N'), ('N3', 'N'), ('N4', 'N'), ('O1', 'O'), ('O2', 'O')
    ]

    # Define bonds
    bonds = [
        ('C1', 'C2'), ('C1', 'N1'), ('C1', 'H1'), ('C2', 'C3'), ('C2', 'N2'), ('C3', 'C4'),
        ('C6', 'C7'), ('C7', 'C8'), ('C7', 'H4'), ('C8', 'O1'), ('C8', 'O2'), ('N1', 'H5'),
        ('N2', 'H6'), ('N3', 'H7'), ('N4', 'H8'), ('O1', 'H9'), ('O2', 'H10')
    ]

    # Add nodes (atoms)
    @graph_model.node(lambda x: x[1], key=lambda x: x[0], label=lambda x: x[1])
    def atom():
        yield from atoms

    @graph_model.edge()
    def bond():
        for bond in bonds:
            yield {'source': bond[0], 'target': bond[1]}

    return graph_model


if __name__ == '__main__':
    model = caffeine_graph_model()
    schema = graphinate.builders.GraphQLBuilder(model).build()
    graphinate.graphql.server(schema)
