from circusd.extension import CircusReloaderExtension

DJANGO_SERVERS = [
    ("django-test.di.unistra.fr",),
    ("django-test2.di.unistra.fr",),
    ("django-pprd-w1.u-strasbg.fr", "django-pprd-w2.u-strasbg.fr"),
    ("django-pprd-w3.di.unistra.fr", "django-pprd-w4.di.unistra.fr"),
    ("django-w3.u-strasbg.fr", "django-w4.u-strasbg.fr"),
    ("django-w7.di.unistra.fr", "django-w8.di.unistra.fr"),
]

if __name__ == "__main__":
    CircusReloaderExtension(django_servers=DJANGO_SERVERS).run()
