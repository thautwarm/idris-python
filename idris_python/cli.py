import sys

from idris_python.loader import load_cam, LinkSession
from subprocess import Popen, PIPE
from pathlib import Path
import toml
from wisepy2 import wise


@wise
def idris_python(main_file_or_project_entry: str, packages: str = "cam", idris: "idris executable path" = "idris",
                 o: "output .cam file" = ""):
    """
    You can specify multiple packages by
        idris-python --packages "cam base effect"
    """
    packages = (e.strip() for e in packages.split(' '))
    p = Path(main_file_or_project_entry)
    if p.suffix == '.idr':
        ins = [str(p.absolute())]
    else:
        p = p.absolute()
        with p.open('r') as f:
            config = toml.load(f)

        config = config['idris-cam']
        assert config.get('backend', "python") == "python", "The backend is specified"
        modules = config['modules']

        p: Path = p.parent
        ins = []

        for m in modules:
            ins.append(str(p.joinpath('src', *m.split('.'))))

    proc = Popen([idris, '--codegen', 'cam', *ins, *(('-o', o) if o else ()), '-p', *packages, ], stdout=PIPE,
                 stderr=PIPE)

    stdout, stderr = proc.communicate(timeout=30)
    print(stdout)
    if proc.returncode is not 0:
        print(stderr)
        return 1
    if not o:
        common_abstract_machine_python_loader(o)
    return 0


@wise
def common_abstract_machine_python_loader(filename):
    """
    The .cam file loader.
    """
    return load_cam(filename, LinkSession())


def idris_python_run():
    sys.exit(idris_python(sys.argv[1:]))


def cam_run():
    sys.exit(common_abstract_machine_python_loader(sys.argv[1:]))
