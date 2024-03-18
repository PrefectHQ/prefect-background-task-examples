# FastAPI User Signups

This example API demonstrates accepting new user registrations and queues up a few
asynchronous tasks that should happen when each user joins:

* Send the user a confirmation email
* Add the new user to an onboarding email flow in the company's marketing software
* Populating the user's workspace with default objects

These are fire-and-forget tasks that need to happen, but the request cycle doesn't need
to wait on them to complete.
