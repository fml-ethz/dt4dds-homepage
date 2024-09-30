import gc
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

from .dt4dds import dt4dds

def run(working_dir, settings):

    primers_0 = ["ACACGACGCTCTTCCGATCT", "AGACGTGTGCTCTTCCGATCT"]
    primers_2 = ["AATGATACGGCGACCACCGAGATCTACACTCTTTCCCTACACGACGCTCTTCCGATCT", "CAAGCAGAAGACGGCATACGAGATCGTGATGTGACTGGAGTTCAGACGTGTGCTCTTCCGATCT"]

    # assign efficiency properties
    dt4dds.properties.set_property_settings(
        dt4dds.settings.defaults.SequenceProperties(
            efficiency_distribution='normal',
            efficiency_params={'loc': 1.0, 'scale': 0.0051+float(settings['pcr']['homogeneity'])*(0.012-0.0051)},
        )
    )



    # 
    # synthesis
    # 
    seq_list = dt4dds.tools.txt_to_seqlist(working_dir / "design_sequences.txt")
    n_seqs = len(seq_list)
    logger.info(f"Total number of sequences: {n_seqs}")

    if settings['synthesis']['platform'] == "Electrochemical synthesis (e.g. Genscript)":
        synthesis_settings = dt4dds.settings.defaults.ArraySynthesis_CustomArray(
            oligo_distribution_type='lognormal',
            oligo_distribution_params={'mean': 0, 'sigma': 1.30 - float(settings['synthesis']['homogeneity'])*(1.30-0.58)},
        )
    elif settings['synthesis']['platform'] == "Material deposition-based synthesis (e.g. Twist)":
        synthesis_settings = dt4dds.settings.defaults.ArraySynthesis_Twist(
            oligo_distribution_type='lognormal',
            oligo_distribution_params={'mean': 0, 'sigma': 0.30 - float(settings['synthesis']['homogeneity'])*(0.30-0.27)},
        )
    else:
        raise NotImplementedError(f"Unknown synthesis platform: {settings['synthesis']['platform']}")

    array_synthesis = dt4dds.processes.ArraySynthesis(synthesis_settings)
    array_synthesis.process(seq_list)
    pool = array_synthesis.sample_by_counts(float(settings['synthesis']['coverage'])*n_seqs)
    pool = dt4dds.generators.attach_primers_to_pool(pool, *primers_0)
    pool.volume = 1

    # free up space
    del seq_list, array_synthesis
    gc.collect()
    logger.info("Finished synthesis")



    # 
    # PCR
    # 
    if settings['pcr']['polymerase'] == "Taq-based (fidelity ~ 1)":
        pcr_settings = dt4dds.settings.defaults.PCR_Taq()
    elif settings['pcr']['polymerase'] == "Generic high fidelity (fidelity ~ 40)":
        pcr_settings = dt4dds.settings.defaults.PCR_HiFi()
    elif settings['pcr']['polymerase'] == "Q5 HiFi (fidelity ~ 280)":
        pcr_settings = dt4dds.settings.defaults.PCR_Q5()
    elif settings['pcr']['polymerase'] == "exonuclease-deficient (fidelity ~ 0.3)":
        pcr_settings = dt4dds.settings.defaults.PCR_Exo()
    else:
        raise NotImplementedError(f"No polymerase of type {settings['pcr']['polymerase']} known.")

    n_cycles = int(settings['pcr']['n_cycles'])
    if n_cycles > 30:
        n_cycles = 30
        pcr_settings.polymerase_fidelity /= n_cycles/30
        logger.info(f"Adapted cycle count from {int(settings['pcr']['n_cycles'])} to {n_cycles}, fidelity {pcr_settings.polymerase_fidelity}")

    pcr = dt4dds.processes.PCR(pcr_settings(
        primers=primers_2,
        template_volume=1,
        volume=20,
        efficiency_mean=float(settings['pcr']['efficiency'])/100,
        n_cycles=n_cycles,
    ))
    pool = pcr.process(pool)

    # free up space
    del pcr
    gc.collect()
    logger.info("Finished PCR")



    # 
    # aging
    # 
    if settings['aging']['enabled']:
        # ensure sufficient counts for aging
        if pool.n_oligos < int(float(settings['aging']['coverage'])*n_seqs):
            factor = 1.1* (int(float(settings['aging']['coverage'])*n_seqs) / pool.n_oligos)
            logger.info(f"Increasing coverage for aging by factor {factor}")
            for seq, count in pool:
                pool.add_sequence(seq, int((factor-1)*count))

        # sample exact coverage
        pool = pool.sample_by_counts(int(float(settings['aging']['coverage'])*n_seqs))
        pool.volume = 1

        aging = dt4dds.processes.Aging(
            dt4dds.settings.defaults.Aging(
                n_halflives=float(settings['aging']['half-lives']),
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
    # sequencing
    # 
    # ensure sufficient counts for sequencing
    if pool.n_oligos < int(float(settings['sequencing']['depth'])*n_seqs):
        factor = 1.1* (int(float(settings['sequencing']['depth'])*n_seqs) / pool.n_oligos)
        logger.info(f"Increasing coverage for sequencing by factor {factor}")
        for seq, count in pool:
            pool.add_sequence(seq, int((factor-1)*count))

    sbs_sequencing = dt4dds.processes.SBSSequencing(
        dt4dds.settings.defaults.iSeq100(
            output_directory=working_dir,
            n_reads=int(float(settings['sequencing']['depth'])*n_seqs),
            read_length=int(settings['sequencing']['length']),
            read_mode='paired-end' if settings['sequencing']['paired'] else 'single-end',
        )
    )
    sbs_sequencing.process(pool)
    logger.info("Finished sequencing")