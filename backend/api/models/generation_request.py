from django.db import models


class GenerationRequest(models.Model):
    """
    Represents a user's music generation request.

    Stores input parameters, request status, and associated user.
    Acts as a log for tracking usage and analyzing behavior.
    Allows failed requests to be edited and retried without creating a new record.
    """
    