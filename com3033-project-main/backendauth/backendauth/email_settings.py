import ssl
from django.core.mail.backends.smtp import EmailBackend

class CustomEmailBackend(EmailBackend):
    def _get_tls_context(self):
        # Create default context and disable strict verification
        context = ssl.create_default_context()
        context.verify_flags &= ~ssl.VERIFY_X509_STRICT
        return context