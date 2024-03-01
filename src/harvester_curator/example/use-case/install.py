import os
import sys
import subprocess

top = "Dumux_coltman2022a"
os.makedirs(top, exist_ok=True)

def runFromSubFolder(cmd, subFolder):
    folder = os.path.join(top, subFolder)
    try:
        subprocess.run(cmd, cwd=folder, check=True)
    except Exception as e:
        cmdString = ' '.join(cmd)
        sys.exit("Error when calling:\n{}\n-> folder: {}\n-> error: {}"
                 .format(cmdString, folder, str(e)))

def installModule(subFolder, url, branch):
    targetFolder = url.split("/")[-1].replace(".git", "")
    print(targetFolder)
    if not os.path.exists(targetFolder):
        runFromSubFolder(['git', 'clone', url, targetFolder], '.')
        runFromSubFolder(['git', 'checkout', branch], subFolder)
    else:
        print(f"Skip cloning {url} since target '{targetFolder}' already exists.")

print("Installing dune-localfunctions")
installModule("dune-localfunctions", "https://gitlab.dune-project.org/core/dune-localfunctions.git", "releases/2.9")

print("Installing dune-alugrid")
installModule("dune-alugrid", "https://gitlab.dune-project.org/extensions/dune-alugrid.git", "releases/2.9")

print("Installing dune-subgrid")
installModule("dune-subgrid", "https://gitlab.dune-project.org/extensions/dune-subgrid.git", "master")

print("Installing dune-spgrid")
installModule("dune-spgrid", "https://gitlab.dune-project.org/extensions/dune-spgrid.git", "releases/2.9")

print("Installing dune-istl")
installModule("dune-istl", "https://gitlab.dune-project.org/core/dune-istl.git", "releases/2.9")

print("Installing dune-geometry")
installModule("dune-geometry", "https://gitlab.dune-project.org/core/dune-geometry.git", "releases/2.9")

print("Installing dumux")
installModule("dumux", "https://git.iws.uni-stuttgart.de/dumux-repositories/dumux.git", "master")

print("Installing dune-grid")
installModule("dune-grid", "https://gitlab.dune-project.org/core/dune-grid.git", "releases/2.9")

print("Installing dune-common")
installModule("dune-common", "https://gitlab.dune-project.org/core/dune-common.git", "releases/2.9")

print("Installing coltman2022a")
installModule("coltman2022a", "https://git.iws.uni-stuttgart.de/dumux-pub/coltman2022a.git", "main")

print("Configuring project")
runFromSubFolder( ['./dune-common/bin/dunecontrol', '--opts=dumux/cmake.opts', 'all'], '.' )