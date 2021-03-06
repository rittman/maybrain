"""
Utility functions for writing maybrain entities to files
"""
def output_adj_matrix(brain, filename):
    """
    Outputs the adjacency matrix to a file

    Parameters
    ----------
    brain: maybrain.brain.Brain
        An instance of the `Brain` class
    filename: str
        The filename to which the adjacency matrix will be written
    """

    try:
        with open(filename, "w") as file:
            for line in brain.adjMat:
                for num in line[:-1]:
                    file.write(str(num) + '\t')
                file.write(str(line[-1]) + '\n')
    except IOError as error:
        error.strerror = 'Problem with opening file "' + filename + '": ' + error.strerror
        raise error


def output_edges(brain, filename, properties=None):
    """
    Outputs the edges of a brain to file

    Parameters
    ----------
    brain: maybrain.brain.Brain
        An instance of the `Brain` class
    filename: str
        The filename to which the edges will be written
    properties: list
        The list of properties you want to save from each edge
    """
    if properties is None:
        properties = []
    try:
        with open(filename, "w") as file:
            # write column headers
            line = 'n1' + '\t' + 'n2'
            for prop in properties:
                line = line + '\t' + prop
            line = line + '\n'
            file.write(line)

            for e in brain.G.edges(data=True):
                # add coordinates
                line = str(e[0]) + '\t' + str(e[1])
                # add other properties
                for prop in properties:
                    try:
                        line = line + '\t' + str(e[2][prop])
                    except BaseException:
                        continue  # Property doesn't exist, just continue
                line = line + '\n'
                # write out
                file.write(line)
    except IOError as error:
        error.strerror = 'Problem with opening file "' + filename + '": ' + error.strerror
        raise error
