import os

import flowstate

test_folder = os.path.join(
    os.path.dirname(f"{os.sep}".join(__file__.split(os.sep)[:-1])),
    ".artifacts",
    "assets",
)


def test_graph():
    """
    Use our example data to see that the dot output produced matches what we
    expect.
    """
    examples = set(
        [
            os.path.join(test_folder, os.path.splitext(os.path.basename(f))[0])
            for f in os.listdir(test_folder)
            if f.startswith("test_")
        ]
    )

    # The examples won't be byte-for-byte identical with what we produce unless
    # we sort the lines
    for e in examples:
        with open(e + ".dot") as f:
            expect = "".join(sorted([l.strip() for l in f.readlines()]))
        with open(e + ".json") as f:
            g = flowstate.Graph(f)
            got = "".join(sorted(g.render("dot").splitlines()))
            assert got.strip() == expect.strip()
