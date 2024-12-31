import re

from django.core.mail.backends.locmem import EmailBackend


class CustomLocMemEmailBackend(EmailBackend):
    def send_messages(self, email_messages):
        # Убираем несериализуемые объекты
        for message in email_messages:
            if hasattr(message, "request"):
                delattr(message, "request")
        return super().send_messages(email_messages)


def parse_uid_and_token(text: str) -> dict[str, str]:
    pattern = (
        r"https?://testserver/[^/]+/(?P<uid>[A-Z]+)/(?P<token>[A-Za-z0-9-]+)/"
    )
    result = re.search(pattern, text)
    if result:
        return result.groupdict()
    return None
