from django.contrib.auth.decorators import user_passes_test


def admin_required(view_func):
    return user_passes_test(
        lambda u: u.is_authenticated and u.groups.filter(name='Admin').exists()
    )(view_func)


def cashier_required(view_func):
    return user_passes_test(
        lambda u: u.is_authenticated and (
            u.groups.filter(name='Cashier').exists() or
            u.groups.filter(name='Admin').exists()
        )
    )(view_func)
