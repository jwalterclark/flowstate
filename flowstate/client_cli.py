#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from contextlib import redirect_stdout

import flowstate


def main():
    g = flowstate.Graph(sys.stdin)

    with redirect_stdout(sys.stdout):
        print(g.render("dot"))


if __name__ == "__main__":
    main()
