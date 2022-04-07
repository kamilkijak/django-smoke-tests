class DisableMigrations(object):

    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None
