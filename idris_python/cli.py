import sys

from idris_python.loader import load_cam, LinkSession
from subprocess import Popen, PIPE
from pathlib import Path
from wisepy2 import wise
import toml
import tempfile


@wise
def idris_python(main_file_or_project_entry: str,
                 packages: str = "cam",
                 idris: "idris executable path" = "idris",
                 o: "output .cam file" = "<nocam>"):
    """
    You can specify multiple packages by
        idris-python --packages "cam base effect"
    """
    packages = (e.strip() for e in packages.split(' '))
    out_cam = o != "<nocam>"
    if not out_cam:
        o = tempfile.mkstemp(suffix='.cam')[1]
    p = Path(main_file_or_project_entry)
    if p.suffix == '.idr':
        ins = [str(p.absolute())]
    else:
        p = p.absolute()
        with p.open('r') as f:
            config = toml.load(f)

        config = config['idris-cam']
        assert config.get('backend',
                          "python") == "python", "The backend is specified"
        modules = config['modules']

        p: Path = p.parent
        ins = []

        for m in modules:
            ins.append(str(p.joinpath('src', *m.split('.'))))

    proc = Popen([
        idris,
        '--codegen',
        'cam',
        *ins,
        '-o',
        o,
        '-p',
        *packages,
    ],
                 stdout=PIPE,
                 stderr=PIPE)

    stdout, stderr = proc.communicate(timeout=30)
    stdout = stdout.decode()
    if stdout:
        print(stdout)
    if proc.returncode is not 0:
        print(stderr.decode())
        return 1
    if not out_cam:
        common_abstract_machine_python_loader([o])
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
