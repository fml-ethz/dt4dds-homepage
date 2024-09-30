import sys
import logging
import pathlib
import zipfile
import yaml

# local imports
import scenarios

# working dir from arguments
working_dir = pathlib.Path(sys.argv[1])

# set up logging
logging.basicConfig(
    level=logging.INFO, 
    format='[%(levelname)s][%(asctime)s][%(name)s][%(funcName)s]: %(message)s',
    handlers=[logging.FileHandler(working_dir / "runner.log", mode='a'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.info(f"Started on working dir {working_dir}")


# 
# main try block
# 
try:
    # load settings
    settings = yaml.safe_load(open(working_dir / "settings.txt"))
    logger.info(f"Loaded settings from working dir {working_dir}")

    # challenge submission
    if settings['submission_type'] == 'challenge':
        scenarios.challenge.run(working_dir, settings)

    # advanced submission
    elif settings['submission_type'] == 'advanced':
        scenarios.advanced.run(working_dir, settings)

    # scenario submission 
    elif settings['submission_type'] == 'basic':
        if settings['scenario'] == 'Density Benchmark Scenario':
            scenarios.density_benchmark.run(working_dir)
        elif settings['scenario'] == 'Worst Case Scenario':
            scenarios.worst_case.run(working_dir)
        elif settings['scenario'] == 'Long-Term Storage Scenario':
            scenarios.long_term_storage.run(working_dir)
        elif settings['scenario'] == 'High-Density Storage Scenario':
            scenarios.high_density_storage.run(working_dir)
        else:
            logger.error(f"Unknown basic scenario specified: {settings['scenario']}")
            raise NotImplementedError(f"Unknown basic scenario specified: {settings['scenario']}")

    # raise error if unknown
    else:
        logger.error(f"Unknown submission type specified: {settings['submission_type']}")
        raise NotImplementedError(f"Unknown submission type specified: {settings['submission_type']}")


    # compress output
    with zipfile.ZipFile(working_dir / "output.zip", 'w') as f:        
        for filename in ['R1.fq.gz', 'R2.fq.gz', 'settings.txt', 'design_sequences.txt']:
            filepath = working_dir / filename
            if filepath.is_file():
                f.write(filepath, compress_type=zipfile.ZIP_DEFLATED, arcname=filepath.name)

    # delete temporary files
    for filename in ['R1.fq.gz', 'R2.fq.gz']:
        filepath = working_dir / filename
        if filepath.is_file():
            filepath.unlink()


# if there was any error, exit with error code
except Exception as e:
    logger.exception(f"Processing failed: {e}")
    sys.exit(1)
except BaseException as e:
    logger.exception(f"Processing failed on system level")
    sys.exit(1)

# if there was no error up to now, exit without error code
logger.info(f"Finished without errors")
sys.exit(0)