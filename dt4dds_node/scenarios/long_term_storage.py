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

    synthesis_settings = dt4dds.settings.defaults.ArraySynthesis_CustomArray(
        oligo_distribution_type='lognormal',
        oligo_distribution_params={'mean': 0, 'sigma': 1.30 - 1.0*(1.30-0.58)},
    )
    array_synthesis = dt4dds.processes.ArraySynthesis(synthesis_settings)
    array_synthesis.process(seq_list)
    pool = array_synthesis.sample_by_counts(100*n_seqs)
    pool = dt4dds.generators.attach_primers_to_pool(pool, *primers_0)
    pool.volume = 1

    # free up space
    del seq_list, array_synthesis
    gc.collect()
    logger.info("Finished synthesis")



    # 
    # PCR
    # 
    pcr_settings = dt4dds.settings.defaults.PCR_Taq()
    pcr = dt4dds.processes.PCR(pcr_settings(
        primers=primers_0,
        template_volume=1,
        volume=20,
        efficiency_mean=0.95,
        n_cycles=20,
    ))
    pool = pcr.process(pool)

    # free up space
    del pcr
    gc.collect()
    logger.info("Finished PCR")



    # 
    # aging
    # 
    # sample exact coverage
    pool = pool.sample_by_counts(100*n_seqs)
    pool.volume = 1

    aging = dt4dds.processes.Aging(
        dt4dds.settings.defaults.Aging(
            n_halflives=5,
            substitution_rate=0.0,
        )
    )
    pool = aging.process(pool)
    pool.volume = 1

    # free up space
    del aging
    gc.collect()
    logger.info("Finished aging")


    # 
    # PCR
    # 
    pcr_settings = dt4dds.settings.defaults.PCR_Taq()
    pcr = dt4dds.processes.PCR(pcr_settings(
        primers=primers_2,
        template_volume=1,
        volume=20,
        efficiency_mean=0.95,
        n_cycles=10,
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
            n_reads=50*n_seqs,
            read_length=150,
            read_mode='paired-end',
        )
    )
    sbs_sequencing.process(pool)
    logger.info("Finished sequencing")