import logging
import json

from django.shortcuts import render, HttpResponse, get_object_or_404, redirect, reverse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.http import Http404
from django.utils import timezone
from django.core.files.base import File
from django.utils.text import slugify

from .models import Job, BasicSubmission, AdvancedSubmission, ChallengeSubmission
from .forms import BasicSubmissionForm, AdvancedSubmissionForm, ChallengeSubmissionForm

logger = logging.getLogger("dt4dds_web.jobs.views")
logger.setLevel(logging.DEBUG)



def get_job_submission_or_message(request, uid, quiet=False):

    available = True

    try:
        job = Job.objects.get(pk=uid)

        if job.basicsubmission_set.count():
            submission = job.basicsubmission_set.get()
        elif job.advancedsubmission_set.count():
            submission = job.advancedsubmission_set.get()
        elif job.challengesubmission_set.count():
            submission = job.challengesubmission_set.get()
        else:
            available = False

        if job.is_deleted:
            available = False

    except ObjectDoesNotExist:
        available = False

    if available:
        return job, submission
    else:
        if not quiet:
            messages.add_message(request, messages.ERROR, f"A submission with ID {uid} does not exist or was deleted.")
            raise Http404("Submission not found")
        return None, None





def overview(request):

    context = {
        'title': 'Overview',
        'meta_title': 'Overview'
    }
 
    return render(request, 'jobs/overview.html', context=context)



def submission_basic(request):

    # form submitted
    if request.method == 'POST':

        form = BasicSubmissionForm(request.POST)

        # form is valid
        if form.is_valid():

            # save the submission
            submission = form.save(commit=False)
            
            # create a job for it and assign it
            job = Job()
            submission.job = job

            # save the design sequences and set status
            job.create_folder()
            job.save_design_sequences(form.cleaned_data['sequences_raw'].splitlines())
            submission.save_settings_file(job.settings_file)
            job.state = job.StateTypes.WAITING

            # save the submission and job
            job.save()
            submission.save()


            context = {
                'title': 'Scenario submission',
                'meta_title': 'Submission',
                'form': form,
            }
            return redirect(reverse('jobs:detail', kwargs={'uid': job.uid}))

        # form is invalid
        else:
            messages.add_message(request, messages.ERROR, form.errors)
            context = {
                'title': 'Scenario submission',
                'meta_title': 'Submission',
                'form': form,
            }
            return render(request, 'jobs/submission_basic.html', context=context)

    # get form
    else:

        context = {
            'title': 'Scenario submission',
            'meta_title': 'Submission',
            'form': BasicSubmissionForm(),
        }
        return render(request, 'jobs/submission_basic.html', context=context)



def submission_advanced(request):

    # form submitted
    if request.method == 'POST':

        form = AdvancedSubmissionForm(request.POST)

        # form is valid
        if form.is_valid():

            # save the submission
            submission = form.save(commit=False)
            
            # create a job for it and assign it
            job = Job()
            submission.job = job

            # save the design sequences and set status
            job.create_folder()
            job.save_design_sequences(form.cleaned_data['sequences_raw'].splitlines())
            submission.save_settings_file(job.settings_file)
            job.state = job.StateTypes.WAITING

            # save the submission and job
            job.save()
            submission.save()

            context = {
                'title': 'Advanced submission',
                'meta_title': 'Submission',
                'form': form,
            }
            return redirect(reverse('jobs:detail', kwargs={'uid': job.uid}))

        # form is invalid
        else:
            messages.add_message(request, messages.ERROR, form.errors)
            context = {
                'title': 'Advanced submission',
                'meta_title': 'Submission',
                'form': form,
            }
            return render(request, 'jobs/submission_advanced.html', context=context)

    # get form
    else:

        context = {
            'title': 'Advanced submission',
            'meta_title': 'Submission',
            'form': AdvancedSubmissionForm(),
        }
        return render(request, 'jobs/submission_advanced.html', context=context)



def submission_challenge(request):

    # form submitted
    if request.method == 'POST':

        form = ChallengeSubmissionForm(request.POST)

        # form is valid
        if form.is_valid():

            # save the submission
            submission = form.save(commit=False)
            
            # create a job for it and assign it
            job = Job()
            submission.job = job

            # save the design sequences and set status
            job.create_folder()
            job.save_design_sequences(form.cleaned_data['sequences_raw'].splitlines())
            submission.save_settings_file(job.settings_file)
            job.state = job.StateTypes.WAITING

            # save the submission and job
            job.save()
            submission.save()

            context = {
                'title': 'Challenge submission',
                'meta_title': 'Submission',
                'form': form,
            }
            return redirect(reverse('jobs:detail', kwargs={'uid': job.uid}))

        # form is invalid
        else:
            messages.add_message(request, messages.ERROR, form.errors)
            context = {
                'title': 'Challenge submission',
                'meta_title': 'Submission',
                'form': form,
            }
            return render(request, 'jobs/submission_challenge.html', context=context)

    # get form
    else:

        context = {
            'title': 'Challenge submission',
            'meta_title': 'Submission',
            'form': ChallengeSubmissionForm(),
        }
        return render(request, 'jobs/submission_challenge.html', context=context)


def detail(request, uid):

    job, submission = get_job_submission_or_message(request, uid)

    all_pending = Job.objects.all().filter(state=Job.StateTypes.WAITING).exclude(is_deleted=True)
    queue_length = f"#{all_pending.filter(submission_date__lt=job.submission_date).count()+1}"

    running_time = "NA"
    if job.state == job.StateTypes.RUNNING and job.run_start_date:
        duration = timezone.now() - job.run_start_date
        running_time = f'{int(duration.total_seconds()//60):1d}:{int(duration.total_seconds() % 60):02d}'

    context = {
        'title': 'Submission details',
        'meta_title': 'Details',
        'id': uid,
        'job': job,
        'submission': submission,
        'queue_length': queue_length,
        'running_time': running_time,
    }

    return render(request, 'jobs/detail.html', context=context)



def status(request, uid):

    job, _ = get_job_submission_or_message(request, uid, quiet=True)

    if job:
        all_pending = Job.objects.all().filter(state=Job.StateTypes.WAITING).exclude(is_deleted=True)
        queue_length = f"#{all_pending.filter(submission_date__lt=job.submission_date).count()+1}"

        running_time = "NA"
        if job.state == job.StateTypes.RUNNING and job.run_start_date:
            duration = timezone.now() - job.run_start_date
            running_time = f'{int(duration.total_seconds()//60):1d}:{int(duration.total_seconds() % 60):02d}'

        response = {'state': job.state}

        if job.state == job.StateTypes.RUNNING and job.run_start_date:
            response['time'] = running_time
        
        if job.state == job.StateTypes.WAITING:
            response['queue'] = queue_length

    else:
        response = {}

    return HttpResponse(json.dumps(response))



def results(request, uid):

    job, submission = get_job_submission_or_message(request, uid)

    if not job.state == job.StateTypes.FINISHED:
        messages.add_message(request, messages.INFO, f"Output is only available for finished jobs.")
        return redirect(reverse('jobs:detail', kwargs={'uid': job.uid}))

    if not job.output_file.is_file():
        messages.add_message(request, messages.ERROR, f"The was an error locating the output file. Please inform administrators.")
        return redirect(reverse('jobs:detail', kwargs={'uid': job.uid}))

    if not job.first_download_date:
        job.first_download_date = timezone.now()
        job.save()

    with open(job.output_file, 'rb') as file_handle:

        download_file = File(file_handle)

        response = HttpResponse(download_file, 'application/zip')
        response['Content-Length'] = download_file.size    
        response['Content-Disposition'] = f'attachment; filename="output_{slugify(submission.name)}.zip"'
        return response




def delete(request, uid):

    job, submission = get_job_submission_or_message(request, uid)

    # delete job files, mark job as deleted
    job.delete_output()
    job.is_deleted = True
    job.save()

    messages.add_message(request, messages.INFO, f"The submission with ID {uid} and all associated data were successfully deleted.")
    return redirect(reverse('basic:home'))