"""PyPOWER Module testing"""

import os
import sys
import importlib
MODULEDIR = ".."
CASEDIR = "../pypower"
sys.path.extend([MODULEDIR,CASEDIR])
from pypower.api import runpf, runopf, ppoption
tested = 0
failed = 0
print(f"Testing all cases in {CASEDIR}...")
for case in os.listdir("../pypower"):
    if case.startswith("case") and case.endswith(".py"):
        name = os.path.splitext(case)[0]
        module = importlib.__import__(name)
        try:
            if hasattr(module,name):
                tested += 1
                print(f"Running {case} pf and opf",end="...",flush=True,file=sys.stdout)
                model = getattr(module,name)
                casedata = model()
                ppopt = ppoption(VERBOSE=0,OUT_ALL=0)
                assert runpf(casedata,ppopt)[1] == 1, "runpf failed"
                assert runopf(casedata,ppopt)["success"], "runopf failed"
                print("ok",file=sys.stdout)
        except Exception as err:
            print(f"ERROR [{name}]: {err}",file=sys.stderr)
            failed += 1
print(f"Testing completed: {tested=}, {failed=}")
exit(1 if failed > 0 else 0)