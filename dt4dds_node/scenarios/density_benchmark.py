import gc
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

from .dt4dds import dt4dds

def run(working_dir):

    # set up config
    dt4dds.config.enable_multiprocessing = False
    dt4dds.config.n_processes = 1


    primers_0 = ["ACACGACGCTCTTCCGATCT", "AGACGTGTGCTCTTCCGATCT"]
    primers_2 = ["AATGATACGGCGACCACCGAGATCTACACTCTTTCCCTACACGACGCTCTTCCGATCT", "CAAGCAGAAGACGGCATACGAGATCGTGATGTGACTGGAGTTCAGACGTGTGCTCTTCCGATCT"]

    # assign efficiency properties
    dt4dds.properties.set_property_settings(
        dt4dds.settings.defaults.SequenceProperties(
            efficiency_distribution='normal',
            efficiency_params={'loc': 1.0, 'scale': 0.0051+0.5*(0.012-0.0051)},
        )
    )



    # 
    # synthesis
    # 
    seq_list = dt4dds.tools.txt_to_seqlist(working_dir / "design_sequences.txt")
    n_seqs = len(seq_list)
    logger.info(f"Total number of sequences: {n_seqs}")

    synthesis_settings = dt4dds.settings.defaults.ArraySynthesis_Twist(
        oligo_distribution_type='lognormal',
        oligo_distribution_params={'mean': 0, 'sigma': 0.30 - 0.5*(0.30-0.27)},
    )
    array_synthesis = dt4dds.processes.ArraySynthesis(synthesis_settings)
    array_synthesis.process(seq_list)
    pool = array_synthesis.sample_by_counts(200*n_seqs)
    pool = dt4dds.generators.attach_primers_to_pool(pool, *primers_0)
    pool.volume = 1

    # free up space
    del seq_list, array_synthesis
    gc.collect()
    logger.info("Finished synthesis")



    # 
    # PCR
    # 
    pcr_settings = dt4dds.settings.defaults.PCR_HiFi()
    pcr = dt4dds.processes.PCR(pcr_settings(
        primers=primers_2,
        template_volume=1,
        volume=20,
        efficiency_mean=0.95,
        n_cycles=30,
    ))
    pool = pcr.process(pool)

    # free up space
    del pcr
    gc.collect()
    logger.info("Finished PCR")


    # 
    # sequencing
    # 
    sbs_sequencing = dt4dds.processes.SBSSequencing(
        dt4dds.settings.defaults.iSeq100(
            output_directory=working_dir,
            n_reads=int(6.2*n_seqs),
            read_length=150,
            read_mode='paired-end',
        )
    )
    sbs_sequencing.process(pool)
    logger.info("Finished sequencing")