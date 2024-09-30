from django import forms

from .models import BasicSubmission, AdvancedSubmission, ChallengeSubmission
from .validators import validate_sequences



class SubmissionForm(forms.ModelForm):

    sequences_raw = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': '5',
        }),
        validators=[validate_sequences],
    )

    class Meta:
        abstract = True




class BasicSubmissionForm(SubmissionForm):
    
    class Meta:
        model = BasicSubmission
        fields = [
            'name', 
            'scenario',
        ]


class AdvancedSubmissionForm(SubmissionForm):

    class Meta:
        model = AdvancedSubmission
        fields = [
            'name', 
            'synthesis_type', 
            'synthesis_homogeneity', 
            'synthesis_coverage',
            'pcr_polymerase',
            'pcr_efficiency',
            'pcr_homogeneity',
            'pcr_cycles',
            'storage_enabled',
            'storage_coverage',
            'storage_halflives',
            'sequencing_paired',
            'sequencing_depth',
            'sequencing_length',
        ]


class ChallengeSubmissionForm(SubmissionForm):
    
    class Meta:
        model = ChallengeSubmission
        fields = [
            'name', 
            'challenge',
        ]