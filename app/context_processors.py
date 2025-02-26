from .models import Profile

def user_profile(request):
    if request.user.is_authenticated:
        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            profile = None
    else:
        profile = None

    return {'user_profile': profile}