# import pathlib
# from os import walk

from pycg.pycg import CallGraphGenerator
from pycg.utils.constants import CALL_GRAPH_OP

# entry_points = []
# for (dirpath, dirnames, filenames) in walk(f"./src/{package}"):
#     entry_points.extend((pathlib.PurePath(dirpath) / filename).as_posix() for filename in filenames)

cg = CallGraphGenerator(entry_points=["graphinate/builders/d3.py"],
                        package="graphinate",
                        max_iter=-1,
                        operation=CALL_GRAPH_OP)

cg.analyze()

o = cg.output()
