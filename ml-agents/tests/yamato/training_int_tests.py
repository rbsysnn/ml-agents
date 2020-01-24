import os
import sys
import subprocess

from .yamato_utils import (
    get_base_path,
    run_standalone_build,
    init_venv,
    override_config_file,
)


def main():
    nn_file_expected = "./models/ppo/3DBall.nn"
    if os.path.exists(nn_file_expected):
        # Should never happen - make sure nothing leftover from an old test.
        print("Artifacts from previous build found!")
        sys.exit(1)

    base_path = get_base_path()
    print(f"Running in base path {base_path}")

    build_returncode = run_standalone_build(base_path)
    if build_returncode != 0:
        print("Standalone build FAILED!")
        sys.exit(build_returncode)

    init_venv()

    # Copy the default training config but override the max_steps parameter
    override_config_file("config/trainer_config.yaml", "override.yaml", max_steps=100)

    # TODO pass scene name and exe destination to build
    # TODO make sure we fail if the exe isn't found - see MLA-559
    mla_learn_cmd = "mlagents-learn override.yaml --train --env=UnitySDK/testPlayer --no-graphics --env-args -logFile -"  # noqa
    res = subprocess.run(f"source venv/bin/activate; {mla_learn_cmd}", shell=True)

    if res.returncode == 0 and os.path.exists(nn_file_expected):
        print("mlagents-learn run SUCCEEDED!")
    else:
        print("mlagents-learn run FAILED!")

    sys.exit(res.returncode)


if __name__ == "__main__":
    main()