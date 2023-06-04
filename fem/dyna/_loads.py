
class DynaMeshLoadsMixin:
    def add_load(self, load_type, **load_kwargs):

        if load_type == 'arf':
            self.add_arf_load()
