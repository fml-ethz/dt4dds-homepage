import subprocess
import pathlib

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def run(working_dir, settings):

    # load settings
    input_file = working_dir / "design_sequences.txt"
    output_file_1 = working_dir / "R1.fq"
    output_file_2 = working_dir / "R2.fq"
    challenge = "photolithography"

    if settings['challenge'] == 'Photolithographic DNA synthesis':
        challenge = "photolithography"
        logger.info("Running challenge on photolithographic DNA synthesis")

    elif settings['challenge'] == 'DNA decay after long-term storage':
        challenge = "decay"
        logger.info("Running challenge on DNA decay after long-term storage")

    else:
        raise NotImplementedError(f"Unknown challenge type: {settings['challenge']}")
    
    # run the challenge
    p = subprocess.run([
            f'{pathlib.Path(__file__).parent.resolve()}/challenge.sh',
            str(challenge),
            str(input_file),
            str(output_file_1),
            str(output_file_2),
        ],
        capture_output=True,
    )
    logger.info("Finished challenge")

    # save the output fom the process
    with open(working_dir / "output.txt", "wb") as f:
        f.write(p.stdout)
        f.write(p.stderr)

    # raise error if the process failed
    if p.returncode != 0:
        raise subprocess.CalledProcessError(p.returncode, p.args)
