from django.core.mail.backends.locmem import EmailBackend


class CustomLocMemEmailBackend(EmailBackend):
    def send_messages(self, email_messages):
        # Убираем несериализуемые объекты
        for message in email_messages:
            if hasattr(message, "request"):
                delattr(message, "request")
        return super().send_messages(email_messages)
