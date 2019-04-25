from idris_python.read_ir import *


def load_cam(path, session):
    with open(path, 'r') as f:
        js = json.load(f)


    letrec: LetRec = aeson_to_ir(js)
    return run_code(letrec, session)
