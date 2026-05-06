from django.contrib import admin

from .models import Profile, JobOffer, Proposal, Message


admin.site.register(Profile)
admin.site.register(JobOffer)
admin.site.register(Proposal)
admin.site.register(Message)
