import click
import os
from pathlib import Path
import subprocess
import tempfile
import shutil
from jinja2 import Environment, FileSystemLoader
import questionary

# TODO: add test that the environment exists before doing anything.

main_dir=os.path.join(os.getenv("HOME"), ".guix_env")
file_path = os.path.realpath(__file__)

environment = Environment(loader=FileSystemLoader(
    os.path.join(os.path.dirname(file_path),"template_scripts/")))

guix_python_packages = [
    "python",
    "python-toolchain",
    "poetry", # this comes from perso channel while waiting for guix to have a newer version of poetry
    "xcb-util", # xcb is for matplotlib to be able to plt.show
    "xcb-util-wm",
    "xcb-util-image",
    "xcb-util-keysyms",
    "xcb-util-renderutil",
    "xcb-util-cursor",
    ]

default_guix_packages = [
    "bash",
    "glibc-locales",
    "nss-certs",
    "coreutils",
    "diffutils",
    "findutils",
    "curl",
    "git",
    "make",
    "mesa",
    "zlib",
    "which",
    "tcl",
    "gtk",
    "grep",
    "dbus",
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
@click.option('--without-python', is_flag=True, help="Do an environment without python")
@click.option('--pyproject-file',required = False, type=str, help="Path to a pyproject.toml file to be used in the python install (override requirement file if both are given).")
@click.option('--poetry-lock-file',required = False, type=str, help="Path to a poetry.lock file to be used in the python install")
@click.option('--manifest-file',required = False, type=str, help="Path to a manifest file to be used in the guix install. Will replace the default manifest.")
@click.option('--guix-args',required = False, type=str, default="-CFNW", help="arguments to be passed to guix")
@click.pass_context
def create(ctx, name, channel_file, without_python, requirements_file, pyproject_file, poetry_lock_file, manifest_file, guix_args):
    """
    Create an environment with name `name`. A channel file can be specified, otherwise a channel file will be
    automatically created.
    """
    with_python = not without_python
    assert not os.path.isdir(os.path.join(main_dir, name)), "Environment already exist"
    os.system('mkdir -p '+os.path.join(main_dir, name, "bin"))
    os.system('mkdir -p '+os.path.join(main_dir, name, ".local"))
    home = os.getenv("HOME")

    zshrc = environment.get_template("zshrc").render(name = name, reqfile = os.path.join(main_dir, name, "requirements.txt"), with_python=with_python)
    run_script = environment.get_template("run_script.sh").render(name=name, guix_args = guix_args, HOME=home, with_python=with_python)

    channels = _make_channel_file(channel_file)
        
    with open(os.path.join(main_dir, name, ".zshrc"), "w") as myfile:
        myfile.write(zshrc)
    with open(os.path.join(main_dir, name, "bin", "run_script.sh"), "w") as myfile:
        myfile.write(run_script)
        os.system('chmod +x '+os.path.join(main_dir, name, "bin", "run_script.sh"))
        
    # Guix manifest and channel files
    if channel_file is None:
        with open(os.path.join(main_dir, name, "channels.scm"), "w") as myfile:
            myfile.write(channels)
    else:
        os.system("cp "+channel_file+" "+os.path.join(main_dir, name, "channels.scm"))
        os.system

    if manifest_file is None:
        with open(os.path.join(main_dir, name, "manifest.scm"), "w") as myfile:
            packages = default_guix_packages
            if with_python:
                packages = packages + guix_python_packages
            myfile.write(
                    "(specifications->manifest '(\n\"" + '"\n "'.join(packages) + '"\n))'
                )
    else:
        os.system("cp "+manifest_file+" "+os.path.join(main_dir, name, "manifest.scm"))

    # 
    with open(os.path.join(main_dir, name, "bin", "launch_in_guix.sh"), "w") as myfile:
        launcher = environment.get_template("launch_in_guix.sh").render(name=name, guix_args = guix_args,)
        myfile.write(launcher)

    os.system("chmod +x "+os.path.join(main_dir, name, "bin", "launch_in_guix.sh"))

    with open(os.path.join(main_dir, name, "bin",  "launch_shell.sh"), "w") as myfile:
        launcher = environment.get_template("launch_shell.sh").render(name=name, with_python=with_python)
        myfile.write(launcher)
    os.system("chmod +x "+os.path.join(main_dir, name, "bin",  "launch_shell.sh"))

    # initialize a git repo for rollback capability
    
    guix_git_cmd = f"guix time-machine --channels=$HOME/.guix_env/{name}/channels.scm -- shell git  -- git init $HOME/.guix_env/{name}/"
    subprocess.run(guix_git_cmd, shell=True)
    with open(os.path.join(main_dir, name, "bin",  "add_commit.sh"), "w") as myfile:
            launcher = environment.get_template("add_commit.sh").render(name=name, with_python=with_python)
            myfile.write(launcher)
    os.system("chmod +x "+os.path.join(main_dir, name, "bin",  "add_commit.sh"))
    os.system(os.path.join(main_dir, name, "bin",  "add_commit.sh"))

    if with_python:
        ### construct a poetry environment optionally with the specified requirements
        _make_python_env(main_dir, name, pyproject_file, poetry_lock_file, requirements_file)
        
    print(f"Guix-env environment {name} has been created, its files can be found in {os.path.join(main_dir, name)}")
    

@guix_env.command()
@click.argument('name',required = True, type=str)
@click.pass_context
def update(ctx, name):
    """
    Update the channel file to the current guix channel file (and as a consequence, it will update the packages managed by guix at next shell/run).
    
    """
    print("Updating channel file")
    channels = _make_channel_file(os.path.join(main_dir, name, "channels.scm"))
    with open(os.path.join(main_dir, name, "channels.scm"), "w") as myfile:
        myfile.write(channels)
    if os.path.isfile(os.path.join(main_dir, name, "pyproject.toml")):
        print("Found python install, updating")
        _launch_cmd(name, "gep update")
        

@guix_env.command()
@click.argument('name',required = True, type=str)
@click.pass_context
def rm(ctx, name):
    """
    Remove a guix-env environment.
    """
    if os.path.isdir(os.path.join(main_dir, name)):
        print("Removing ", os.path.join(main_dir, name))
        shutil.rmtree(os.path.join(main_dir, name))
    else:
        print("Environment not found, not removing anything")

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
    print("Commiting changes...")
    os.system(os.path.join(main_dir, name, "bin",  "add_commit.sh"))

    print(f"Package {pkg} added to the manifest for environment {name}.") 

@guix_env.command()
@click.argument('name',required = True, type=str)
@click.argument('pkg',required = True, type=str)
@click.pass_context
def add_python(ctx, name, pkg):
    """
    Add the python package `pkg` to the environment named `name`.
    """
    _launch_cmd(name, f"gep add  {pkg}")
    print("Commiting changes...")
    os.system(os.path.join(main_dir, name, "bin",  "add_commit.sh"))


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
    Get informations on packages in the environment with name `name`.
    """
    click.echo("Environment located in "+os.path.join(main_dir, name))
    _launch_cmd(name," guix describe")

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
    _launch_cmd(name, "gep run pip3 freeze")



@guix_env.command()
@click.argument('name',required = True, type=str)
@click.pass_context
def rollback(ctx, name):
    """
    Rollback to previous commit `name`.
    """
    raise NotImplemented("Not implemented yet. For now, just roll back the git repo manually")
    
    # answer = questionary.form(
    #     which_date = questionary.select("Rollback to which commit",
    #                                     choices=["item1", "item2", "item3"])
    # ).ask()

    # print(answers)

    

@guix_env.command()
@click.argument('name',required = True, type=str)
@click.pass_context
def shell(ctx, name):
    """
    Open a shell in the environment with name `name`.
    """
    assert os.path.isdir(os.path.join(main_dir, name)), "Environment does not exist"

    print(f"Welcome to your guix-env environment: {name}. Launching environment...")
    # print("To install python package, use 'gep add package_name'. gep is an alias for poetry that install things at the right place.")
    
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

    _launch_cmd(name, cmd)


def _launch_cmd(name, cmd):
    os.system(os.path.join(main_dir, name, "bin", "launch_in_guix.sh")+ " " + os.path.join(main_dir, name, "bin", "run_script.sh") + " "  + cmd)


  
def _is_in_guix(pkg):
    print("Checking that the package is indeed a guix package")
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


def _make_python_env(main_dir, name, pyproject_file, poetry_lock_file, requirements_file):
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
        os.system(os.path.join(main_dir, name, "bin", "launch_in_guix.sh")+ " " + os.path.join("/tmp",  "create_guix_env.sh"))
