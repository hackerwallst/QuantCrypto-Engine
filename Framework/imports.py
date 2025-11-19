# framework/imports.py
# ----------------------------------------------------
# Módulo central de imports utilizados pelo framework.
# Evita repetição de imports em cada arquivo.

import os
import re
import math
import uuid
import warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")

pd.set_option("display.max_colwidth", 120)
