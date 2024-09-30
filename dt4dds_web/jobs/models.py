from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.files.storage import default_storage
from django.conf import settings

import logging
logger = logging.getLogger("dt4dds_web.jobs.models")

import uuid
import pathlib
import shutil
import yaml


class Job(models.Model):

    STORAGE_DIR = pathlib.Path(pathlib.Path(settings.BASE_DIR) / '../files/jobs').resolve()


    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    submission_date = models.DateTimeField('Submission date', auto_now_add=True)
    run_start_date = models.DateTimeField('Run start date', default=None, blank=True, null=True)
    run_end_date = models.DateTimeField('Run end date', default=None, blank=True, null=True)
    first_download_date = models.DateTimeField('First download date', default=None, blank=True, null=True)
    is_deleted = models.BooleanField('Is deleted?', default=False)

    class StateTypes(models.TextChoices):
        BLOCKED = 'BL', 'Blocked'
        WAITING = 'WA', 'Waiting'
        RUNNING = 'RU', 'Running'
        FINISHED = 'FI', 'Finished'
        FAILED = 'FA', 'Failed'

    state = models.CharField(
        "Job state",
        max_length=2,
        choices=StateTypes.choices,
        default=StateTypes.BLOCKED,
    )

    @property
    def folder(self):
        return pathlib.Path(self.STORAGE_DIR / str(self.uid))

    @property
    def settings_file(self):
        return self.folder / "settings.txt"

    @property
    def sequences_file(self):
        return self.folder / "design_sequences.txt"
    
    @property
    def output_file(self):
        return self.folder / "output.zip"


    def create_folder(self):
        self.folder.mkdir(parents=True, exist_ok=True)


    def save_design_sequences(self, sequence_list):
        with self.sequences_file.open("w", encoding ="utf-8") as f:
            f.writelines('\n'.join(map(str, sequence_list)))


    def delete_directory(self):
        try:
            shutil.rmtree(self.folder)
        except Exception as e:
            logger.exception(e)


    def delete_output(self):
        if self.output_file.is_file():
            self.output_file.unlink() 


    def delete(self):
        logger.info(f"Deleting job with UID {self.uid}")
        self.delete_directory()
        super().delete()




class AbstractSubmission(models.Model):

    name = models.CharField("Submission name", max_length=200, default="Unnamed submission")
    email = models.EmailField("Email address", max_length=200, default="", blank=True)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)

    class Meta:
        abstract = True


    def save_settings_file(self, filepath):
        with open(filepath, "w") as f:
            yaml.dump(self._get_settings_dict(), f, default_flow_style=False, sort_keys=False)



class BasicSubmission(AbstractSubmission):

    class ScenarioTypes(models.TextChoices):
        DENSITY_BENCHMARK = 'DB', 'Density Benchmark Scenario'
        HIGH_DENSITY_STORAGE = 'HD', 'High-Density Storage Scenario'
        WORST_CASE = 'WC', 'Worst Case Scenario'
        LONG_TERM_STORAGE = 'LS', 'Long-Term Storage Scenario'

    scenario = models.CharField(
        "Scenario type",
        max_length=2,
        choices=ScenarioTypes.choices,
        default=ScenarioTypes.DENSITY_BENCHMARK,
    )
    
    def _get_settings_dict(self):
        d = {
            'submission_type': 'basic',
            'scenario': self.ScenarioTypes(self.scenario).label,
        }
        return d




class AdvancedSubmission(AbstractSubmission):

    # 
    # SYNTHESIS
    # 

    class SynthesisTypes(models.TextChoices):
        ELECTROCHEMICAL = 'EC', 'Electrochemical synthesis (e.g. Genscript)'
        MATDEPOSITION = 'MD', 'Material deposition-based synthesis (e.g. Twist)'

    synthesis_type = models.CharField(
        "Synthesis type",
        max_length=2,
        choices=SynthesisTypes.choices,
        default=None,
    )

    synthesis_coverage = models.IntegerField(
        "Synthesis coverage",
        default=100,
        validators=[
            MaxValueValidator(500),
            MinValueValidator(1)
        ]
    )
    
    synthesis_homogeneity = models.FloatField(
        "Synthesis homogeneity",
        default=0.5,
        validators=[
            MaxValueValidator(1),
            MinValueValidator(0)
        ]
    )


    # 
    # PCR
    # 

    class PolymeraseTypes(models.TextChoices):
        TAQ = 'TAQ', 'Taq-based (fidelity ~ 1)'
        HIFI = 'HFi', 'Generic high fidelity (fidelity ~ 40)'
        Q5H = 'Q5H', 'Q5 HiFi (fidelity ~ 280)'
        EXO = 'EXO', 'exonuclease-deficient (fidelity ~ 0.3)'

    pcr_polymerase = models.CharField(
        "Polymerase type",
        max_length=3,
        choices=PolymeraseTypes.choices,
        default=None,
    )

    pcr_efficiency = models.IntegerField(
        "PCR efficiency", 
        default=90,
        validators=[
            MaxValueValidator(100),
            MinValueValidator(50)
        ]
    )

    pcr_homogeneity = models.FloatField(
        "PCR Efficiency homogeneity",
        default=0.5,
        validators=[
            MaxValueValidator(1),
            MinValueValidator(0)
        ]
    )

    pcr_cycles = models.IntegerField(
        "PCR cycles", 
        default=30,
        validators=[
            MaxValueValidator(150),
            MinValueValidator(0)
        ]
    )


    # 
    # STORAGE
    # 

    storage_enabled = models.BooleanField(
        "Storage enabled",
        default=True
    )

    storage_coverage = models.FloatField(
        "Storage coverage", 
        default=20,
        validators=[
            MaxValueValidator(200),
            MinValueValidator(1)
        ]
    )

    storage_halflives = models.FloatField(
        "Storage half-lives", 
        default=1,
        validators=[
            MaxValueValidator(10),
            MinValueValidator(0)
        ]
    )


    # 
    # SEQUENCING
    # 

    sequencing_paired = models.BooleanField(
        "Sequencing in paired-read mode enabled",
        default=True
    )

    sequencing_depth = models.IntegerField(
        "Sequencing depth", 
        default=20,
        validators=[
            MaxValueValidator(50),
            MinValueValidator(1)
        ]
    )

    sequencing_length = models.IntegerField(
        "Sequencing length", 
        default=150,
        validators=[
            MaxValueValidator(300),
            MinValueValidator(30)
        ]
    )


    def _get_settings_dict(self):
        d = {
            'submission_type': 'advanced',
            'synthesis': {
                'platform': self.SynthesisTypes(self.synthesis_type).label,
                'coverage': self.synthesis_coverage,
                'homogeneity': self.synthesis_homogeneity,
            },
            'pcr': {
                'polymerase': self.PolymeraseTypes(self.pcr_polymerase).label,
                'efficiency': self.pcr_efficiency,
                'homogeneity': self.pcr_homogeneity,
                'n_cycles': self.pcr_cycles,
            },
            'aging': {
                'enabled': self.storage_enabled,
                'coverage': self.storage_coverage,
                'half-lives': self.storage_halflives,
            },
            'sequencing': {
                'depth': self.sequencing_depth,
                'length': self.sequencing_length,
                'paired': self.sequencing_paired,
            },
        }
        return d



class ChallengeSubmission(AbstractSubmission):

    class ChallengeTypes(models.TextChoices):
        PHOTOLITHOGRAPHY = 'PS', 'Photolithographic DNA synthesis'
        DNA_DECAY = 'DD', 'DNA decay after long-term storage'

    challenge = models.CharField(
        "Challenge type",
        max_length=2,
        choices=ChallengeTypes.choices,
        default=ChallengeTypes.DNA_DECAY,
    )
    
    def _get_settings_dict(self):
        d = {
            'submission_type': 'challenge',
            'challenge': self.ChallengeTypes(self.challenge).label,
        }
        return d