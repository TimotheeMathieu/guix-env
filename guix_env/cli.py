import click
import os
from pathlib import Path
import subprocess
import tempfile
import shutil
from jinja2 import Environment, FileSystemLoader

# TODO: add test that the environment exists before doing anything.

main_dir=os.path.join(os.getenv("HOME"), ".guix_env")
file_path = os.path.realpath(__file__)

environment = Environment(loader=FileSystemLoader(
    os.path.join(os.path.dirname(file_path),"template_scripts/")))

default_guix_packages = [
    "python",
    "python-toolchain",
    "poetry-next", # this comes from perso channel while waiting for guix to have a newer version of poetry
    "bash",
    "glibc-locales",
    "nss-certs",
    "coreutils",
    "diffutils",
    "curl",
    "git",
    "make",
    "zlib",
    "which",
    "tcl",
    "gtk",
    "grep",
    "xcb-util", # xcb/dbus is for matplotlib to be able to plt.show
    "xcb-util-wm",
    "xcb-util-image",
    "xcb-util-keysyms",
    "xcb-util-renderutil",
    "dbus",
    "xcb-util-cursor",
    "ncurses",
    "nano",
    "tmux",
    "zsh"
]

@click.group()
@click.pass_context
def guix_env(ctx):
    """
    Construct guix environment for python development
    """
    pass

@guix_env.command()
@click.argument('name',required = True, type=str)
@click.option('--channel-file',required = False, type=str, help="Path to a channel file to be used in the guix install")
@click.option('--requirements-file',required = False, type=str, help="Path to a requirements.txt file to be used in the python install")
@click.option('--pyproject-file',required = False, type=str, help="Path to a pyproject.toml file to be used in the python install (override requirement file if both are given).")
@click.option('--poetry-lock-file',required = False, type=str, help="Path to a poetry.lock file to be used in the python install")
@click.option('--manifest-file',required = False, type=str, help="Path to a manifest file to be used in the guix install. Will replace the default manifest.")
@click.option('--guix-args',required = False, type=str, default="-CFNW", help="arguments to be passed to guix")
@click.pass_context
def create(ctx, name, channel_file, requirements_file, pyproject_file, poetry_lock_file, manifest_file, guix_args):
    """
    Create an environment with name `name`. A channel file can be specified, otherwise a channel file will be
    automatically created.
    """
    assert not os.path.isdir(os.path.join(main_dir, name)), "Environment already exist"
    os.system('mkdir -p '+os.path.join(main_dir, name, "bin"))
    os.system('mkdir -p '+os.path.join(main_dir, name, ".local"))

    zshrc = environment.get_template("zshrc").render(name = name, reqfile = os.path.join(main_dir, name, "requirements.txt"))

    # TBC
    
    channels = _make_channel_file(channel_file)
    home = os.getenv("HOME")
    run_script = environment.get_template("run_script.sh").render(name=name, guix_args = guix_args, HOME=home)
        
    with open(os.path.join(main_dir, name, "bin", ".zshrc"), "w") as myfile:
        myfile.write(zshrc)
    with open(os.path.join(main_dir, name, "bin", "run_script.sh"), "w") as myfile:
        myfile.write(run_script)
        os.system('chmod +x '+os.path.join(main_dir, name, "bin", "run_script.sh"))
        
    if channel_file is None:
        with open(os.path.join(main_dir, name, "channels.scm"), "w") as myfile:
            myfile.write(channels)
    else:
        os.system("cp "+channel_file+" "+os.path.join(main_dir, name, "channels.scm"))

    if manifest_file is None:
        with open(os.path.join(main_dir, name, "manifest.scm"), "w") as myfile:
            packages = default_guix_packages
            myfile.write(
                    "(specifications->manifest '(\n\"" + '"\n "'.join(packages) + '"\n))'
                )
    else:
        os.system("cp "+manifest_file+" "+os.path.join(main_dir, name, "manifest.scm"))

    guix_python_cmd = f"guix time-machine --channels=$HOME/.guix_env/{name}/channels.scm -- shell python -- python3 --version | cut -d ' ' -f 2"

    python_version = subprocess.check_output(guix_python_cmd, shell=True).decode().strip()
        
    if pyproject_file is None:
        author = subprocess.run(["whoami"], capture_output=True).stdout.decode()
        pyproject = environment.get_template("pyproject.toml").render(name = name, python_version = python_version)
    else:
        with open(pyproject_file, "r") as myfile:
            pyproject = myfile.read()

    with open(os.path.join(main_dir, name,  "pyproject.toml"), "w") as myfile:
        myfile.write(pyproject)

    if poetry_lock_file is not None:
        os.system(f"cp {poetry_lock_file} {os.path.join(main_dir, name)}")

    with open(os.path.join(main_dir, name, "bin", "launch_in_guix.sh"), "w") as myfile:
        launcher = environment.get_template("launch_in_guix.sh").render(name=name, guix_args = guix_args,)
        myfile.write(launcher)

    os.system("chmod +x "+os.path.join(main_dir, name, "bin", "launch_in_guix.sh"))

    # TODO: use one template file for the environment and add the rest with ninja
    with open(os.path.join(main_dir, name, "bin",  "launch_shell.sh"), "w") as myfile:
        launcher = environment.get_template("launch_shell.sh").render(name=name)
        myfile.write(launcher)
    os.system("chmod +x "+os.path.join(main_dir, name, "bin",  "launch_shell.sh"))

    if requirements_file is None:
        reqfile = ""
    else:
        os.system("cp "+os.path.realpath(requirements_file)+ " /tmp/requirements_for_guix_env.txt")
        reqfile = "/tmp/requirements_for_guix_env.txt"
    create_env_file = environment.get_template("create_env.sh").render(name=name,
                                                                       directory = os.path.join(main_dir, name),
                                                                       requirements = reqfile)
    with open(os.path.join("/tmp",  "create_guix_env.sh"), "w") as myfile:
        myfile.write(create_env_file)
    os.system("chmod +x "+os.path.join("/tmp",  "create_guix_env.sh"))

    run_script = environment.get_template("run_script.sh").render(name=name)
    with open(os.path.join(main_dir, name, "bin",  "run_script.sh"), "w") as myfile:
        myfile.write(create_env_file)
    os.system("chmod +x "+os.path.join(main_dir, name, "bin", "run_script.sh"))
    
    os.system(os.path.join(main_dir, name, "bin", "launch_in_guix.sh")+ " " + os.path.join("/tmp",  "create_guix_env.sh"))

@guix_env.command()
@click.argument('name',required = True, type=str)
@click.pass_context
def update(ctx, name):
    """
    Update the channel file (and as a consequence, it will update the packages managed by guix at next shell/run).
    """
    channels = _make_channel_file(os.path.join(main_dir, name, "channels.scm"))
    with open(os.path.join(main_dir, name, "channels.scm"), "w") as myfile:
        myfile.write(channels)
    # TODO: add poetry update and a capacity to roll-back



@guix_env.command()
@click.argument('name',required = True, type=str)
@click.pass_context
def rm(ctx, name):
    """
    Remove a guix-env environment.
    """
    if os.path.isdir(os.path.join(main_dir, name)):
        shutil.rmtree(os.path.join(main_dir, name))


@guix_env.command()
@click.argument('name',required = True, type=str)
@click.argument('pkg',required = True, type=str)
@click.pass_context
def add_guix(ctx, name, pkg):
    """
    Add the guix package `pkg` to the environment named `name`.
    Warning: if you add a package from inside an environment, the package will not be available until you reconstruct the environment.
    """
    with open(os.path.join(main_dir, name, "manifest.scm"), "r") as myfile:
        packages = myfile.read().split("(")[2].split(")")[0]
        packages = packages.split("\n")
        packages = [ a.replace('"', "").strip()  for a in packages]
        packages = [pkg for pkg in packages if len(pkg)>0]
    assert _is_in_guix(pkg), "package not found in guix."
    packages.append(pkg)
    with open(os.path.join(main_dir, name, "manifest.scm"), "w") as myfile:
        myfile.write(
                "(specifications->manifest '(\n\"" + '"\n "'.join(packages) + '"\n))'
            )

@guix_env.command()
@click.argument('name',required = True, type=str)
@click.argument('pkg',required = True, type=str)
@click.pass_context
def add_python(ctx, name, pkg):
    """
    Add the python package `pkg` to the environment named `name`.
    """
    env_file = os.path.join(main_dir, name, "bin", "use_env.sh")
    os.system(f"{env_file} poetry add {pkg} --directory={os.path.join(main_dir, name)}")

@guix_env.command()
@click.pass_context
def list(ctx):
    """
    list all the environments.
    """
    os.system('ls '+main_dir)

@guix_env.command()
@click.argument('name',required = True, type=str)
@click.pass_context
def info(ctx, name):
    """
    Get informations on environment with name `name`.
    """
    click.echo("Environment located in "+os.path.join(main_dir, name))
    env_file = os.path.join(main_dir, name, "bin", "use_env.sh")
    os.system(env_file+" guix describe")

    with open(os.path.join(main_dir, name, "manifest.scm"), "r") as myfile:
        packages = myfile.read().split("(")[2].split(")")[0]
        packages = packages.split("\n")
        packages = [ a.replace('"', "").strip()  for a in packages]
        packages = [pkg for pkg in packages if len(pkg)>0]
    click.echo("-"*10)
    click.echo("Installed packages")
    click.echo("\n".join(packages))
    click.echo("-"*10)
    click.echo("Installed python packages")
    os.system(f"{env_file} poetry run pip3 freeze --directory={os.path.join(main_dir, name)}")

@guix_env.command()
@click.argument('name',required = True, type=str)
@click.option("--tmux", is_flag=True, required=False, help="Launch in a tmux console, if it does not exists create it.")
@click.option("--cwd", is_flag=True, required=False, help="Used only in conjunction with tmux, change current directory in the tmux environment.")
@click.pass_context
def shell(ctx, name, tmux, cwd):
    """
    Open a shell in the environment with name `name`.
    """
    # env_file = os.path.join(main_dir, name, "bin", "use_env.sh")

    if tmux:
        child = subprocess.run(["tmux","has-session", "-t",  "guix_env_"+name],capture_output=True,text=True)
        rc = child.returncode
        if rc != 0:
            print("env not launched yet, launching now")
            os.system("tmux new-session -d -s guix_env_"+name+" "+activation_file)

        if cwd:
            wd = os.getcwd()
            os.system("tmux send-keys -t guix_env_"+name+" \" cd "+wd+ " && clear\" ENTER")
            print("done cwd")
        os.system("tmux attach -t guix_env_"+name)
    else:
        os.system(os.path.join(main_dir, name, "bin", "launch_in_guix.sh") + " " + os.path.join(main_dir, name, "bin", "launch_shell.sh"))

@guix_env.command()
@click.argument('name',required = True, type=str)
@click.argument('cmd',required = True, type=str)
@click.pass_context
def run(ctx, name, cmd):
    """
    Run the command `cmd` in the  environment with name `name`.

    Example of usage is
    guix-env run my_env "ls $HOME/"
    """

    os.system(os.path.join(main_dir, name, "bin", "launch_in_guix.sh")+ " " + os.path.join(main_dir, name, "bin", "run_script.sh") + " "  + cmd)

  
def _is_in_guix(pkg):
    output = subprocess.run(["guix", "search", pkg], capture_output=True).stdout.decode()
    output = output.split("name: ")
    names = [o.split("\n")[0] for o in output]
    res = False
    for name in names:
        if pkg == name.strip():
            res = True
    return res

def _make_channel_file(channel_file=None):

    if channel_file is None:
        system_channels = subprocess.run(["guix", "describe", "-f", "channels"], capture_output=True).stdout.decode()
    else:
        system_channels = subprocess.run(["cat", channel_file], capture_output=True).stdout.decode()
    
    channels = environment.get_template("channels.scm").render(system_channels = system_channels)
    return channels
